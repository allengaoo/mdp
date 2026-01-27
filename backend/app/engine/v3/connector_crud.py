"""
Connector CRUD operations for MDP Platform V3.1
Tables: sys_connection
"""
import time
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.logger import logger
from app.models.system import (
    Connection,
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionRead,
    ConnectionSummary,
    ConnectionTestResponse,
    SourceTableInfo,
    SourceExplorerResponse,
)


# ==========================================
# Connection CRUD
# ==========================================

def create_connection(session: Session, data: ConnectionCreate) -> Connection:
    """Create a new connection."""
    conn = Connection(
        name=data.name,
        conn_type=data.conn_type,
        config_json=data.config_json,
        status="ACTIVE",
    )
    session.add(conn)
    session.commit()
    session.refresh(conn)
    logger.info(f"[Connector] Created connection: {conn.id} ({conn.name})")
    return conn


def get_connection(session: Session, conn_id: str) -> Optional[Connection]:
    """Get connection by ID."""
    return session.get(Connection, conn_id)


def list_connections(
    session: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Connection]:
    """List all connections."""
    stmt = select(Connection).offset(skip).limit(limit)
    return list(session.exec(stmt).all())


def list_connections_summary(
    session: Session,
    skip: int = 0,
    limit: int = 100
) -> List[ConnectionSummary]:
    """List connections with summary info (no sensitive config)."""
    connections = list_connections(session, skip, limit)
    return [
        ConnectionSummary(
            id=c.id,
            name=c.name,
            conn_type=c.conn_type,
            status=c.status,
            last_tested_at=c.last_tested_at,
            created_at=c.created_at,
        )
        for c in connections
    ]


def update_connection(
    session: Session,
    conn_id: str,
    data: ConnectionUpdate
) -> Optional[Connection]:
    """Update an existing connection."""
    conn = session.get(Connection, conn_id)
    if not conn:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(conn, key, value)
    
    conn.updated_at = datetime.utcnow()
    session.add(conn)
    session.commit()
    session.refresh(conn)
    logger.info(f"[Connector] Updated connection: {conn_id}")
    return conn


def delete_connection(session: Session, conn_id: str) -> bool:
    """Delete connection by ID."""
    conn = session.get(Connection, conn_id)
    if not conn:
        return False
    
    session.delete(conn)
    session.commit()
    logger.info(f"[Connector] Deleted connection: {conn_id}")
    return True


def update_connection_status(
    session: Session,
    conn_id: str,
    status: str,
    error_message: Optional[str] = None
) -> Optional[Connection]:
    """Update connection status after test."""
    conn = session.get(Connection, conn_id)
    if not conn:
        return None
    
    conn.status = status
    conn.error_message = error_message
    conn.last_tested_at = datetime.utcnow()
    conn.updated_at = datetime.utcnow()
    session.add(conn)
    session.commit()
    session.refresh(conn)
    return conn


# ==========================================
# Connection Testing
# ==========================================

def _build_connection_string(conn_type: str, config: Dict[str, Any]) -> str:
    """Build SQLAlchemy connection string from config."""
    if conn_type == "MYSQL":
        host = config.get("host", "localhost")
        port = config.get("port", 3306)
        database = config.get("database", "")
        user = config.get("user", "root")
        password = config.get("password", "")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    
    elif conn_type == "POSTGRES":
        host = config.get("host", "localhost")
        port = config.get("port", 5432)
        database = config.get("database", "")
        user = config.get("user", "postgres")
        password = config.get("password", "")
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    
    else:
        raise ValueError(f"Unsupported connection type for SQL: {conn_type}")


def _create_engine_for_config(conn_type: str, config: Dict[str, Any]) -> Engine:
    """Create SQLAlchemy engine for given config."""
    conn_string = _build_connection_string(conn_type, config)
    return create_engine(conn_string, pool_pre_ping=True)


def test_connection(conn_type: str, config: Dict[str, Any]) -> ConnectionTestResponse:
    """
    Test connection without saving.
    Returns success/fail with latency.
    """
    start_time = time.time()
    
    try:
        if conn_type in ("MYSQL", "POSTGRES"):
            engine = _create_engine_for_config(conn_type, config)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            engine.dispose()
            
        elif conn_type == "S3":
            # S3 connection test would use boto3
            # For now, validate config structure
            required = ["bucket", "region"]
            missing = [k for k in required if k not in config]
            if missing:
                return ConnectionTestResponse(
                    success=False,
                    message=f"Missing required S3 config: {missing}"
                )
            # TODO: Implement actual S3 connectivity test with boto3
            
        elif conn_type == "KAFKA":
            # Kafka connection test would use kafka-python
            required = ["bootstrap_servers"]
            missing = [k for k in required if k not in config]
            if missing:
                return ConnectionTestResponse(
                    success=False,
                    message=f"Missing required Kafka config: {missing}"
                )
            # TODO: Implement actual Kafka connectivity test
            
        elif conn_type == "REST_API":
            # REST API test would use requests
            required = ["base_url"]
            missing = [k for k in required if k not in config]
            if missing:
                return ConnectionTestResponse(
                    success=False,
                    message=f"Missing required REST API config: {missing}"
                )
            # TODO: Implement actual REST API ping
            
        else:
            return ConnectionTestResponse(
                success=False,
                message=f"Unsupported connection type: {conn_type}"
            )
        
        latency_ms = int((time.time() - start_time) * 1000)
        return ConnectionTestResponse(
            success=True,
            message="Connection successful",
            latency_ms=latency_ms
        )
        
    except SQLAlchemyError as e:
        logger.error(f"[Connector] Test failed: {e}")
        return ConnectionTestResponse(
            success=False,
            message=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[Connector] Test failed: {e}")
        return ConnectionTestResponse(
            success=False,
            message=f"Connection failed: {str(e)}"
        )


# ==========================================
# Source Explorer
# ==========================================

def explore_source(conn_type: str, config: Dict[str, Any]) -> SourceExplorerResponse:
    """
    Explore available tables/resources in the source.
    """
    response = SourceExplorerResponse(
        connection_id="",  # Will be set by caller
        conn_type=conn_type,
        tables=[]
    )
    
    try:
        if conn_type in ("MYSQL", "POSTGRES"):
            engine = _create_engine_for_config(conn_type, config)
            
            from sqlalchemy import inspect
            inspector = inspect(engine)
            
            # Get schemas (for Postgres) or use default
            if conn_type == "POSTGRES":
                schemas = inspector.get_schema_names()
                response.schemas = [s for s in schemas if s not in ('information_schema', 'pg_catalog')]
            
            # Get table names
            table_names = inspector.get_table_names()
            
            for table_name in table_names:
                # Get columns
                columns = inspector.get_columns(table_name)
                col_info = [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col.get("nullable", True)
                    }
                    for col in columns
                ]
                
                response.tables.append(SourceTableInfo(
                    name=table_name,
                    columns=col_info
                ))
            
            engine.dispose()
            
        elif conn_type == "S3":
            # TODO: List S3 buckets/prefixes using boto3
            response.error = "S3 explorer not yet implemented"
            
        elif conn_type == "KAFKA":
            # TODO: List Kafka topics
            response.error = "Kafka explorer not yet implemented"
            
        elif conn_type == "REST_API":
            # REST API doesn't have browsable structure
            response.error = "REST API has no browsable structure"
            
        else:
            response.error = f"Unsupported type: {conn_type}"
            
    except Exception as e:
        logger.error(f"[Connector] Explorer failed: {e}")
        response.error = str(e)
    
    return response
