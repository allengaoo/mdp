"""
Health API endpoints for MDP Platform V3.1
Index Health monitoring and observability.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select, func
from sqlalchemy import desc

from app.core.db import get_session
from app.core.logger import logger
from app.models.observability import (
    IndexJobRun,
    IndexErrorSample,
    IndexJobRunRead,
    IndexErrorSampleRead,
    ObjectHealthSummary,
    SystemHealthSummary,
    JobHistoryResponse,
)

router = APIRouter(prefix="/health", tags=["Health"])


# ==========================================
# Health Summary Endpoints
# ==========================================

@router.get("/summary", response_model=SystemHealthSummary)
def get_health_summary(session: Session = Depends(get_session)):
    """
    Get overall system health summary.
    Aggregates latest job runs for all object types.
    """
    # Get latest run for each object_def_id
    subquery = (
        select(
            IndexJobRun.object_def_id,
            func.max(IndexJobRun.start_time).label("latest_time")
        )
        .group_by(IndexJobRun.object_def_id)
        .subquery()
    )
    
    stmt = (
        select(IndexJobRun)
        .join(
            subquery,
            (IndexJobRun.object_def_id == subquery.c.object_def_id) &
            (IndexJobRun.start_time == subquery.c.latest_time)
        )
        .order_by(desc(IndexJobRun.start_time))
    )
    
    latest_runs = session.exec(stmt).all()
    
    # Build object summaries
    objects: List[ObjectHealthSummary] = []
    total_rows_processed = 0
    total_rows_indexed = 0
    total_ai_latency = 0
    ai_latency_count = 0
    total_corrupt_files = 0
    
    for run in latest_runs:
        # Calculate status
        if run.status == "FAILED":
            status = "FAILED"
        elif run.rows_indexed < run.rows_processed:
            status = "DEGRADED"
        else:
            status = "HEALTHY"
        
        # Calculate lag
        lag_seconds = None
        if run.end_time:
            lag_seconds = int((datetime.utcnow() - run.end_time).total_seconds())
        
        # Calculate success rate
        success_rate = 100.0
        if run.rows_processed > 0:
            success_rate = round((run.rows_indexed / run.rows_processed) * 100, 2)
        
        # Extract metrics
        metrics = run.metrics_json or {}
        
        # Accumulate for system totals
        total_rows_processed += run.rows_processed
        total_rows_indexed += run.rows_indexed
        
        if "ai_latency_avg_ms" in metrics:
            total_ai_latency += metrics["ai_latency_avg_ms"]
            ai_latency_count += 1
        
        if "corrupt_media_files" in metrics:
            total_corrupt_files += metrics["corrupt_media_files"]
        
        objects.append(ObjectHealthSummary(
            object_def_id=run.object_def_id,
            object_name=None,  # Can be joined with object type table
            status=status,
            last_run_time=run.end_time or run.start_time,
            lag_seconds=lag_seconds,
            rows_processed=run.rows_processed,
            rows_indexed=run.rows_indexed,
            success_rate=success_rate,
            metrics=metrics
        ))
    
    # Calculate system-level stats
    healthy_count = sum(1 for o in objects if o.status == "HEALTHY")
    degraded_count = sum(1 for o in objects if o.status == "DEGRADED")
    failed_count = sum(1 for o in objects if o.status == "FAILED")
    
    overall_success_rate = 100.0
    if total_rows_processed > 0:
        overall_success_rate = round((total_rows_indexed / total_rows_processed) * 100, 2)
    
    avg_ai_latency = None
    if ai_latency_count > 0:
        avg_ai_latency = round(total_ai_latency / ai_latency_count, 2)
    
    return SystemHealthSummary(
        total_objects=len(objects),
        healthy_count=healthy_count,
        degraded_count=degraded_count,
        failed_count=failed_count,
        overall_success_rate=overall_success_rate,
        avg_ai_latency_ms=avg_ai_latency,
        total_corrupt_files=total_corrupt_files,
        objects=objects
    )


# ==========================================
# Object History Endpoints
# ==========================================

@router.get("/objects/{object_def_id}/history", response_model=JobHistoryResponse)
def get_object_history(
    object_def_id: str,
    days: int = 7,
    limit: int = 50,
    session: Session = Depends(get_session)
):
    """
    Get historical job runs for an object type.
    Used for trend charts (e.g., AI latency over time).
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    stmt = (
        select(IndexJobRun)
        .where(IndexJobRun.object_def_id == object_def_id)
        .where(IndexJobRun.start_time >= since)
        .order_by(desc(IndexJobRun.start_time))
        .limit(limit)
    )
    
    runs = session.exec(stmt).all()
    
    return JobHistoryResponse(
        object_def_id=object_def_id,
        runs=[IndexJobRunRead.model_validate(r) for r in runs]
    )


# ==========================================
# Error Sample Endpoints
# ==========================================

@router.get("/jobs/{run_id}/errors", response_model=List[IndexErrorSampleRead])
def get_job_errors(
    run_id: str,
    category: Optional[str] = None,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    Get error samples for a specific job run.
    Used for debugging failed/degraded runs.
    """
    stmt = select(IndexErrorSample).where(IndexErrorSample.job_run_id == run_id)
    
    if category:
        stmt = stmt.where(IndexErrorSample.error_category == category)
    
    stmt = stmt.order_by(desc(IndexErrorSample.created_at)).limit(limit)
    
    errors = session.exec(stmt).all()
    return [IndexErrorSampleRead.model_validate(e) for e in errors]


# ==========================================
# Reindex Endpoint
# ==========================================

@router.post("/objects/{object_def_id}/reindex")
def trigger_reindex(
    object_def_id: str,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """
    Trigger immediate re-indexing for an object type.
    Finds the latest mapping and starts a new job.
    """
    from app.models.context import ObjectMappingDef
    from app.engine.indexing_worker import run_indexing_job
    
    # Find latest published mapping for this object
    stmt = (
        select(ObjectMappingDef)
        .where(ObjectMappingDef.object_def_id == object_def_id)
        .where(ObjectMappingDef.status == "PUBLISHED")
        .order_by(desc(ObjectMappingDef.updated_at))
        .limit(1)
    )
    
    mapping = session.exec(stmt).first()
    
    if not mapping:
        raise HTTPException(
            status_code=404,
            detail=f"No published mapping found for object: {object_def_id}"
        )
    
    # Trigger background indexing
    background_tasks.add_task(run_indexing_job, mapping.id)
    
    logger.info(f"[Health] Triggered reindex for object: {object_def_id}, mapping: {mapping.id}")
    
    return {
        "message": "Reindex job triggered",
        "object_def_id": object_def_id,
        "mapping_id": mapping.id
    }


# ==========================================
# Job Run Details
# ==========================================

@router.get("/jobs/{run_id}", response_model=IndexJobRunRead)
def get_job_run(
    run_id: str,
    session: Session = Depends(get_session)
):
    """Get details of a specific job run."""
    stmt = select(IndexJobRun).where(IndexJobRun.id == run_id)
    run = session.exec(stmt).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Job run not found")
    
    return IndexJobRunRead.model_validate(run)
