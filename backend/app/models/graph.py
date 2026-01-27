"""
Graph Layer Models for MDP Platform V3.1
Tables: sys_link_instance

Stores actual link instances between object instances.
Supports both hard links (database FK) and temporal analysis.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Column, JSON


class SysLinkInstance(SQLModel, table=True):
    """
    Link instance connecting two object instances.
    
    Supports:
    - Polymorphic links (any object type to any object type)
    - Temporal validity (valid_start, valid_end)
    - Custom properties (confidence score, role, etc.)
    
    Maps to table: sys_link_instance
    """
    __tablename__ = "sys_link_instance"
    __table_args__ = {"extend_existing": True}
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    
    # Reference to link type definition (schema)
    link_type_id: Optional[str] = Field(default=None, max_length=36, index=True)
    
    # Polymorphic source/target (can be any object instance)
    source_instance_id: str = Field(max_length=255, index=True)
    target_instance_id: str = Field(max_length=255, index=True)
    
    # Source/Target object type for quick filtering
    source_object_type: Optional[str] = Field(default=None, max_length=100)
    target_object_type: Optional[str] = Field(default=None, max_length=100)
    
    # Temporal analysis support
    valid_start: Optional[datetime] = Field(default=None)
    valid_end: Optional[datetime] = Field(default=None)
    
    # Custom properties (confidence, role, weight, etc.)
    properties: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Audit fields
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# ==========================================
# DTOs for Graph Operations
# ==========================================

class GraphNode(SQLModel):
    """Node in a graph response (React Flow compatible)."""
    id: str
    type: str = "objectNode"  # React Flow node type
    position: Dict[str, float] = {"x": 0, "y": 0}
    data: Dict[str, Any] = {}


class GraphEdge(SQLModel):
    """Edge in a graph response (React Flow compatible)."""
    id: str
    source: str
    target: str
    type: str = "default"  # 'default' or 'semantic'
    animated: bool = False
    style: Optional[Dict[str, Any]] = None
    label: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class GraphDTO(SQLModel):
    """Complete graph data for React Flow."""
    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []


class ExpandOptions(SQLModel):
    """Options for graph expansion."""
    semantic: bool = False  # Include semantic/vector similarity links
    limit: int = 50  # Max neighbors to return
    depth: int = 1  # Expansion depth (1 = immediate neighbors)
    link_types: Optional[List[str]] = None  # Filter by link type


class ExpandRequest(SQLModel):
    """Request body for expand endpoint."""
    seed_ids: List[str]
    options: Optional[ExpandOptions] = None


class ShortestPathRequest(SQLModel):
    """Request body for shortest path endpoint."""
    source: str
    target: str
    max_depth: int = 10


class ShortestPathResponse(SQLModel):
    """Response for shortest path query."""
    found: bool
    path: List[str] = []
    edges: List[GraphEdge] = []
    distance: int = 0
