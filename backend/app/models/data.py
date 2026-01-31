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
    connection_id: Optional[str] = Field(default=None, max_length=36)  # V3 field: link to sys_connection
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
    connection_id: Optional[str] = None  # V3 field: link to sys_connection
    table_name: str
    db_type: str
    columns_schema: Optional[List[Dict[str, Any]]]
    created_at: Optional[datetime]


# ==========================================
# ExecutionLog Model
# ==========================================

class ExecutionLog(SQLModel, table=True):
    """Action execution log record.
    
    Maps to database table: sys_action_log
    """
    __tablename__ = "sys_action_log"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    project_id: str = Field(index=True, max_length=36)
    action_def_id: str = Field(index=True, max_length=36)
    trigger_user_id: Optional[str] = Field(default=None, max_length=36)  # 触发用户
    input_params: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))  # 执行入参
    execution_status: str = Field(default="SUCCESS", max_length=20)  # SUCCESS, FAILED
    error_message: Optional[str] = Field(default=None)
    duration_ms: Optional[int] = Field(default=None)  # 执行耗时
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, index=True)


# ==========================================
# DTOs for ExecutionLog
# ==========================================

class ExecutionLogCreate(SQLModel):
    """DTO for creating ExecutionLog."""
    project_id: str
    action_def_id: str
    trigger_user_id: Optional[str] = None
    input_params: Optional[Dict[str, Any]] = None
    execution_status: str = "SUCCESS"
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None


class ExecutionLogRead(SQLModel):
    """DTO for reading ExecutionLog."""
    id: str
    project_id: str
    action_def_id: str
    action_name: Optional[str] = None  # Populated from ActionDefinition join
    trigger_user_id: Optional[str]
    input_params: Optional[Dict[str, Any]]
    execution_status: str
    duration_ms: Optional[int]
    error_message: Optional[str]
    created_at: Optional[datetime]