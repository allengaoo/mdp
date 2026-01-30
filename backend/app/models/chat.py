"""
Chat2App Data Models.
MDP Platform V3.1

Pydantic models for Chat Agent request/response.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Single message in conversation."""
    role: MessageRole
    content: str


class AgentAction(str, Enum):
    """Agent response action type."""
    QUERY = "query"         # Execute SQL and show results
    FORM = "form"           # Render AMIS form
    TABLE = "table"         # Render AMIS table
    CHART = "chart"         # Render AMIS chart
    TEXT = "text"           # Plain text response
    ERROR = "error"         # Error message
    CLARIFY = "clarify"     # Ask for clarification


class ChatRequest(BaseModel):
    """Request to Chat Agent."""
    message: str = Field(..., description="User's natural language query")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context (selected object, current view, etc.)"
    )
    history: List[ChatMessage] = Field(
        default_factory=list,
        description="Conversation history"
    )


class AmisSchema(BaseModel):
    """AMIS JSON Schema for UI rendering."""
    type: str = Field(..., description="AMIS component type")
    body: Optional[Any] = Field(default=None, description="Component body")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Data to render")
    
    class Config:
        extra = "allow"  # Allow additional AMIS properties


class ChatResponse(BaseModel):
    """Response from Chat Agent."""
    action: AgentAction = Field(..., description="Action type")
    message: str = Field(..., description="Human-readable message")
    amis_schema: Optional[AmisSchema] = Field(
        default=None,
        description="AMIS schema for UI rendering"
    )
    sql: Optional[str] = Field(
        default=None,
        description="Generated SQL (for transparency)"
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw data if applicable"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up questions"
    )


class HealthResponse(BaseModel):
    """Health check response."""
    ollama_available: bool
    model: str
    status: str
