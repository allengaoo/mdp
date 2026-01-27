"""
Sync Worker - ETL Engine for MDP Platform V3.1
Handles data synchronization from external sources to mdp_raw_store.
"""
import traceback
from typing import Optional, Dict, Any
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import settings
from app.core.logger import logger
from app.core.db import get_session_context
from app.engine.v3 import connector_crud, sync_crud


def _get_raw_store_engine() -> Engine:
    """Get SQLAlchemy engine for raw store database."""
    return create_engine(settings.raw_store_database_url, pool_pre_ping=True)


def _get_source_engine(conn_type: str, config: Dict[str, Any]) -> Engine:
    """Get SQLAlchemy engine for source database."""
    conn_string = connector_crud._build_connection_string(conn_type, config)
    return create_engine(conn_string, pool_pre_ping=True)


def _standardize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize dataframe columns and add metadata.
    
    - Lowercase column names
    - Add _sync_timestamp column
    """
    # Lowercase column names
    df.columns = [col.lower() for col in df.columns]
    
    # Add sync timestamp
    df['_sync_timestamp'] = datetime.utcnow()
    
    return df


def _sync_mysql_table(
    source_engine: Engine,
    target_engine: Engine,
    source_config: Dict[str, Any],
    target_table: str,
    sync_mode: str,
    chunk_size: int = 10000
) -> int:
    """
    Sync data from MySQL/Postgres table to raw store.
    
    Returns: Number of rows synced
    """
    source_table = source_config.get("table")
    source_schema = source_config.get("schema")
    source_query = source_config.get("query")
    
    if source_query:
        # Custom SQL query
        query = source_query
    elif source_schema:
        query = f"SELECT * FROM {source_schema}.{source_table}"
    else:
        query = f"SELECT * FROM {source_table}"
    
    logger.info(f"[SyncWorker] Extracting data with query: {query[:100]}...")
    
    total_rows = 0
    first_chunk = True
    
    # Read in chunks for memory safety
    for chunk_df in pd.read_sql(query, source_engine, chunksize=chunk_size):
        # Transform
        chunk_df = _standardize_dataframe(chunk_df)
        
        # Determine write mode
        if first_chunk:
            if sync_mode == "FULL_OVERWRITE":
                # Drop and recreate table
                if_exists = "replace"
            else:
                # Append mode
                if_exists = "append"
            first_chunk = False
        else:
            # Always append subsequent chunks
            if_exists = "append"
        
        # Load to target
        chunk_df.to_sql(
            name=target_table,
            con=target_engine,
            if_exists=if_exists,
            index=False
        )
        
        total_rows += len(chunk_df)
        logger.info(f"[SyncWorker] Loaded {total_rows} rows to {target_table}")
    
    return total_rows


def run_sync_job(job_id: str, run_log_id: str):
    """
    Execute a sync job.
    
    This function is designed to be called as a background task.
    It handles the full ETL process and updates the run log.
    """
    logger.info(f"[SyncWorker] Starting job {job_id}, log {run_log_id}")
    
    rows_affected = 0
    error_message = None
    status = "SUCCESS"
    
    try:
        with get_session_context() as session:
            # Get job definition
            job = sync_crud.get_sync_job(session, job_id)
            if not job:
                raise ValueError(f"Job not found: {job_id}")
            
            # Get connection
            conn = connector_crud.get_connection(session, job.connection_id)
            if not conn:
                raise ValueError(f"Connection not found: {job.connection_id}")
            
            logger.info(f"[SyncWorker] Job: {job.name}, Connection: {conn.name} ({conn.conn_type})")
            
            # Get engines
            target_engine = _get_raw_store_engine()
            
            if conn.conn_type in ("MYSQL", "POSTGRES"):
                source_engine = _get_source_engine(conn.conn_type, conn.config_json)
                
                rows_affected = _sync_mysql_table(
                    source_engine=source_engine,
                    target_engine=target_engine,
                    source_config=job.source_config,
                    target_table=job.target_table,
                    sync_mode=job.sync_mode,
                )
                
                source_engine.dispose()
                
            elif conn.conn_type == "S3":
                # TODO: Implement S3 sync with boto3 + pandas
                raise NotImplementedError("S3 sync not yet implemented")
                
            elif conn.conn_type == "KAFKA":
                # TODO: Implement Kafka consumer sync
                raise NotImplementedError("Kafka sync not yet implemented")
                
            elif conn.conn_type == "REST_API":
                # TODO: Implement REST API polling sync
                raise NotImplementedError("REST API sync not yet implemented")
                
            else:
                raise ValueError(f"Unsupported connection type: {conn.conn_type}")
            
            target_engine.dispose()
            
            logger.info(f"[SyncWorker] Job {job_id} completed. Rows synced: {rows_affected}")
            
    except Exception as e:
        status = "FAILED"
        error_message = f"{str(e)}\n{traceback.format_exc()}"
        logger.error(f"[SyncWorker] Job {job_id} failed: {e}")
    
    # Update run log
    try:
        with get_session_context() as session:
            sync_crud.complete_run_log(
                session,
                run_log_id,
                status=status,
                rows_affected=rows_affected,
                message=error_message
            )
            
            # Update job status
            sync_crud.update_job_run_status(
                session,
                job_id,
                status=status,
                rows_synced=rows_affected if status == "SUCCESS" else None
            )
    except Exception as e:
        logger.error(f"[SyncWorker] Failed to update run log: {e}")


def preview_sync_data(
    conn_type: str,
    config: Dict[str, Any],
    source_config: Dict[str, Any],
    limit: int = 100
) -> Dict[str, Any]:
    """
    Preview data from source without syncing.
    
    Returns: {"columns": [...], "data": [...], "total_rows": int}
    """
    try:
        if conn_type in ("MYSQL", "POSTGRES"):
            engine = _get_source_engine(conn_type, config)
            
            source_table = source_config.get("table")
            source_query = source_config.get("query")
            
            if source_query:
                query = f"SELECT * FROM ({source_query}) AS subq LIMIT {limit}"
            else:
                query = f"SELECT * FROM {source_table} LIMIT {limit}"
            
            df = pd.read_sql(query, engine)
            
            # Get total count
            if source_query:
                count_query = f"SELECT COUNT(*) FROM ({source_query}) AS subq"
            else:
                count_query = f"SELECT COUNT(*) FROM {source_table}"
            
            with engine.connect() as conn:
                total_rows = conn.execute(text(count_query)).scalar()
            
            engine.dispose()
            
            return {
                "columns": list(df.columns),
                "data": df.to_dict(orient="records"),
                "total_rows": total_rows
            }
        else:
            return {"error": f"Preview not supported for {conn_type}"}
            
    except Exception as e:
        logger.error(f"[SyncWorker] Preview failed: {e}")
        return {"error": str(e)}
