"""
Meta models for ObjectType, LinkType, FunctionDefinition, and ActionDefinition.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Column, JSON


# ==========================================
# Base SQLModel Definitions
# ==========================================

class Project(SQLModel, table=True):
    """Project definition."""
    __tablename__ = "meta_project"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: Optional[datetime] = Field(default=None)


class ObjectType(SQLModel, table=True):
    """Object type definition."""
    __tablename__ = "meta_object_type"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    api_name: str = Field(unique=True, index=True, max_length=100)
    display_name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    property_schema: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    project_id: Optional[str] = Field(default=None, foreign_key="meta_project.id", max_length=36)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


class LinkType(SQLModel, table=True):
    """Link type definition (relationship definitions)."""
    __tablename__ = "meta_link_type"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    api_name: str = Field(unique=True, index=True, max_length=100)
    display_name: str = Field(max_length=200)
    source_type_id: str = Field(foreign_key="meta_object_type.id", max_length=36)
    target_type_id: str = Field(foreign_key="meta_object_type.id", max_length=36)
    cardinality: str = Field(default="MANY_TO_MANY", max_length=50)


class FunctionDefinition(SQLModel, table=True):
    """Function definition (business logic code)."""
    __tablename__ = "meta_function_def"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    api_name: str = Field(unique=True, index=True, max_length=100)
    display_name: str = Field(max_length=200)
    code_content: Optional[str] = None
    bound_object_type_id: Optional[str] = Field(default=None, foreign_key="meta_object_type.id", max_length=36)
    description: Optional[str] = Field(default=None, max_length=500)
    input_params_schema: Optional[List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    output_type: str = Field(default="VOID", max_length=50)


class ActionDefinition(SQLModel, table=True):
    """Action definition (user triggers)."""
    __tablename__ = "meta_action_def"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    api_name: str = Field(unique=True, index=True, max_length=100)
    display_name: str = Field(max_length=200)
    backing_function_id: str = Field(foreign_key="meta_function_def.id", max_length=36)


class SharedProperty(SQLModel, table=True):
    """Shared property definition (common properties across ObjectTypes)."""
    __tablename__ = "meta_shared_property"
    # 禁用自动反射，使用显式定义的列
    __table_args__ = {'extend_existing': True}
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    api_name: str = Field(max_length=100)
    display_name: str = Field(max_length=200)
    data_type: str = Field(max_length=50)
    formatter: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: Optional[datetime] = Field(default=None)


# ==========================================
# 底层表模型 (用于写入操作)
# 这些表是 meta_object_type 和 meta_link_type 视图的底层数据源
# ==========================================

class OntObjectType(SQLModel, table=True):
    """底层对象类型定义表 - 用于写入操作。
    
    视图 meta_object_type 从此表读取数据。
    """
    __tablename__ = "ont_object_type"
    __table_args__ = {'extend_existing': True}
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    api_name: str = Field(unique=True, index=True, max_length=100)
    display_name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None)
    backing_dataset_id: str = Field(max_length=36)  # 关联到 sys_dataset
    title_property_id: Optional[str] = Field(default=None, max_length=36)
    created_at: Optional[datetime] = Field(default=None)


class OntLinkType(SQLModel, table=True):
    """底层链接类型定义表 - 用于写入操作。
    
    视图 meta_link_type 从此表读取数据。
    """
    __tablename__ = "ont_link_type"
    __table_args__ = {'extend_existing': True}
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    api_name: str = Field(unique=True, index=True, max_length=100)
    display_name: str = Field(max_length=200)
    source_object_type_id: str = Field(max_length=36)  # 对应视图中的 source_type_id
    target_object_type_id: str = Field(max_length=36)  # 对应视图中的 target_type_id
    cardinality: str = Field(default="MANY_TO_MANY", max_length=20)


# ==========================================
# DTOs for Project
# ==========================================

class ProjectCreate(SQLModel):
    """DTO for creating Project."""
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class ProjectRead(SQLModel):
    """DTO for reading Project."""
    id: str
    name: str
    description: Optional[str]
    created_at: Optional[datetime]


# ==========================================
# DTOs for ObjectType
# ==========================================

class ObjectTypeCreate(SQLModel):
    """DTO for creating ObjectType."""
    api_name: str = Field(max_length=100)
    display_name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    property_schema: Optional[Dict[str, Any]] = None
    project_id: Optional[str] = Field(default=None, max_length=36)
    source_connection_id: Optional[str] = Field(default=None, max_length=36)
    source_table_name: Optional[str] = Field(default=None, max_length=100)


class ObjectTypeUpdate(SQLModel):
    """DTO for updating ObjectType."""
    display_name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    property_schema: Optional[Dict[str, Any]] = None


class ObjectTypeRead(SQLModel):
    """DTO for reading ObjectType."""
    id: str
    api_name: str
    display_name: str
    description: Optional[str]
    property_schema: Optional[Dict[str, Any]]
    project_id: Optional[str]
    created_at: datetime
    updated_at: datetime


# ==========================================
# DTOs for LinkType
# ==========================================

class LinkTypeCreate(SQLModel):
    """DTO for creating LinkType."""
    api_name: str = Field(max_length=100)
    display_name: str = Field(max_length=200)
    source_type_id: str = Field(max_length=36)
    target_type_id: str = Field(max_length=36)
    cardinality: str = Field(default="MANY_TO_MANY", max_length=50)


class LinkTypeUpdate(SQLModel):
    """DTO for updating LinkType."""
    display_name: Optional[str] = Field(default=None, max_length=200)
    # Note: description field removed - not in database schema
    source_type_id: Optional[str] = Field(default=None, max_length=36)
    target_type_id: Optional[str] = Field(default=None, max_length=36)
    cardinality: Optional[str] = Field(default=None, max_length=50)


class LinkTypeRead(SQLModel):
    """DTO for reading LinkType."""
    id: str
    api_name: str
    display_name: str
    source_type_id: str
    target_type_id: str
    cardinality: str


# ==========================================
# DTOs for FunctionDefinition
# ==========================================

class FunctionDefinitionCreate(SQLModel):
    """DTO for creating FunctionDefinition."""
    api_name: str = Field(max_length=100)
    display_name: str = Field(max_length=200)
    code_content: Optional[str] = None
    bound_object_type_id: Optional[str] = Field(default=None, max_length=36)
    description: Optional[str] = Field(default=None, max_length=500)
    input_params_schema: Optional[List[Dict[str, Any]]] = None
    output_type: str = Field(default="VOID", max_length=50)


class FunctionDefinitionUpdate(SQLModel):
    """DTO for updating FunctionDefinition."""
    display_name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    code_content: Optional[str] = None
    bound_object_type_id: Optional[str] = Field(default=None, max_length=36)
    input_params_schema: Optional[List[Dict[str, Any]]] = None
    output_type: Optional[str] = Field(default=None, max_length=50)


class FunctionDefinitionRead(SQLModel):
    """DTO for reading FunctionDefinition."""
    id: str
    api_name: str
    display_name: str
    code_content: Optional[str]
    bound_object_type_id: Optional[str]
    description: Optional[str]
    input_params_schema: Optional[List[Dict[str, Any]]]
    output_type: str


# ==========================================
# DTOs for ActionDefinition
# ==========================================

class ActionDefinitionCreate(SQLModel):
    """DTO for creating ActionDefinition."""
    api_name: str = Field(max_length=100)
    display_name: str = Field(max_length=200)
    backing_function_id: str = Field(max_length=36)


class ActionDefinitionUpdate(SQLModel):
    """DTO for updating ActionDefinition."""
    display_name: Optional[str] = Field(default=None, max_length=200)
    backing_function_id: Optional[str] = Field(default=None, max_length=36)


class ActionDefinitionRead(SQLModel):
    """DTO for reading ActionDefinition."""
    id: str
    api_name: str
    display_name: str
    backing_function_id: str


# ==========================================
# DTOs for Actions & Logic Page (V3)
# ==========================================

class ActionDefWithFunction(SQLModel):
    """Action definition with resolved function details.
    
    Used by Actions & Logic page to display actions with their bound functions.
    """
    id: str
    api_name: str
    display_name: str
    backing_function_id: str
    # Resolved from FunctionDefinition JOIN
    function_api_name: Optional[str] = None
    function_display_name: Optional[str] = None


class FunctionDefForList(SQLModel):
    """Function definition for list display.
    
    Used by Actions & Logic page to display functions with code preview.
    """
    id: str
    api_name: str
    display_name: str
    description: Optional[str] = None
    output_type: str = "VOID"
    code_content: Optional[str] = None  # For drawer preview


# ==========================================
# DTOs for SharedProperty
# ==========================================

class SharedPropertyCreate(SQLModel):
    """DTO for creating SharedProperty."""
    api_name: str = Field(max_length=100)
    display_name: str = Field(max_length=200)
    data_type: str = Field(max_length=50)
    formatter: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=500)


class SharedPropertyUpdate(SQLModel):
    """DTO for updating SharedProperty."""
    display_name: Optional[str] = Field(default=None, max_length=200)
    data_type: Optional[str] = Field(default=None, max_length=50)
    formatter: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=500)


class SharedPropertyRead(SQLModel):
    """DTO for reading SharedProperty."""
    id: str
    api_name: str
    display_name: str
    data_type: str
    formatter: Optional[str]
    description: Optional[str]
    created_at: Optional[datetime]
