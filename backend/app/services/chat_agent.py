"""
Chat2App Agent Service.
MDP Platform V3.1

Core agent logic: NL -> SQL -> AMIS Schema.
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from app.core.ollama_client import ollama_client, OllamaServiceUnavailable
from app.engine.sql_runner import execute_safe_sql, SQLValidationError, SQLExecutionError
from app.models.chat import (
    ChatRequest, ChatResponse, ChatMessage, 
    AgentAction, AmisSchema, MessageRole
)


# System prompt for SQL generation
SQL_SYSTEM_PROMPT = """你是一个数据分析助手。根据用户的自然语言问题，生成 MySQL SELECT 查询。

数据库表结构：
- objects: id, object_type, display_name, created_at, updated_at
- object_properties: object_id, property_key, property_value
- links: id, source_id, target_id, link_type, created_at
- link_types: id, name, source_type, target_type

规则：
1. 只生成 SELECT 语句
2. 使用标准 MySQL 语法
3. 避免子查询，优先使用 JOIN
4. 返回 JSON 格式: {"sql": "SELECT ...", "explanation": "..."}

示例：
用户: "显示所有目标对象"
返回: {"sql": "SELECT * FROM objects WHERE object_type = 'Target'", "explanation": "查询类型为Target的所有对象"}
"""


def build_table_schema(columns: List[str], rows: List[Dict]) -> AmisSchema:
    """Build AMIS table schema from query results."""
    return AmisSchema(
        type="table",
        columns=[{"name": col, "label": col} for col in columns],
        data={"items": rows}
    )


def build_chart_schema(data: Dict[str, Any], chart_type: str = "bar") -> AmisSchema:
    """Build AMIS chart schema."""
    return AmisSchema(
        type="chart",
        config={
            "xAxis": {"type": "category"},
            "yAxis": {"type": "value"},
            "series": [{"type": chart_type}]
        },
        data=data
    )


def build_error_response(message: str, suggestions: List[str] = None) -> ChatResponse:
    """Build error response."""
    return ChatResponse(
        action=AgentAction.ERROR,
        message=message,
        suggestions=suggestions or ["请尝试更具体的问题", "查看有哪些数据表"]
    )


async def process_chat(request: ChatRequest) -> ChatResponse:
    """
    Main agent entry point.
    
    Flow:
    1. Build conversation context
    2. Call Ollama to generate SQL
    3. Execute SQL safely
    4. Convert results to AMIS schema
    """
    try:
        # Build messages for LLM
        messages = [
            {"role": "system", "content": SQL_SYSTEM_PROMPT}
        ]
        
        # Add history
        for msg in request.history[-5:]:  # Last 5 messages for context
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Call Ollama
        logger.info(f"Processing chat: {request.message[:100]}...")
        llm_response = await ollama_client.generate_response(messages)
        
        # Check for parse error
        if "parse_error" in llm_response:
            return build_error_response(
                f"LLM 返回格式错误: {llm_response.get('raw_content', '')[:200]}",
                ["请用更简单的方式描述您的需求"]
            )
        
        # Extract SQL
        sql = llm_response.get("sql")
        explanation = llm_response.get("explanation", "")
        
        if not sql:
            # LLM didn't generate SQL - might be a clarification
            return ChatResponse(
                action=AgentAction.TEXT,
                message=llm_response.get("raw_content", "我不确定如何处理这个请求"),
                suggestions=["查询所有对象", "显示数据统计"]
            )
        
        # Execute SQL
        try:
            result = await execute_safe_sql(sql)
        except SQLValidationError as e:
            return build_error_response(
                f"SQL 验证失败: {str(e)}",
                ["请修改您的问题，我只能执行查询操作"]
            )
        except SQLExecutionError as e:
            return build_error_response(
                f"查询执行失败: {str(e)}",
                ["请检查您的问题是否涉及存在的数据表"]
            )
        
        # Build response
        if result["row_count"] == 0:
            return ChatResponse(
                action=AgentAction.TEXT,
                message=f"{explanation}\n\n查询未返回结果。",
                sql=sql,
                suggestions=["尝试放宽查询条件", "查看有哪些数据"]
            )
        
        # Build table schema
        amis_schema = build_table_schema(result["columns"], result["rows"])
        
        return ChatResponse(
            action=AgentAction.TABLE,
            message=f"{explanation}\n\n找到 {result['row_count']} 条记录。",
            amis_schema=amis_schema,
            sql=sql,
            data={"columns": result["columns"], "rows": result["rows"]},
            suggestions=["按时间排序", "显示更多详情", "导出数据"]
        )
        
    except OllamaServiceUnavailable as e:
        return build_error_response(
            f"AI 服务不可用: {str(e)}",
            ["请确保 Ollama 服务正在运行", "执行: ollama serve"]
        )
    except Exception as e:
        logger.exception("Unexpected error in chat agent")
        return build_error_response(
            f"处理请求时发生错误: {str(e)}"
        )
