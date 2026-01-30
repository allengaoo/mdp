"""
Tests for Chat2App data models.
Chat2App Module - MDP Platform V3.1
"""
import pytest
from pydantic import ValidationError
from app.models.chat import (
    ChatRequest, ChatResponse, ChatMessage,
    AgentAction, AmisSchema, MessageRole, HealthResponse
)


class TestChatMessage:
    """Test cases for ChatMessage model."""

    def test_valid_user_message(self):
        """应该创建有效的用户消息"""
        msg = ChatMessage(role=MessageRole.USER, content="显示所有对象")
        assert msg.role == MessageRole.USER
        assert msg.content == "显示所有对象"

    def test_valid_assistant_message(self):
        """应该创建有效的助手消息"""
        msg = ChatMessage(role=MessageRole.ASSISTANT, content="查询完成")
        assert msg.role == MessageRole.ASSISTANT

    def test_valid_system_message(self):
        """应该创建有效的系统消息"""
        msg = ChatMessage(role=MessageRole.SYSTEM, content="System prompt")
        assert msg.role == MessageRole.SYSTEM


class TestChatRequest:
    """Test cases for ChatRequest model."""

    def test_valid_request_minimal(self):
        """应该创建最小有效请求"""
        req = ChatRequest(message="显示所有目标")
        assert req.message == "显示所有目标"
        assert req.context is None
        assert req.history == []

    def test_valid_request_with_context(self):
        """应该创建带上下文的请求"""
        req = ChatRequest(
            message="查询详情",
            context={"object_id": "tgt-001", "view": "360"}
        )
        assert req.context["object_id"] == "tgt-001"

    def test_valid_request_with_history(self):
        """应该创建带历史记录的请求"""
        history = [
            ChatMessage(role=MessageRole.USER, content="查询1"),
            ChatMessage(role=MessageRole.ASSISTANT, content="结果1"),
        ]
        req = ChatRequest(message="查询2", history=history)
        assert len(req.history) == 2

    def test_reject_empty_message(self):
        """应该拒绝空消息"""
        with pytest.raises(ValidationError):
            ChatRequest(message="")


class TestAmisSchema:
    """Test cases for AmisSchema model."""

    def test_valid_table_schema(self):
        """应该创建有效的表格 schema"""
        schema = AmisSchema(
            type="table",
            columns=[{"name": "id", "label": "ID"}],
            data={"items": [{"id": 1}]}
        )
        assert schema.type == "table"

    def test_valid_chart_schema(self):
        """应该创建有效的图表 schema"""
        schema = AmisSchema(
            type="chart",
            config={"xAxis": {"type": "category"}}
        )
        assert schema.type == "chart"

    def test_allow_extra_properties(self):
        """应该允许额外的 AMIS 属性"""
        schema = AmisSchema(
            type="form",
            title="Test Form",
            body=[{"type": "input-text", "name": "name"}]
        )
        assert schema.type == "form"
        # Extra properties should be allowed
        assert hasattr(schema, 'title') or schema.model_extra.get('title') == "Test Form"


class TestChatResponse:
    """Test cases for ChatResponse model."""

    def test_valid_text_response(self):
        """应该创建有效的文本响应"""
        resp = ChatResponse(
            action=AgentAction.TEXT,
            message="处理完成"
        )
        assert resp.action == AgentAction.TEXT
        assert resp.amis_schema is None
        assert resp.sql is None

    def test_valid_table_response(self):
        """应该创建有效的表格响应"""
        schema = AmisSchema(type="table", data={"items": []})
        resp = ChatResponse(
            action=AgentAction.TABLE,
            message="找到 10 条记录",
            amis_schema=schema,
            sql="SELECT * FROM objects"
        )
        assert resp.action == AgentAction.TABLE
        assert resp.sql == "SELECT * FROM objects"

    def test_valid_error_response(self):
        """应该创建有效的错误响应"""
        resp = ChatResponse(
            action=AgentAction.ERROR,
            message="SQL 验证失败",
            suggestions=["尝试更简单的问题"]
        )
        assert resp.action == AgentAction.ERROR
        assert len(resp.suggestions) == 1

    def test_default_suggestions_empty(self):
        """应该默认空建议列表"""
        resp = ChatResponse(action=AgentAction.TEXT, message="OK")
        assert resp.suggestions == []


class TestHealthResponse:
    """Test cases for HealthResponse model."""

    def test_valid_healthy_response(self):
        """应该创建健康状态响应"""
        resp = HealthResponse(
            ollama_available=True,
            model="llama3",
            status="ready"
        )
        assert resp.ollama_available is True
        assert resp.model == "llama3"

    def test_valid_unhealthy_response(self):
        """应该创建不健康状态响应"""
        resp = HealthResponse(
            ollama_available=False,
            model="llama3",
            status="ollama_unavailable"
        )
        assert resp.ollama_available is False


class TestAgentAction:
    """Test cases for AgentAction enum."""

    def test_all_action_types(self):
        """应该包含所有动作类型"""
        actions = [a.value for a in AgentAction]
        assert "query" in actions
        assert "table" in actions
        assert "chart" in actions
        assert "text" in actions
        assert "error" in actions
        assert "clarify" in actions
