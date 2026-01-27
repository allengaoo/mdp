"""
API Payload Schemas (DTOs) for strict type validation.
Separated from DB models to avoid circular imports.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ==========================================
# Nested Property Definitions
# ==========================================

class PropertyDef(BaseModel):
    """Property definition within ObjectType."""
    key: str = Field(..., description="Property API key (e.g., 'fuel')")
    label: str = Field(..., description="Display label (e.g., '燃油')")
    type: str = Field(..., description="Data type: STRING, INTEGER, DOUBLE, BOOLEAN, DATE, etc.")
    required: bool = Field(default=False, description="Whether this property is required")
    shared_property_id: Optional[str] = Field(default=None, description="Optional: Reference to shared property")


# ==========================================
# Link Mapping Configuration
# ==========================================

class LinkMappingConfig(BaseModel):
    """Mapping configuration for LinkType relationships."""
    join_table_id: Optional[str] = Field(default=None, description="For M:N relationships: join table ID")
    source_fk: Optional[str] = Field(default=None, description="Source foreign key column name")
    target_fk: Optional[str] = Field(default=None, description="Target foreign key column name")
    
    class Config:
        # Allow additional fields for backward compatibility
        extra = "allow"


# ==========================================
# Action Parameter Definition
# ==========================================

class ActionParamDef(BaseModel):
    """Action parameter definition."""
    key: str = Field(..., description="Parameter key")
    label: str = Field(..., description="Display label")
    type: str = Field(..., description="Parameter data type")


# ==========================================
# Request Models
# ==========================================

class ObjectTypeRequest(BaseModel):
    """Request model for creating/updating ObjectType."""
    api_name: str = Field(..., max_length=100, description="Unique API identifier")
    display_name: str = Field(..., max_length=200, description="Display name")
    project_id: Optional[str] = Field(default=None, max_length=36, description="Project ID")
    property_schema: List[PropertyDef] = Field(default_factory=list, description="List of property definitions")
    description: Optional[str] = Field(default=None, max_length=500, description="Optional description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "api_name": "fighter",
                "display_name": "战斗机",
                "project_id": "proj_001",
                "property_schema": [
                    {"key": "fuel", "label": "燃油", "type": "INTEGER", "required": True}
                ]
            }
        }


class LinkTypeRequest(BaseModel):
    """Request model for creating/updating LinkType."""
    api_name: str = Field(..., max_length=100, description="Unique API identifier")
    display_name: Optional[str] = Field(default=None, max_length=200, description="Display name")
    source_type_id: str = Field(..., max_length=36, description="Source ObjectType ID")
    target_type_id: str = Field(..., max_length=36, description="Target ObjectType ID")
    cardinality: str = Field(..., description="Cardinality: ONE_TO_ONE, ONE_TO_MANY, MANY_TO_MANY")
    mapping_config: Optional[LinkMappingConfig] = Field(default=None, description="Mapping configuration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "api_name": "participation",
                "source_type_id": "fighter",
                "target_type_id": "mission",
                "cardinality": "MANY_TO_MANY",
                "mapping_config": {"join_table_id": "tbl_link"}
            }
        }


class ActionRunRequest(BaseModel):
    """Request model for action execution."""
    action_api_name: str = Field(..., description="Action API name to execute")
    source_object_id: Optional[str] = Field(default=None, description="Source object ID (preferred field name)")
    source_id: Optional[str] = Field(default=None, description="Source object ID (backward compatibility alias)")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action_api_name": "strike",
                "source_object_id": "obj_123",
                "params": {"weapon": "missile"}
            }
        }
    
    def model_post_init(self, __context):
        """Ensure source_id is set if source_object_id is provided, and vice versa."""
        # Use source_object_id if provided, otherwise use source_id
        if self.source_object_id:
            self.source_id = self.source_object_id
        elif self.source_id:
            self.source_object_id = self.source_id
        else:
            # Neither provided - this will be validated by the endpoint
            pass
    
    @property
    def effective_source_id(self) -> Optional[str]:
        """Get the effective source ID (either source_object_id or source_id)."""
        return self.source_object_id or self.source_id


# ==========================================
# Response Models
# ==========================================

class ProjectResponse(BaseModel):
    """Response model for Project with aggregated statistics."""
    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(default=None, description="Project description")
    tags: List[str] = Field(default_factory=list, description="Project tags (default empty)")
    object_count: int = Field(..., description="Number of object types in this project")
    link_count: int = Field(..., description="Number of link types in this project")
    created_at: Optional[datetime] = Field(default=None, description="Creation time")
    updated_at: Optional[datetime] = Field(default=None, description="Last update time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "00000000-0000-0000-0000-000000000001",
                "name": "Battlefield System",
                "description": "军事战场场景本体",
                "tags": ["军事", "战场", "演示"],
                "object_count": 12,
                "link_count": 12,
                "created_at": "2024-01-15T14:30:00",
                "updated_at": "2024-01-15T14:30:00"
            }
        }

