"""
Chat2App API Endpoints.
MDP Platform V3.1

REST API for Chat Agent interactions.
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.core.ollama_client import ollama_client
from app.core.config import settings
from app.services.chat_agent import process_chat
from app.models.chat import ChatRequest, ChatResponse, HealthResponse


router = APIRouter(prefix="/chat", tags=["Chat2App"])


@router.get("/health", response_model=HealthResponse)
async def check_health():
    """
    Check Chat2App service health.
    
    Verifies Ollama connectivity and returns status.
    """
    is_available = await ollama_client.health_check()
    
    return HealthResponse(
        ollama_available=is_available,
        model=settings.ollama_model,
        status="ready" if is_available else "ollama_unavailable"
    )


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to the Chat Agent.
    
    Processes natural language query and returns:
    - Generated SQL (for transparency)
    - AMIS schema for UI rendering
    - Query results as data
    - Suggested follow-up questions
    """
    logger.info(f"Chat request: {request.message[:100]}...")
    
    response = await process_chat(request)
    
    logger.info(f"Chat response action: {response.action}")
    return response


@router.get("/schema-example")
async def get_schema_example():
    """
    Return example AMIS schemas for reference.
    
    Useful for frontend development and testing.
    """
    return {
        "table_example": {
            "type": "table",
            "columns": [
                {"name": "id", "label": "ID"},
                {"name": "name", "label": "名称"},
                {"name": "status", "label": "状态"}
            ],
            "data": {
                "items": [
                    {"id": 1, "name": "示例1", "status": "active"},
                    {"id": 2, "name": "示例2", "status": "inactive"}
                ]
            }
        },
        "chart_example": {
            "type": "chart",
            "config": {
                "xAxis": {"type": "category", "data": ["A", "B", "C"]},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar", "data": [10, 20, 30]}]
            }
        }
    }
