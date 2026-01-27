"""
Context Layer Models for MDP Platform V3.1
Tables: ctx_project_object_binding, ctx_object_mapping_def
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON


# ==========================================
# ORM Models - Context Binding
# ==========================================

class ProjectObjectBinding(SQLModel, table=True):
    """Project to object type binding relationship.
    
    Defines which object type version a project uses,
    with optional project-specific display alias.
    Maps to table: ctx_project_object_binding
    """
    __tablename__ = "ctx_project_object_binding"
    
    project_id: str = Field(foreign_key="sys_project.id", primary_key=True, max_length=36)
    object_def_id: str = Field(foreign_key="meta_object_type_def.id", primary_key=True, max_length=36)
    used_version_id: str = Field(foreign_key="meta_object_type_ver.id", max_length=36)
    project_display_alias: Optional[str] = Field(default=None, max_length=100)
    is_visible: bool = Field(default=True)


# ==========================================
# DTOs - Project Object Binding
# ==========================================

class ProjectObjectBindingCreate(SQLModel):
    """DTO for creating ProjectObjectBinding."""
    project_id: str = Field(max_length=36)
    object_def_id: str = Field(max_length=36)
    used_version_id: str = Field(max_length=36)
    project_display_alias: Optional[str] = Field(default=None, max_length=100)
    is_visible: bool = True


class ProjectObjectBindingUpdate(SQLModel):
    """DTO for updating ProjectObjectBinding."""
    used_version_id: Optional[str] = Field(default=None, max_length=36)
    project_display_alias: Optional[str] = Field(default=None, max_length=100)
    is_visible: Optional[bool] = None


class ProjectObjectBindingRead(SQLModel):
    """DTO for reading ProjectObjectBinding."""
    project_id: str
    object_def_id: str
    used_version_id: str
    project_display_alias: Optional[str]
    is_visible: bool


class ProjectObjectBindingWithDetails(ProjectObjectBindingRead):
    """DTO for binding with related entity details."""
    project_name: Optional[str] = None
    object_type_api_name: Optional[str] = None
    object_type_display_name: Optional[str] = None
    version_number: Optional[str] = None


# ==========================================
# ORM Models - Multimodal Mapping
# ==========================================

class ObjectMappingDef(SQLModel, table=True):
    """Multimodal mapping definition - stores React Flow graph logic.
    
    Defines how to map raw data columns to ontology object properties,
    including transformation logic (e.g., image -> vector embedding).
    Maps to table: ctx_object_mapping_def
    """
    __tablename__ = "ctx_object_mapping_def"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    object_def_id: str = Field(max_length=36, index=True)  # Target ontology object type
    source_connection_id: str = Field(max_length=36)  # Source connection
    source_table_name: str = Field(max_length=100)  # Table in mdp_raw_store
    mapping_spec: Dict[str, Any] = Field(sa_column=Column(JSON))  # React Flow nodes & edges
    status: str = Field(default="DRAFT", max_length=20)  # DRAFT, PUBLISHED, ARCHIVED
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# ==========================================
# DTOs - Object Mapping
# ==========================================

class ObjectMappingDefCreate(SQLModel):
    """DTO for creating ObjectMappingDef."""
    object_def_id: str = Field(max_length=36)
    source_connection_id: str = Field(max_length=36)
    source_table_name: str = Field(max_length=100)
    mapping_spec: Dict[str, Any]


class ObjectMappingDefUpdate(SQLModel):
    """DTO for updating ObjectMappingDef."""
    source_table_name: Optional[str] = Field(default=None, max_length=100)
    mapping_spec: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(default=None, max_length=20)


class ObjectMappingDefRead(SQLModel):
    """DTO for reading ObjectMappingDef."""
    id: str
    object_def_id: str
    source_connection_id: str
    source_table_name: str
    mapping_spec: Dict[str, Any]
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class ObjectMappingDefWithDetails(ObjectMappingDefRead):
    """DTO with related entity details."""
    object_type_name: Optional[str] = None
    connection_name: Optional[str] = None


# ==========================================
# DTOs - Mapping Preview
# ==========================================

class MappingPreviewRequest(SQLModel):
    """DTO for requesting mapping preview."""
    source_connection_id: str = Field(max_length=36)
    source_table_name: str = Field(max_length=100)
    mapping_spec: Dict[str, Any]
    limit: int = Field(default=5, ge=1, le=100)


class MappingPreviewResponse(SQLModel):
    """DTO for mapping preview result."""
    columns: list[str]
    data: list[Dict[str, Any]]
    row_count: int
    warnings: Optional[list[str]] = None


# ==========================================
# ORM Models - Object Instance Lineage
# ==========================================

class ObjectInstanceLineage(SQLModel, table=True):
    """Object instance lineage - tracks vector to source data mapping.
    
    Enables tracing from a vector/instance back to its original source row,
    supporting queries like "which file does this vector come from?"
    Maps to table: ctx_object_instance_lineage
    """
    __tablename__ = "ctx_object_instance_lineage"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    object_def_id: str = Field(max_length=36, index=True)  # Ontology object type
    instance_id: str = Field(max_length=36, index=True)  # Object instance ID (also ChromaDB vector ID)
    mapping_id: str = Field(max_length=36, index=True)  # Source mapping definition
    source_table: str = Field(max_length=100)  # Original table in mdp_raw_store
    source_row_id: str = Field(max_length=100)  # Original row ID/PK
    source_file_path: Optional[str] = Field(default=None, max_length=500)  # File path for unstructured data
    vector_collection: Optional[str] = Field(default=None, max_length=100)  # ChromaDB collection name
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# ==========================================
# DTOs - Object Instance Lineage
# ==========================================

class ObjectInstanceLineageCreate(SQLModel):
    """DTO for creating lineage record."""
    object_def_id: str = Field(max_length=36)
    instance_id: str = Field(max_length=36)
    mapping_id: str = Field(max_length=36)
    source_table: str = Field(max_length=100)
    source_row_id: str = Field(max_length=100)
    source_file_path: Optional[str] = Field(default=None, max_length=500)
    vector_collection: Optional[str] = Field(default=None, max_length=100)


class ObjectInstanceLineageRead(SQLModel):
    """DTO for reading lineage record."""
    id: str
    object_def_id: str
    instance_id: str
    mapping_id: str
    source_table: str
    source_row_id: str
    source_file_path: Optional[str]
    vector_collection: Optional[str]
    created_at: Optional[datetime]


class LineageLookupResponse(SQLModel):
    """DTO for lineage lookup result."""
    instance_id: str
    object_def_id: str
    source_table: str
    source_row_id: str
    source_file_path: Optional[str]
    vector_collection: Optional[str]
