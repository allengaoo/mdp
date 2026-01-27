"""
Sync Job CRUD operations for MDP Platform V3.1
Tables: sys_sync_job_def, sys_sync_run_log
"""
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from app.core.logger import logger
from app.models.system import (
    Connection,
    SyncJobDef,
    SyncJobDefCreate,
    SyncJobDefUpdate,
    SyncJobDefRead,
    SyncJobDefWithConnection,
    SyncRunLog,
    SyncRunLogCreate,
    SyncRunLogRead,
    SyncRunLogWithJob,
)


# ==========================================
# Sync Job Definition CRUD
# ==========================================

def create_sync_job(session: Session, data: SyncJobDefCreate) -> SyncJobDef:
    """Create a new sync job definition."""
    job = SyncJobDef(
        connection_id=data.connection_id,
        name=data.name,
        source_config=data.source_config,
        target_table=data.target_table,
        sync_mode=data.sync_mode,
        schedule_cron=data.schedule_cron,
        is_enabled=data.is_enabled,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    logger.info(f"[SyncJob] Created job: {job.id} ({job.name})")
    return job


def get_sync_job(session: Session, job_id: str) -> Optional[SyncJobDef]:
    """Get sync job by ID."""
    return session.get(SyncJobDef, job_id)


def get_sync_job_with_connection(
    session: Session,
    job_id: str
) -> Optional[SyncJobDefWithConnection]:
    """Get sync job with connection info."""
    job = session.get(SyncJobDef, job_id)
    if not job:
        return None
    
    conn = session.get(Connection, job.connection_id)
    
    return SyncJobDefWithConnection(
        id=job.id,
        connection_id=job.connection_id,
        name=job.name,
        source_config=job.source_config,
        target_table=job.target_table,
        sync_mode=job.sync_mode,
        schedule_cron=job.schedule_cron,
        is_enabled=job.is_enabled,
        last_run_status=job.last_run_status,
        last_run_at=job.last_run_at,
        rows_synced=job.rows_synced,
        created_at=job.created_at,
        updated_at=job.updated_at,
        connection_name=conn.name if conn else None,
        connection_type=conn.conn_type if conn else None,
    )


def list_sync_jobs(
    session: Session,
    connection_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[SyncJobDef]:
    """List sync jobs, optionally filtered by connection."""
    stmt = select(SyncJobDef)
    if connection_id:
        stmt = stmt.where(SyncJobDef.connection_id == connection_id)
    stmt = stmt.offset(skip).limit(limit)
    return list(session.exec(stmt).all())


def list_sync_jobs_with_connection(
    session: Session,
    connection_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[SyncJobDefWithConnection]:
    """List sync jobs with connection info."""
    jobs = list_sync_jobs(session, connection_id, skip, limit)
    results = []
    
    for job in jobs:
        conn = session.get(Connection, job.connection_id)
        results.append(SyncJobDefWithConnection(
            id=job.id,
            connection_id=job.connection_id,
            name=job.name,
            source_config=job.source_config,
            target_table=job.target_table,
            sync_mode=job.sync_mode,
            schedule_cron=job.schedule_cron,
            is_enabled=job.is_enabled,
            last_run_status=job.last_run_status,
            last_run_at=job.last_run_at,
            rows_synced=job.rows_synced,
            created_at=job.created_at,
            updated_at=job.updated_at,
            connection_name=conn.name if conn else None,
            connection_type=conn.conn_type if conn else None,
        ))
    
    return results


def update_sync_job(
    session: Session,
    job_id: str,
    data: SyncJobDefUpdate
) -> Optional[SyncJobDef]:
    """Update sync job definition."""
    job = session.get(SyncJobDef, job_id)
    if not job:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)
    
    job.updated_at = datetime.utcnow()
    session.add(job)
    session.commit()
    session.refresh(job)
    logger.info(f"[SyncJob] Updated job: {job_id}")
    return job


def delete_sync_job(session: Session, job_id: str) -> bool:
    """Delete sync job definition."""
    job = session.get(SyncJobDef, job_id)
    if not job:
        return False
    
    session.delete(job)
    session.commit()
    logger.info(f"[SyncJob] Deleted job: {job_id}")
    return True


def update_job_run_status(
    session: Session,
    job_id: str,
    status: str,
    rows_synced: Optional[int] = None
) -> Optional[SyncJobDef]:
    """Update job after a run completes."""
    job = session.get(SyncJobDef, job_id)
    if not job:
        return None
    
    job.last_run_status = status
    job.last_run_at = datetime.utcnow()
    if rows_synced is not None:
        job.rows_synced = rows_synced
    job.updated_at = datetime.utcnow()
    
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


# ==========================================
# Sync Run Log CRUD
# ==========================================

def create_run_log(
    session: Session,
    job_id: str,
    triggered_by: str = "MANUAL"
) -> SyncRunLog:
    """Create a new run log entry."""
    log = SyncRunLog(
        job_id=job_id,
        start_time=datetime.utcnow(),
        status="RUNNING",
        triggered_by=triggered_by,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    logger.info(f"[SyncRunLog] Created log: {log.id} for job {job_id}")
    return log


def get_run_log(session: Session, log_id: str) -> Optional[SyncRunLog]:
    """Get run log by ID."""
    return session.get(SyncRunLog, log_id)


def list_run_logs(
    session: Session,
    job_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[SyncRunLog]:
    """List run logs, optionally filtered by job."""
    stmt = select(SyncRunLog).order_by(SyncRunLog.start_time.desc())
    if job_id:
        stmt = stmt.where(SyncRunLog.job_id == job_id)
    stmt = stmt.offset(skip).limit(limit)
    return list(session.exec(stmt).all())


def list_run_logs_with_job(
    session: Session,
    job_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[SyncRunLogWithJob]:
    """List run logs with job info."""
    logs = list_run_logs(session, job_id, skip, limit)
    results = []
    
    for log in logs:
        job = session.get(SyncJobDef, log.job_id)
        conn = session.get(Connection, job.connection_id) if job else None
        
        results.append(SyncRunLogWithJob(
            id=log.id,
            job_id=log.job_id,
            start_time=log.start_time,
            end_time=log.end_time,
            duration_ms=log.duration_ms,
            rows_affected=log.rows_affected,
            status=log.status,
            message=log.message,
            triggered_by=log.triggered_by,
            job_name=job.name if job else None,
            connection_name=conn.name if conn else None,
        ))
    
    return results


def complete_run_log(
    session: Session,
    log_id: str,
    status: str,
    rows_affected: Optional[int] = None,
    message: Optional[str] = None
) -> Optional[SyncRunLog]:
    """Complete a run log entry."""
    log = session.get(SyncRunLog, log_id)
    if not log:
        return None
    
    log.end_time = datetime.utcnow()
    log.duration_ms = int((log.end_time - log.start_time).total_seconds() * 1000)
    log.status = status
    log.rows_affected = rows_affected
    log.message = message
    
    session.add(log)
    session.commit()
    session.refresh(log)
    logger.info(f"[SyncRunLog] Completed log: {log_id} with status {status}")
    return log
