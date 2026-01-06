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
