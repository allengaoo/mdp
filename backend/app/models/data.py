"""
Data models for ObjectInstance, LinkInstance, and DataSourceTable.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Column, JSON


class ObjectInstance(SQLModel, table=True):
    """Object instance (actual data rows with JSON properties)."""
    __tablename__ = "sys_object_instance"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    object_type_id: str = Field(foreign_key="meta_object_type.id", max_length=36)
    properties: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


class LinkInstance(SQLModel, table=True):
    """Link instance (connections between objects)."""
    __tablename__ = "sys_link_instance"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    link_type_id: str = Field(foreign_key="meta_link_type.id", max_length=36)
    source_instance_id: str = Field(foreign_key="sys_object_instance.id", max_length=36)
    target_instance_id: str = Field(foreign_key="sys_object_instance.id", max_length=36)
    properties: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: Optional[datetime] = Field(default=None)


class DataSourceTable(SQLModel, table=True):
    """Data source table definition (raw data sources for object types)."""
    __tablename__ = "sys_datasource_table"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    table_name: str = Field(unique=True, index=True, max_length=100)
    db_type: str = Field(default="MySQL", max_length=20)
    columns_schema: Optional[List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    created_at: Optional[datetime] = Field(default=None)


# ==========================================
# DTOs for DataSourceTable
# ==========================================

class DataSourceTableCreate(SQLModel):
    """DTO for creating DataSourceTable."""
    table_name: str = Field(max_length=100)
    db_type: str = Field(default="MySQL", max_length=20)
    columns_schema: Optional[List[Dict[str, Any]]] = None


class DataSourceTableRead(SQLModel):
    """DTO for reading DataSourceTable."""
    id: str
    table_name: str
    db_type: str
    columns_schema: Optional[List[Dict[str, Any]]]
    created_at: Optional[datetime]


# ==========================================
# ExecutionLog Model
# ==========================================

class ExecutionLog(SQLModel, table=True):
    """Action execution log record."""
    __tablename__ = "sys_action_log"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True, max_length=36)
    action_def_id: str = Field(index=True, max_length=36)
    source_object_id: Optional[str] = Field(default=None, max_length=36)
    execution_status: str = Field(default="SUCCESS", index=True, max_length=20)  # SUCCESS, FAILED
    duration_ms: Optional[int] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    request_params: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, index=True)


# ==========================================
# DTOs for ExecutionLog
# ==========================================

class ExecutionLogCreate(SQLModel):
    """DTO for creating ExecutionLog."""
    project_id: str
    action_def_id: str
    source_object_id: Optional[str] = None
    execution_status: str = "SUCCESS"
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None
    request_params: Optional[Dict[str, Any]] = None


class ExecutionLogRead(SQLModel):
    """DTO for reading ExecutionLog."""
    id: str
    project_id: str
    action_def_id: str
    action_name: Optional[str] = None  # Populated from ActionDefinition join
    source_object_id: Optional[str]
    execution_status: str
    duration_ms: Optional[int]
    error_message: Optional[str]
    request_params: Optional[Dict[str, Any]]
    created_at: Optional[datetime]