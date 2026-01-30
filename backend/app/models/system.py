"""
System Layer Models for MDP Platform V3.1
Tables: sys_project, sys_connection, sys_dataset
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Column, JSON


# ==========================================
# ORM Models - System Layer
# ==========================================

class Project(SQLModel, table=True):
    """Project/Workspace definition.
    
    Projects serve as the context for applications and object bindings.
    Maps to table: sys_project
    """
    __tablename__ = "sys_project"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, sa_column=Column("description"))
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class Connection(SQLModel, table=True):
    """External data source connection configuration.
    
    Supports: MYSQL, POSTGRES, S3, REST_API, KAFKA, ELASTICSEARCH
    Maps to table: sys_connection
    """
    __tablename__ = "sys_connection"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    name: str = Field(max_length=100)
    conn_type: str = Field(max_length=50)  # MYSQL, POSTGRES, S3, REST_API, KAFKA, ELASTICSEARCH
    config_json: Dict[str, Any] = Field(sa_column=Column(JSON))
    status: str = Field(default="ACTIVE", max_length=20)  # ACTIVE, ERROR, TESTING
    error_message: Optional[str] = Field(default=None, max_length=500)
    last_tested_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class Dataset(SQLModel, table=True):
    """Dataset definition pointing to specific data table/file/API.
    
    Maps to table: sys_dataset
    """
    __tablename__ = "sys_dataset"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    connection_id: str = Field(foreign_key="sys_connection.id", max_length=36)
    name: str = Field(max_length=100)
    location_config: Dict[str, Any] = Field(sa_column=Column(JSON))  # table name / S3 path / API endpoint
    cached_schema: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


# ==========================================
# DTOs - Project
# ==========================================

class ProjectCreate(SQLModel):
    """DTO for creating Project."""
    name: str = Field(max_length=100)
    description: Optional[str] = None


class ProjectUpdate(SQLModel):
    """DTO for updating Project."""
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None


class ProjectRead(SQLModel):
    """DTO for reading Project."""
    id: str
    name: str
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class ProjectWithStats(ProjectRead):
    """DTO for Project with aggregated statistics."""
    object_count: int = 0
    link_count: int = 0


# ==========================================
# DTOs - Connection
# ==========================================

class ConnectionCreate(SQLModel):
    """DTO for creating Connection."""
    name: str = Field(max_length=100)
    conn_type: str = Field(max_length=50)
    config_json: Dict[str, Any]


class ConnectionUpdate(SQLModel):
    """DTO for updating Connection."""
    name: Optional[str] = Field(default=None, max_length=100)
    conn_type: Optional[str] = Field(default=None, max_length=50)
    config_json: Optional[Dict[str, Any]] = None


class ConnectionRead(SQLModel):
    """DTO for reading Connection."""
    id: str
    name: str
    conn_type: str
    config_json: Dict[str, Any]
    status: str
    error_message: Optional[str]
    last_tested_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class ConnectionSummary(SQLModel):
    """DTO for connection list display (without sensitive config)."""
    id: str
    name: str
    conn_type: str
    status: str
    last_tested_at: Optional[datetime]
    created_at: Optional[datetime]


class ConnectionTestRequest(SQLModel):
    """DTO for testing connection without saving."""
    conn_type: str = Field(max_length=50)
    config_json: Dict[str, Any]


class ConnectionTestResponse(SQLModel):
    """DTO for connection test result."""
    success: bool
    message: str
    latency_ms: Optional[int] = None


# ==========================================
# DTOs - Dataset
# ==========================================

class DatasetCreate(SQLModel):
    """DTO for creating Dataset."""
    connection_id: str = Field(max_length=36)
    name: str = Field(max_length=100)
    location_config: Dict[str, Any]
    cached_schema: Optional[Dict[str, Any]] = None


class DatasetUpdate(SQLModel):
    """DTO for updating Dataset."""
    name: Optional[str] = Field(default=None, max_length=100)
    location_config: Optional[Dict[str, Any]] = None
    cached_schema: Optional[Dict[str, Any]] = None


class DatasetRead(SQLModel):
    """DTO for reading Dataset."""
    id: str
    connection_id: str
    name: str
    location_config: Dict[str, Any]
    cached_schema: Optional[Dict[str, Any]]


class DatasetWithConnection(DatasetRead):
    """DTO for Dataset with connection info."""
    connection_name: Optional[str] = None
    connection_type: Optional[str] = None


# ==========================================
# ORM Models - Sync Job Definition
# ==========================================

class SyncJobDef(SQLModel, table=True):
    """Sync job definition - defines what to sync and how.
    
    Maps to table: sys_sync_job_def
    """
    __tablename__ = "sys_sync_job_def"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    connection_id: str = Field(foreign_key="sys_connection.id", max_length=36, index=True)
    name: str = Field(max_length=100)
    source_config: Dict[str, Any] = Field(sa_column=Column(JSON))  # {"table": "users"} or {"topic": "events"}
    target_table: str = Field(max_length=100)  # Table name in mdp_raw_store, e.g., raw_conn1_users
    sync_mode: str = Field(default="FULL_OVERWRITE", max_length=50)  # FULL_OVERWRITE, INCREMENTAL
    schedule_cron: Optional[str] = Field(default=None, max_length=100)  # e.g., "0 0 * * *"
    is_enabled: bool = Field(default=True)
    last_run_status: Optional[str] = Field(default=None, max_length=20)  # SUCCESS, FAILED, RUNNING
    last_run_at: Optional[datetime] = Field(default=None)
    rows_synced: Optional[int] = Field(default=None)
    cached_schema: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))  # Column schema from source table
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# ==========================================
# DTOs - Sync Job Definition
# ==========================================

class SyncJobDefCreate(SQLModel):
    """DTO for creating SyncJobDef."""
    connection_id: str = Field(max_length=36)
    name: str = Field(max_length=100)
    source_config: Dict[str, Any]
    target_table: str = Field(max_length=100)
    sync_mode: str = Field(default="FULL_OVERWRITE", max_length=50)
    schedule_cron: Optional[str] = Field(default=None, max_length=100)
    is_enabled: bool = True


class SyncJobDefUpdate(SQLModel):
    """DTO for updating SyncJobDef."""
    name: Optional[str] = Field(default=None, max_length=100)
    source_config: Optional[Dict[str, Any]] = None
    target_table: Optional[str] = Field(default=None, max_length=100)
    sync_mode: Optional[str] = Field(default=None, max_length=50)
    schedule_cron: Optional[str] = None
    is_enabled: Optional[bool] = None


class SyncJobDefRead(SQLModel):
    """DTO for reading SyncJobDef."""
    id: str
    connection_id: str
    name: str
    source_config: Dict[str, Any]
    target_table: str
    sync_mode: str
    schedule_cron: Optional[str]
    is_enabled: bool
    last_run_status: Optional[str]
    last_run_at: Optional[datetime]
    rows_synced: Optional[int]
    cached_schema: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class SyncJobDefCreateResponse(SQLModel):
    """Response DTO for creating SyncJobDef with warnings."""
    job: SyncJobDefRead
    warnings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "mapping_exists": False,
            "mapping_table_mismatch": None,
            "table_exists": False
        }
    )


class SyncJobDefWithConnection(SyncJobDefRead):
    """DTO for SyncJobDef with connection info."""
    connection_name: Optional[str] = None
    connection_type: Optional[str] = None


# ==========================================
# ORM Models - Sync Run Log
# ==========================================

class SyncRunLog(SQLModel, table=True):
    """Sync execution history - audit trail for debugging.
    
    Maps to table: sys_sync_run_log
    """
    __tablename__ = "sys_sync_run_log"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    job_id: str = Field(foreign_key="sys_sync_job_def.id", max_length=36, index=True)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(default=None)
    duration_ms: Optional[int] = Field(default=None)
    rows_affected: Optional[int] = Field(default=None)
    status: str = Field(default="RUNNING", max_length=20)  # RUNNING, SUCCESS, FAILED
    message: Optional[str] = Field(default=None)  # Error trace or success summary
    triggered_by: str = Field(default="MANUAL", max_length=50)  # MANUAL, SCHEDULE, API


# ==========================================
# DTOs - Sync Run Log
# ==========================================

class SyncRunLogCreate(SQLModel):
    """DTO for creating SyncRunLog."""
    job_id: str = Field(max_length=36)
    triggered_by: str = Field(default="MANUAL", max_length=50)


class SyncRunLogRead(SQLModel):
    """DTO for reading SyncRunLog."""
    id: str
    job_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[int]
    rows_affected: Optional[int]
    status: str
    message: Optional[str]
    triggered_by: str


class SyncRunLogWithJob(SyncRunLogRead):
    """DTO for SyncRunLog with job info."""
    job_name: Optional[str] = None
    connection_name: Optional[str] = None


# ==========================================
# DTOs - Source Explorer
# ==========================================

class SourceTableInfo(SQLModel):
    """DTO for source table metadata."""
    name: str
    schema_name: Optional[str] = None
    columns: Optional[List[Dict[str, Any]]] = None
    row_count: Optional[int] = None


class SourceExplorerResponse(SQLModel):
    """DTO for source explorer results."""
    connection_id: str
    conn_type: str
    tables: List[SourceTableInfo] = []
    schemas: Optional[List[str]] = None
    error: Optional[str] = None


# ==========================================
# DTOs - Target Tables (for Object Type binding)
# ==========================================

class TargetTableInfo(SQLModel):
    """DTO for target table info (from sync jobs)."""
    target_table: str
    connection_id: str
    connection_name: str
    sync_job_id: str
    sync_job_name: str
    last_sync_status: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    rows_synced: Optional[int] = None
    columns: Optional[List[Dict[str, Any]]] = None  # Column schema from mdp_raw_store


class TargetTableListResponse(SQLModel):
    """DTO for list of target tables."""
    tables: List[TargetTableInfo] = []
    total: int = 0
