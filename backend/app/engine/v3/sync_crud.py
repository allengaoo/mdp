"""
Sync Job CRUD operations for MDP Platform V3.1
Tables: sys_sync_job_def, sys_sync_run_log
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy import create_engine, text, inspect

from app.core.logger import logger
from app.core.config import settings
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
    TargetTableInfo,
    TargetTableListResponse,
)
from app.engine.v3 import mapping_crud, connector_crud


# ==========================================
# Sync Job Definition CRUD
# ==========================================

def check_table_exists_in_raw_store(table_name: str) -> bool:
    """Check if table exists in mdp_raw_store database."""
    try:
        engine = create_engine(settings.raw_store_database_url, pool_pre_ping=True)
        inspector = inspect(engine)
        exists = inspector.has_table(table_name)
        engine.dispose()
        return exists
    except Exception as e:
        logger.error(f"[SyncJob] Failed to check table existence: {e}")
        return False


def create_sync_job(
    session: Session, 
    data: SyncJobDefCreate
) -> Tuple[SyncJobDef, Dict[str, Any]]:
    """
    Create a new sync job definition.
    
    Returns:
        Tuple of (SyncJobDef, warnings_dict)
        warnings_dict contains:
        - mapping_exists: bool - Whether a mapping exists for this connection
        - mapping_table_mismatch: Optional[str] - Existing mapping's table name if different
        - table_exists: bool - Whether target_table exists in raw_store
    """
    warnings: Dict[str, Any] = {
        "mapping_exists": False,
        "mapping_table_mismatch": None,
        "table_exists": False
    }
    
    # 1. Validate target_table exists in raw_store (if sync job has run before)
    # Note: For new sync jobs, table may not exist yet, so we check but don't fail
    warnings["table_exists"] = check_table_exists_in_raw_store(data.target_table)
    if not warnings["table_exists"]:
        logger.info(f"[SyncJob] Target table {data.target_table} does not exist yet (will be created on first sync)")
    
    # 2. Check for existing mappings with same connection_id
    existing_mappings = mapping_crud.list_mappings_by_connection(session, data.connection_id)
    
    if existing_mappings:
        warnings["mapping_exists"] = True
        
        # Check if any mapping has different table name
        for mapping in existing_mappings:
            if mapping.source_table_name != data.target_table:
                warnings["mapping_table_mismatch"] = mapping.source_table_name
                logger.warning(
                    f"[SyncJob] Found existing mapping with different table name: "
                    f"{mapping.source_table_name} != {data.target_table}"
                )
                break
    
    # 3. Get source table schema from connection
    cached_schema = None
    try:
        conn = session.get(Connection, data.connection_id)
        if conn and "table" in data.source_config:
            source_table_name = data.source_config["table"]
            # Explore source to get table schema
            explorer_result = connector_crud.explore_source(conn.conn_type, conn.config_json)
            # Find the table in explorer results
            for table_info in explorer_result.tables:
                if table_info.name == source_table_name:
                    # Convert columns to schema format
                    cached_schema = {
                        "columns": [
                            {
                                "name": col["name"],
                                "type": col["type"],
                                "nullable": col.get("nullable", True)
                            }
                            for col in (table_info.columns or [])
                        ]
                    }
                    logger.info(f"[SyncJob] Cached schema for source table {source_table_name}: {len(cached_schema['columns'])} columns")
                    break
            if not cached_schema:
                logger.warning(f"[SyncJob] Source table {source_table_name} not found in explorer results")
    except Exception as e:
        logger.warning(f"[SyncJob] Failed to get source table schema: {e}")
        # Continue without schema - can be updated later
    
    # 4. Create sync job
    job = SyncJobDef(
        connection_id=data.connection_id,
        name=data.name,
        source_config=data.source_config,
        target_table=data.target_table,
        sync_mode=data.sync_mode,
        schedule_cron=data.schedule_cron,
        is_enabled=data.is_enabled,
        cached_schema=cached_schema,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    logger.info(f"[SyncJob] Created job: {job.id} ({job.name})")
    
    return job, warnings


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
            cached_schema=job.cached_schema,
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


# ==========================================
# Target Tables (for Object Type binding)
# ==========================================

def get_target_table_columns(table_name: str) -> Optional[List[Dict[str, Any]]]:
    """Get column schema for a target table in mdp_raw_store."""
    try:
        engine = create_engine(settings.raw_store_database_url, pool_pre_ping=True)
        inspector = inspect(engine)
        
        if not inspector.has_table(table_name):
            engine.dispose()
            return None
        
        columns = inspector.get_columns(table_name)
        result = []
        for col in columns:
            result.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
            })
        
        engine.dispose()
        return result
    except Exception as e:
        logger.error(f"[SyncJob] Failed to get table columns for {table_name}: {e}")
        return None


def list_target_tables(
    session: Session,
    include_columns: bool = False,
    only_synced: bool = False
) -> TargetTableListResponse:
    """
    List all target tables from sync jobs.
    
    Args:
        session: Database session
        include_columns: If True, include column schema from mdp_raw_store
        only_synced: If True, only return tables that have been successfully synced
    
    Returns:
        TargetTableListResponse with list of target tables
    """
    # Get all sync jobs
    stmt = select(SyncJobDef)
    if only_synced:
        stmt = stmt.where(SyncJobDef.last_run_status == "SUCCESS")
    
    jobs = list(session.exec(stmt).all())
    
    # Build result list with unique target tables
    seen_tables = set()
    tables = []
    
    for job in jobs:
        # Skip duplicates (same target_table)
        if job.target_table in seen_tables:
            continue
        seen_tables.add(job.target_table)
        
        # Get connection info
        conn = session.get(Connection, job.connection_id)
        
        # Get column schema if requested
        columns = None
        if include_columns:
            # Priority 1: Use cached schema from sync job definition
            if job.cached_schema and "columns" in job.cached_schema:
                columns = job.cached_schema["columns"]
                logger.debug(f"[SyncJob] Using cached schema for {job.target_table}: {len(columns)} columns")
            else:
                # Priority 2: Query from mdp_raw_store (table might have been synced)
                columns = get_target_table_columns(job.target_table)
                if columns:
                    logger.debug(f"[SyncJob] Retrieved schema from mdp_raw_store for {job.target_table}: {len(columns)} columns")
                else:
                    logger.warning(f"[SyncJob] No schema available for {job.target_table} (not cached and table doesn't exist)")
        
        tables.append(TargetTableInfo(
            target_table=job.target_table,
            connection_id=job.connection_id,
            connection_name=conn.name if conn else "Unknown",
            sync_job_id=job.id,
            sync_job_name=job.name,
            last_sync_status=job.last_run_status,
            last_sync_at=job.last_run_at,
            rows_synced=job.rows_synced,
            columns=columns,
        ))
    
    return TargetTableListResponse(tables=tables, total=len(tables))
