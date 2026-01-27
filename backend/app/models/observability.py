"""
Observability Models for MDP Platform V3.1
Tables: sys_index_job_run, sys_index_error_sample
Purpose: Monitor indexing pipeline health and capture errors
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON


# ==========================================
# Enums
# ==========================================

class JobStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"


class ErrorCategory(str, Enum):
    SEMANTIC = "SEMANTIC"           # PK collisions, data type mismatch
    AI_INFERENCE = "AI_INFERENCE"   # Model errors, low confidence
    MEDIA_IO = "MEDIA_IO"           # Corrupt files, S3 errors
    SYSTEM = "SYSTEM"               # DB errors, network issues


# ==========================================
# ORM Models
# ==========================================

class IndexJobRun(SQLModel, table=True):
    """Index job run record with metrics."""
    __tablename__ = "sys_index_job_run"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    mapping_id: str = Field(max_length=36, index=True)
    object_def_id: str = Field(max_length=36, index=True)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: str = Field(default="SUCCESS", max_length=20)
    rows_processed: int = Field(default=0)
    rows_indexed: int = Field(default=0)
    metrics_json: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class IndexErrorSample(SQLModel, table=True):
    """Error sample for debugging (Dead Letter Queue)."""
    __tablename__ = "sys_index_error_sample"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    job_run_id: str = Field(max_length=36, index=True)
    raw_row_id: str = Field(max_length=100)
    error_category: str = Field(max_length=20)
    error_message: str = Field(max_length=2000)
    stack_trace: Optional[str] = Field(default=None, max_length=5000)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# ==========================================
# DTOs - Index Job Run
# ==========================================

class IndexJobRunCreate(SQLModel):
    """DTO for creating job run record."""
    mapping_id: str
    object_def_id: str
    status: str = "SUCCESS"
    rows_processed: int = 0
    rows_indexed: int = 0
    metrics_json: Dict[str, Any] = {}


class IndexJobRunRead(SQLModel):
    """DTO for reading job run record."""
    id: str
    mapping_id: str
    object_def_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    rows_processed: int
    rows_indexed: int
    metrics_json: Dict[str, Any]
    created_at: Optional[datetime]


# ==========================================
# DTOs - Index Error Sample
# ==========================================

class IndexErrorSampleCreate(SQLModel):
    """DTO for creating error sample."""
    job_run_id: str
    raw_row_id: str
    error_category: str
    error_message: str
    stack_trace: Optional[str] = None


class IndexErrorSampleRead(SQLModel):
    """DTO for reading error sample."""
    id: str
    job_run_id: str
    raw_row_id: str
    error_category: str
    error_message: str
    stack_trace: Optional[str]
    created_at: Optional[datetime]


# ==========================================
# DTOs - Health Summary
# ==========================================

class ObjectHealthSummary(SQLModel):
    """Health summary for a single object type."""
    object_def_id: str
    object_name: Optional[str] = None
    status: str  # HEALTHY, DEGRADED, FAILED
    last_run_time: Optional[datetime] = None
    lag_seconds: Optional[int] = None
    rows_processed: int = 0
    rows_indexed: int = 0
    success_rate: float = 100.0
    metrics: Dict[str, Any] = {}


class SystemHealthSummary(SQLModel):
    """Overall system health metrics."""
    total_objects: int = 0
    healthy_count: int = 0
    degraded_count: int = 0
    failed_count: int = 0
    overall_success_rate: float = 100.0
    avg_ai_latency_ms: Optional[float] = None
    total_corrupt_files: int = 0
    objects: List[ObjectHealthSummary] = []


class JobHistoryResponse(SQLModel):
    """Response for job history query."""
    object_def_id: str
    runs: List[IndexJobRunRead] = []
