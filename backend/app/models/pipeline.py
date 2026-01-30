"""
Pipeline Layer Models for MDP Platform V3.1
Tables: sys_pipeline_def, sys_sync_task
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON


# ==========================================
# ORM Models - Pipeline
# ==========================================

class PipelineDef(SQLModel, table=True):
    """Data pipeline definition.
    
    Modes:
    - VIRTUAL: Real-time query (no data copy)
    - MATERIALIZED: Cached/materialized data
    - MEDIA_EXTRACT: Multimedia processing (OCR/ASR/Embedding)
    
    Maps to table: sys_pipeline_def
    """
    __tablename__ = "sys_pipeline_def"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    name: Optional[str] = Field(default=None, max_length=100)
    object_ver_id: str = Field(foreign_key="meta_object_type_ver.id", max_length=36)
    dataset_id: str = Field(foreign_key="sys_dataset.id", max_length=36)
    mode: str = Field(default="VIRTUAL", max_length=50)  # VIRTUAL, MATERIALIZED, MEDIA_EXTRACT
    transform_rules: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    filter_predicate: Optional[str] = None  # SQL WHERE clause
    sync_schedule: Optional[str] = Field(default=None, max_length=50)  # Cron expression
    media_process_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class SyncTask(SQLModel, table=True):
    """Data sync task execution record.
    
    Maps to table: sys_sync_task
    """
    __tablename__ = "sys_sync_task"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    pipeline_id: str = Field(foreign_key="sys_pipeline_def.id", max_length=36)
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = Field(max_length=50)  # PENDING, RUNNING, SUCCESS, FAILED
    rows_processed: int = Field(default=0)
    error_message: Optional[str] = None


# ==========================================
# DTOs - Pipeline
# ==========================================

class PipelineDefCreate(SQLModel):
    """DTO for creating PipelineDef."""
    name: Optional[str] = Field(default=None, max_length=100)
    object_ver_id: str = Field(max_length=36)
    dataset_id: str = Field(max_length=36)
    mode: str = Field(default="VIRTUAL", max_length=50)
    transform_rules: Optional[Dict[str, Any]] = None
    filter_predicate: Optional[str] = None
    sync_schedule: Optional[str] = Field(default=None, max_length=50)
    media_process_config: Optional[Dict[str, Any]] = None
    is_active: bool = True


class PipelineDefUpdate(SQLModel):
    """DTO for updating PipelineDef."""
    name: Optional[str] = Field(default=None, max_length=100)
    mode: Optional[str] = Field(default=None, max_length=50)
    transform_rules: Optional[Dict[str, Any]] = None
    filter_predicate: Optional[str] = None
    sync_schedule: Optional[str] = Field(default=None, max_length=50)
    media_process_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class PipelineDefRead(SQLModel):
    """DTO for reading PipelineDef."""
    id: str
    name: Optional[str]
    object_ver_id: str
    dataset_id: str
    mode: str
    transform_rules: Optional[Dict[str, Any]]
    filter_predicate: Optional[str]
    sync_schedule: Optional[str]
    media_process_config: Optional[Dict[str, Any]]
    is_active: bool
    created_at: Optional[datetime]


class PipelineDefWithDetails(PipelineDefRead):
    """DTO for Pipeline with related entity names."""
    object_type_name: Optional[str] = None
    dataset_name: Optional[str] = None
    last_sync_status: Optional[str] = None
    last_sync_time: Optional[datetime] = None


# ==========================================
# DTOs - Sync Task
# ==========================================

class SyncTaskCreate(SQLModel):
    """DTO for creating SyncTask."""
    pipeline_id: str = Field(max_length=36)
    start_time: datetime
    status: str = Field(default="PENDING", max_length=50)


class SyncTaskUpdate(SQLModel):
    """DTO for updating SyncTask."""
    end_time: Optional[datetime] = None
    status: Optional[str] = Field(default=None, max_length=50)
    rows_processed: Optional[int] = None
    error_message: Optional[str] = None


class SyncTaskRead(SQLModel):
    """DTO for reading SyncTask."""
    id: str
    pipeline_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    rows_processed: int
    error_message: Optional[str]


class SyncTaskWithPipeline(SyncTaskRead):
    """DTO for SyncTask with pipeline info."""
    pipeline_name: Optional[str] = None
    object_type_name: Optional[str] = None
