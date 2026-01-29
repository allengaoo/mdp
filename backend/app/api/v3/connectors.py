"""
V3.1 API - Connectors & Sync Jobs
Endpoints for data connection management and synchronization
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlmodel import Session

from app.core.db import get_session
from app.core.logger import logger
from app.models.system import (
    # Connection
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionRead,
    ConnectionSummary,
    ConnectionTestRequest,
    ConnectionTestResponse,
    SourceExplorerResponse,
    # Sync Job
    SyncJobDefCreate,
    SyncJobDefUpdate,
    SyncJobDefRead,
    SyncJobDefWithConnection,
    SyncJobDefCreateResponse,
    # Sync Run Log
    SyncRunLogRead,
    SyncRunLogWithJob,
    # Target Tables
    TargetTableListResponse,
)
from app.engine.v3 import connector_crud, sync_crud

router = APIRouter(prefix="/connectors", tags=["Connectors"])


# ==========================================
# Connection CRUD Endpoints
# ==========================================

@router.get("", response_model=List[ConnectionSummary])
def list_connectors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """
    List all connections (summary without sensitive config).
    """
    return connector_crud.list_connections_summary(session, skip=skip, limit=limit)


@router.post("", response_model=ConnectionRead, status_code=status.HTTP_201_CREATED)
def create_connector(
    data: ConnectionCreate,
    session: Session = Depends(get_session)
):
    """
    Create a new connection.
    """
    try:
        return connector_crud.create_connection(session, data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create connection: {str(e)}"
        )


@router.get("/{conn_id}", response_model=ConnectionRead)
def get_connector(
    conn_id: str,
    session: Session = Depends(get_session)
):
    """
    Get connection details by ID.
    """
    conn = connector_crud.get_connection(session, conn_id)
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection not found: {conn_id}"
        )
    return conn


@router.put("/{conn_id}", response_model=ConnectionRead)
def update_connector(
    conn_id: str,
    data: ConnectionUpdate,
    session: Session = Depends(get_session)
):
    """
    Update an existing connection.
    """
    conn = connector_crud.update_connection(session, conn_id, data)
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection not found: {conn_id}"
        )
    return conn


@router.delete("/{conn_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connector(
    conn_id: str,
    session: Session = Depends(get_session)
):
    """
    Delete a connection.
    """
    # Check if there are associated sync jobs
    jobs = sync_crud.list_sync_jobs(session, connection_id=conn_id)
    if jobs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete connection with {len(jobs)} associated sync jobs. Delete jobs first."
        )
    
    success = connector_crud.delete_connection(session, conn_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection not found: {conn_id}"
        )
    return None


# ==========================================
# Connection Testing & Exploration
# ==========================================

@router.post("/test", response_model=ConnectionTestResponse)
def test_connection(
    data: ConnectionTestRequest,
):
    """
    Test connection without saving.
    Use this to validate credentials before creating a connection.
    """
    return connector_crud.test_connection(data.conn_type, data.config_json)


@router.post("/{conn_id}/test", response_model=ConnectionTestResponse)
def test_existing_connection(
    conn_id: str,
    session: Session = Depends(get_session)
):
    """
    Test an existing connection and update its status.
    """
    conn = connector_crud.get_connection(session, conn_id)
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection not found: {conn_id}"
        )
    
    result = connector_crud.test_connection(conn.conn_type, conn.config_json)
    
    # Update connection status
    new_status = "ACTIVE" if result.success else "ERROR"
    error_msg = None if result.success else result.message
    connector_crud.update_connection_status(session, conn_id, new_status, error_msg)
    
    return result


@router.get("/{conn_id}/explorer", response_model=SourceExplorerResponse)
def explore_source(
    conn_id: str,
    session: Session = Depends(get_session)
):
    """
    Explore available tables/resources in the source connection.
    Returns list of tables with column information.
    """
    conn = connector_crud.get_connection(session, conn_id)
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection not found: {conn_id}"
        )
    
    result = connector_crud.explore_source(conn.conn_type, conn.config_json)
    result.connection_id = conn_id
    return result


# ==========================================
# Sync Job Endpoints
# ==========================================

@router.get("/{conn_id}/sync-jobs", response_model=List[SyncJobDefWithConnection])
def list_connection_sync_jobs(
    conn_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """
    List all sync jobs for a specific connection.
    """
    conn = connector_crud.get_connection(session, conn_id)
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection not found: {conn_id}"
        )
    
    return sync_crud.list_sync_jobs_with_connection(session, connection_id=conn_id, skip=skip, limit=limit)


# Sync Job Router (separate prefix)
sync_router = APIRouter(prefix="/sync-jobs", tags=["Sync Jobs"])


@sync_router.get("", response_model=List[SyncJobDefWithConnection])
def list_sync_jobs(
    connection_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """
    List all sync jobs.
    """
    return sync_crud.list_sync_jobs_with_connection(session, connection_id=connection_id, skip=skip, limit=limit)


@sync_router.get("/target-tables", response_model=TargetTableListResponse)
def list_target_tables(
    include_columns: bool = Query(False, description="Include column schema from mdp_raw_store"),
    only_synced: bool = Query(False, description="Only return tables that have been successfully synced"),
    session: Session = Depends(get_session)
):
    """
    List all target tables from sync jobs.
    
    Use this endpoint to get available data sources for binding to object types.
    The target tables are created in mdp_raw_store when sync jobs run.
    """
    return sync_crud.list_target_tables(session, include_columns=include_columns, only_synced=only_synced)


@sync_router.post("", response_model=SyncJobDefCreateResponse, status_code=status.HTTP_201_CREATED)
def create_sync_job(
    data: SyncJobDefCreate,
    session: Session = Depends(get_session)
):
    """
    Create a new sync job definition.
    
    Returns warnings if:
    - Mapping exists for this connection with different table name
    - Target table does not exist in raw_store (will be created on first sync)
    """
    # Verify connection exists
    conn = connector_crud.get_connection(session, data.connection_id)
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection not found: {data.connection_id}"
        )
    
    try:
        job, warnings = sync_crud.create_sync_job(session, data)
        
        # Convert to read model
        job_read = SyncJobDefRead(
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
        )
        
        return SyncJobDefCreateResponse(job=job_read, warnings=warnings)
    except Exception as e:
        logger.error(f"[SyncJob] Failed to create sync job: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create sync job: {str(e)}"
        )


@sync_router.get("/{job_id}", response_model=SyncJobDefWithConnection)
def get_sync_job(
    job_id: str,
    session: Session = Depends(get_session)
):
    """
    Get sync job details.
    """
    job = sync_crud.get_sync_job_with_connection(session, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sync job not found: {job_id}"
        )
    return job


@sync_router.put("/{job_id}", response_model=SyncJobDefRead)
def update_sync_job(
    job_id: str,
    data: SyncJobDefUpdate,
    session: Session = Depends(get_session)
):
    """
    Update sync job definition.
    """
    job = sync_crud.update_sync_job(session, job_id, data)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sync job not found: {job_id}"
        )
    return job


@sync_router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sync_job(
    job_id: str,
    session: Session = Depends(get_session)
):
    """
    Delete sync job definition.
    """
    success = sync_crud.delete_sync_job(session, job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sync job not found: {job_id}"
        )
    return None


@sync_router.post("/{job_id}/run", response_model=SyncRunLogRead)
def trigger_sync_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """
    Trigger immediate execution of a sync job.
    Returns the run log entry for tracking.
    """
    from app.engine.sync_worker import run_sync_job
    
    job = sync_crud.get_sync_job(session, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sync job not found: {job_id}"
        )
    
    if not job.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sync job is disabled"
        )
    
    # Create run log
    run_log = sync_crud.create_run_log(session, job_id, triggered_by="API")
    
    # Add background task
    background_tasks.add_task(run_sync_job, job_id, run_log.id)
    
    return run_log


@sync_router.get("/{job_id}/logs", response_model=List[SyncRunLogWithJob])
def list_job_run_logs(
    job_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: Session = Depends(get_session)
):
    """
    List run history for a specific sync job.
    """
    job = sync_crud.get_sync_job(session, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sync job not found: {job_id}"
        )
    
    return sync_crud.list_run_logs_with_job(session, job_id=job_id, skip=skip, limit=limit)
