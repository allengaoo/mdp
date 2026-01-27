"""
Ontology Layer Models for MDP Platform V3.1
Tables: meta_shared_property_def, meta_object_type_def, meta_object_type_ver,
        rel_object_ver_property, meta_link_type_def, meta_link_type_ver, rel_link_ver_property
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Column, JSON


# ==========================================
# ORM Models - Shared Property
# ==========================================

class SharedPropertyDef(SQLModel, table=True):
    """Global shared property definition pool.
    
    Properties can be reused by multiple object types.
    Maps to table: meta_shared_property_def
    """
    __tablename__ = "meta_shared_property_def"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    api_name: str = Field(unique=True, index=True, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=100)
    data_type: str = Field(max_length=50)  # STRING, INT, DOUBLE, BOOLEAN, DATETIME, GEO_POINT, JSON, VECTOR, MEDIA_REF
    description: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# ==========================================
# ORM Models - Object Type Definition & Version
# ==========================================

class ObjectTypeDef(SQLModel, table=True):
    """Object type definition (immutable identifier).
    
    Maps to table: meta_object_type_def
    """
    __tablename__ = "meta_object_type_def"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    api_name: str = Field(unique=True, index=True, max_length=100)
    stereotype: str = Field(default="ENTITY", max_length=50)  # ENTITY, EVENT, DOCUMENT, MEDIA, METRIC
    current_version_id: Optional[str] = Field(default=None, max_length=36)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ObjectTypeVer(SQLModel, table=True):
    """Object type version (contains specific configuration).
    
    Maps to table: meta_object_type_ver
    """
    __tablename__ = "meta_object_type_ver"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    def_id: str = Field(foreign_key="meta_object_type_def.id", max_length=36)
    version_number: str = Field(max_length=50)
    display_name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(default=None, max_length=255)
    color: Optional[str] = Field(default=None, max_length=20)
    status: str = Field(default="DRAFT", max_length=50)  # DRAFT, PUBLISHED, DEPRECATED
    enable_global_search: bool = Field(default=False)
    enable_geo_index: bool = Field(default=False)
    enable_vector_index: bool = Field(default=False)
    cache_ttl_seconds: int = Field(default=0)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ObjectVerProperty(SQLModel, table=True):
    """Object version to property binding relationship.
    
    Maps to table: rel_object_ver_property
    """
    __tablename__ = "rel_object_ver_property"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    object_ver_id: str = Field(foreign_key="meta_object_type_ver.id", max_length=36)
    property_def_id: str = Field(foreign_key="meta_shared_property_def.id", max_length=36)
    local_api_name: Optional[str] = Field(default=None, max_length=100)  # Local alias
    is_primary_key: bool = Field(default=False)
    is_required: bool = Field(default=False)
    is_title: bool = Field(default=False)  # Display as object title
    default_value: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    # Search configuration flags
    is_searchable: bool = Field(default=False)  # Enable full-text search (ES text field)
    is_filterable: bool = Field(default=False)  # Enable facets/aggregations (ES keyword field)
    is_sortable: bool = Field(default=False)    # Enable sorting capability


# ==========================================
# ORM Models - Link Type Definition & Version
# ==========================================

class LinkTypeDef(SQLModel, table=True):
    """Link type definition (immutable identifier).
    
    Maps to table: meta_link_type_def
    """
    __tablename__ = "meta_link_type_def"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    api_name: str = Field(unique=True, index=True, max_length=100)
    current_version_id: Optional[str] = Field(default=None, max_length=36)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class LinkTypeVer(SQLModel, table=True):
    """Link type version.
    
    Maps to table: meta_link_type_ver
    """
    __tablename__ = "meta_link_type_ver"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    def_id: str = Field(foreign_key="meta_link_type_def.id", max_length=36)
    version_number: str = Field(max_length=50)
    display_name: Optional[str] = Field(default=None, max_length=100)
    source_object_def_id: str = Field(foreign_key="meta_object_type_def.id", max_length=36)
    target_object_def_id: str = Field(foreign_key="meta_object_type_def.id", max_length=36)
    cardinality: str = Field(max_length=50)  # ONE_TO_ONE, ONE_TO_MANY, MANY_TO_ONE, MANY_TO_MANY
    status: str = Field(default="DRAFT", max_length=50)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class LinkVerProperty(SQLModel, table=True):
    """Link version to property binding relationship.
    
    Maps to table: rel_link_ver_property
    """
    __tablename__ = "rel_link_ver_property"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    link_ver_id: str = Field(foreign_key="meta_link_type_ver.id", max_length=36)
    property_def_id: str = Field(foreign_key="meta_shared_property_def.id", max_length=36)
    local_api_name: Optional[str] = Field(default=None, max_length=100)


# ==========================================
# DTOs - Shared Property
# ==========================================

class SharedPropertyDefCreate(SQLModel):
    """DTO for creating SharedPropertyDef."""
    api_name: str = Field(max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=100)
    data_type: str = Field(max_length=50)
    description: Optional[str] = None


class SharedPropertyDefUpdate(SQLModel):
    """DTO for updating SharedPropertyDef."""
    display_name: Optional[str] = Field(default=None, max_length=100)
    data_type: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = None


class SharedPropertyDefRead(SQLModel):
    """DTO for reading SharedPropertyDef."""
    id: str
    api_name: str
    display_name: Optional[str]
    data_type: str
    description: Optional[str]
    created_at: Optional[datetime]


# ==========================================
# DTOs - Object Type Definition
# ==========================================

class ObjectTypeDefCreate(SQLModel):
    """DTO for creating ObjectTypeDef."""
    api_name: str = Field(max_length=100)
    stereotype: str = Field(default="ENTITY", max_length=50)


class ObjectTypeDefRead(SQLModel):
    """DTO for reading ObjectTypeDef."""
    id: str
    api_name: str
    stereotype: str
    current_version_id: Optional[str]
    created_at: Optional[datetime]


# ==========================================
# DTOs - Object Type Version
# ==========================================

class ObjectTypeVerCreate(SQLModel):
    """DTO for creating ObjectTypeVer."""
    def_id: str = Field(max_length=36)
    version_number: str = Field(max_length=50)
    display_name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(default=None, max_length=255)
    color: Optional[str] = Field(default=None, max_length=20)
    status: str = Field(default="DRAFT", max_length=50)
    enable_global_search: bool = False
    enable_geo_index: bool = False
    enable_vector_index: bool = False
    cache_ttl_seconds: int = 0


class ObjectTypeVerUpdate(SQLModel):
    """DTO for updating ObjectTypeVer."""
    display_name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(default=None, max_length=255)
    color: Optional[str] = Field(default=None, max_length=20)
    status: Optional[str] = Field(default=None, max_length=50)
    enable_global_search: Optional[bool] = None
    enable_geo_index: Optional[bool] = None
    enable_vector_index: Optional[bool] = None
    cache_ttl_seconds: Optional[int] = None


class ObjectTypeVerRead(SQLModel):
    """DTO for reading ObjectTypeVer."""
    id: str
    def_id: str
    version_number: str
    display_name: Optional[str]
    description: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    status: str
    enable_global_search: bool
    enable_geo_index: bool
    enable_vector_index: bool
    cache_ttl_seconds: int
    created_at: Optional[datetime]


class ObjectTypeFullRead(SQLModel):
    """DTO for reading ObjectType with definition and current version."""
    # Definition fields
    id: str
    api_name: str
    stereotype: str
    # Current version fields
    version_id: Optional[str] = None
    version_number: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    status: Optional[str] = None
    # Properties
    properties: List[Dict[str, Any]] = []
    # Datasource information
    datasource: Optional[Dict[str, Any]] = None  # {
    #   "type": "pipeline" | "mapping",
    #   "dataset_id": str,
    #   "dataset_name": str,
    #   "table_name": str,
    #   "db_type": str,
    #   "connection_id": str,
    #   "connection_name": str,
    #   "pipeline_id": str,
    #   "pipeline_mode": str,
    #   "sync_status": str,  # PENDING, RUNNING, SUCCESS, FAILED
    #   "last_sync_time": str,
    #   "rows_processed": int,
    #   "source_table_name": str,  # For mapping type
    # }


# ==========================================
# DTOs - Object Version Property Binding
# ==========================================

class ObjectVerPropertyCreate(SQLModel):
    """DTO for binding property to object version."""
    property_def_id: str = Field(max_length=36)
    local_api_name: Optional[str] = Field(default=None, max_length=100)
    is_primary_key: bool = False
    is_required: bool = False
    is_title: bool = False
    default_value: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    # Search configuration
    is_searchable: bool = False
    is_filterable: bool = False
    is_sortable: bool = False


class ObjectVerPropertyRead(SQLModel):
    """DTO for reading property binding."""
    binding_id: int  # Renamed from 'id' for clarity (matches frontend IV3ObjectTypeProperty)
    object_ver_id: str
    property_def_id: str
    local_api_name: Optional[str]
    is_primary_key: bool
    is_required: bool
    is_title: bool
    default_value: Optional[str]
    validation_rules: Optional[Dict[str, Any]]
    # Search configuration
    is_searchable: bool = False
    is_filterable: bool = False
    is_sortable: bool = False
    # Joined property info
    property_api_name: Optional[str] = None
    property_display_name: Optional[str] = None
    property_data_type: Optional[str] = None


# ==========================================
# DTOs - Link Type Definition
# ==========================================

class LinkTypeDefCreate(SQLModel):
    """DTO for creating LinkTypeDef."""
    api_name: str = Field(max_length=100)


class LinkTypeDefRead(SQLModel):
    """DTO for reading LinkTypeDef."""
    id: str
    api_name: str
    current_version_id: Optional[str]
    created_at: Optional[datetime]


# ==========================================
# DTOs - Link Type Version
# ==========================================

class LinkTypeVerCreate(SQLModel):
    """DTO for creating LinkTypeVer."""
    def_id: str = Field(max_length=36)
    version_number: str = Field(max_length=50)
    display_name: Optional[str] = Field(default=None, max_length=100)
    source_object_def_id: str = Field(max_length=36)
    target_object_def_id: str = Field(max_length=36)
    cardinality: str = Field(max_length=50)
    status: str = Field(default="DRAFT", max_length=50)


class LinkTypeVerUpdate(SQLModel):
    """DTO for updating LinkTypeVer."""
    display_name: Optional[str] = Field(default=None, max_length=100)
    status: Optional[str] = Field(default=None, max_length=50)


class LinkTypeVerRead(SQLModel):
    """DTO for reading LinkTypeVer."""
    id: str
    def_id: str
    version_number: str
    display_name: Optional[str]
    source_object_def_id: str
    target_object_def_id: str
    cardinality: str
    status: str
    created_at: Optional[datetime]


class LinkTypeFullRead(SQLModel):
    """DTO for reading LinkType with definition and current version."""
    # Definition fields
    id: str
    api_name: str
    # Current version fields
    version_id: Optional[str] = None
    version_number: Optional[str] = None
    display_name: Optional[str] = None
    source_object_def_id: Optional[str] = None
    target_object_def_id: Optional[str] = None
    cardinality: Optional[str] = None
    status: Optional[str] = None
    # Joined object type names
    source_type_name: Optional[str] = None
    target_type_name: Optional[str] = None


# ==========================================
# DTOs - Object Type with Statistics
# ==========================================

class ObjectDefWithStats(SQLModel):
    """DTO for object type definition with aggregated statistics.
    
    Used by Object Center page to display object types with counts.
    """
    # Definition fields
    id: str
    api_name: str
    stereotype: str = "ENTITY"
    # Version fields
    display_name: Optional[str] = None
    description: Optional[str] = None
    status: str = "DRAFT"  # DRAFT, PUBLISHED, DEPRECATED
    # Statistics
    property_count: int = 0  # Number of properties bound to this object type
    instance_count: int = 0  # Number of data instances (placeholder, requires instance table)
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==========================================
# DTOs - Topology Graph Data
# ==========================================

class TopologyNode(SQLModel):
    """Node data for topology visualization.
    
    Maps to: meta_object_type_def JOIN meta_object_type_ver
    """
    id: str                              # ObjectTypeDef.id
    api_name: str                        # ObjectTypeDef.api_name
    display_name: Optional[str] = None   # ObjectTypeVer.display_name
    stereotype: str = "ENTITY"           # ObjectTypeDef.stereotype
    icon: Optional[str] = None           # ObjectTypeVer.icon
    color: Optional[str] = None          # ObjectTypeVer.color


class TopologyEdge(SQLModel):
    """Edge data for topology visualization.
    
    Maps to: meta_link_type_def JOIN meta_link_type_ver
    """
    id: str                              # LinkTypeDef.id
    api_name: str                        # LinkTypeDef.api_name
    display_name: Optional[str] = None   # LinkTypeVer.display_name
    source: str                          # LinkTypeVer.source_object_def_id
    target: str                          # LinkTypeVer.target_object_def_id
    cardinality: Optional[str] = None    # LinkTypeVer.cardinality


class TopologyData(SQLModel):
    """Complete topology graph data for visualization."""
    nodes: List[TopologyNode] = []
    edges: List[TopologyEdge] = []
