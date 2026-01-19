"""
CRUD operations for instance models (ObjectInstance, LinkInstance, DataSourceTable).

IMPORTANT: This module now uses the Ontology-based architecture:
- READ operations: Use sys_object_instance VIEW (backward compatible)
- WRITE operations: Write to physical tables (data_fighter, etc.) via OntologyRepository
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from sqlmodel import Session, select, or_
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError

from app.core.logger import logger
from app.models.data import (
    ObjectInstance, LinkInstance,
    DataSourceTable, DataSourceTableCreate, DataSourceTableRead,
    ExecutionLog, ExecutionLogCreate, ExecutionLogRead
)
from app.engine.ontology_repository import OntologyRepository


# ==========================================
# Object Instance CRUD
# ==========================================

def create_object(
    session: Session,
    type_id: str,
    properties: Optional[Dict[str, Any]] = None
) -> ObjectInstance:
    """
    Create a new ObjectInstance.
    
    NEW ARCHITECTURE: Writes to physical table (e.g., data_fighter) via OntologyRepository,
    then reads back through sys_object_instance view for compatibility.
    """
    logger.info(f"Creating ObjectInstance of type: {type_id}")
    logger.debug(f"Properties: {properties}")
    
    try:
        # Generate instance ID
        instance_id = str(uuid.uuid4())
        
        # Use OntologyRepository to write to physical table
        ontology_repo = OntologyRepository(session)
        sql, params = ontology_repo.build_insert_sql(type_id, properties or {}, instance_id)
        
        # Execute INSERT into physical table
        session.execute(text(sql), params)
        session.commit()
        
        logger.info(f"ObjectInstance created in physical table: {instance_id} (Type: {type_id})")
        
        # Read back through view for compatibility
        # The view automatically serializes physical columns to JSON properties
        db_obj = session.get(ObjectInstance, instance_id)
        
        if not db_obj:
            # Fallback: construct from what we know
            logger.warning(f"Could not read back from view, constructing object manually")
            db_obj = ObjectInstance(
                id=instance_id,
                object_type_id=type_id,
                properties=properties or {},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        logger.info(f"ObjectInstance created successfully: {db_obj.id} (Type: {type_id})")
        return db_obj
        
    except ValueError as e:
        # OntologyRepository couldn't resolve table - fall back to old method for compatibility
        logger.warning(f"Could not resolve physical table for {type_id}, falling back to JSON storage: {e}")
        try:
            now = datetime.now()
            db_obj = ObjectInstance(
                object_type_id=type_id,
                properties=properties or {},
                created_at=now,
                updated_at=now
            )
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            return db_obj
        except Exception as e2:
            session.rollback()
            logger.error(f"Failed to create ObjectInstance (fallback): {str(e2)}")
            raise
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create ObjectInstance: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create ObjectInstance: {str(e)}")
        raise


def get_object(session: Session, obj_id: str) -> Optional[ObjectInstance]:
    """Get ObjectInstance by ID."""
    return session.get(ObjectInstance, obj_id)


def update_object(
    session: Session,
    obj_id: str,
    properties_patch: Dict[str, Any]
) -> Optional[ObjectInstance]:
    """
    Update ObjectInstance properties.
    
    NEW ARCHITECTURE: Updates physical table via OntologyRepository,
    then reads back through sys_object_instance view.
    
    Args:
        session: Database session
        obj_id: ObjectInstance ID
        properties_patch: Dictionary of properties to update (merge, not replace)
        
    Returns:
        Updated ObjectInstance or None if not found
    """
    logger.info(f"Updating ObjectInstance: {obj_id}")
    logger.debug(f"Patch: {properties_patch}")
    
    try:
        # First, get the object to determine its type
        db_obj = session.get(ObjectInstance, obj_id)
        if not db_obj:
            logger.warning(f"ObjectInstance not found: {obj_id}")
            return None
        
        type_id = db_obj.object_type_id
        
        # Use OntologyRepository to update physical table
        ontology_repo = OntologyRepository(session)
        sql, params = ontology_repo.build_update_sql(type_id, obj_id, properties_patch)
        
        # Execute UPDATE on physical table
        result = session.execute(text(sql), params)
        session.commit()
        
        if result.rowcount == 0:
            logger.warning(f"No rows updated for {obj_id}")
            return None
        
        logger.info(f"ObjectInstance updated in physical table: {obj_id}")
        
        # Read back through view for compatibility
        updated_obj = session.get(ObjectInstance, obj_id)
        
        if updated_obj:
            logger.info(f"ObjectInstance updated successfully: {obj_id}")
            logger.debug(f"Updated properties: {updated_obj.properties}")
            return updated_obj
        else:
            logger.warning(f"Could not read back updated object from view")
            return db_obj  # Return original as fallback
        
    except ValueError as e:
        # OntologyRepository couldn't resolve table - fall back to old method
        logger.warning(f"Could not resolve physical table, falling back to JSON storage: {e}")
        try:
            db_obj = session.get(ObjectInstance, obj_id)
            if not db_obj:
                return None
            
            existing_properties = db_obj.properties or {}
            existing_properties.update(properties_patch)
            db_obj.properties = existing_properties
            
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            return db_obj
        except Exception as e2:
            session.rollback()
            logger.error(f"Failed to update ObjectInstance (fallback): {str(e2)}")
            raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update ObjectInstance {obj_id}: {str(e)}")
        raise


def delete_object(session: Session, obj_id: str) -> bool:
    """
    Delete ObjectInstance by ID.
    
    NEW ARCHITECTURE: Deletes from physical table via OntologyRepository.
    """
    logger.info(f"Deleting ObjectInstance: {obj_id}")
    
    try:
        # First, get the object to determine its type
        db_obj = session.get(ObjectInstance, obj_id)
        if not db_obj:
            logger.warning(f"ObjectInstance not found: {obj_id}")
            return False
        
        type_id = db_obj.object_type_id
        
        # Use OntologyRepository to delete from physical table
        ontology_repo = OntologyRepository(session)
        sql, params = ontology_repo.build_delete_sql(type_id, obj_id)
        
        # Execute DELETE on physical table
        result = session.execute(text(sql), params)
        session.commit()
        
        if result.rowcount == 0:
            logger.warning(f"No rows deleted for {obj_id}")
            return False
        
        logger.info(f"ObjectInstance deleted from physical table: {obj_id}")
        return True
        
    except ValueError as e:
        # OntologyRepository couldn't resolve table - fall back to old method
        logger.warning(f"Could not resolve physical table, falling back to direct delete: {e}")
        try:
            db_obj = session.get(ObjectInstance, obj_id)
            if not db_obj:
                return False
            
            session.delete(db_obj)
            session.commit()
            return True
        except Exception as e2:
            session.rollback()
            logger.error(f"Failed to delete ObjectInstance (fallback): {str(e2)}")
            raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete ObjectInstance {obj_id}: {str(e)}")
        raise


def list_objects(
    session: Session,
    type_id: Optional[str] = None,
    filter_criteria: Optional[Dict[str, Any]] = None,
    skip: int = 0,
    limit: int = 100
) -> List[ObjectInstance]:
    """
    List ObjectInstances with optional filtering.
    
    Args:
        session: Database session
        type_id: Optional filter by object_type_id
        filter_criteria: Optional dictionary to filter JSON properties
                        e.g., {"status": "Ready", "fuel": 80}
        skip: Pagination offset
        limit: Pagination limit
        
    Returns:
        List of ObjectInstance objects
    """
    statement = select(ObjectInstance)
    
    # Filter by type_id if provided
    if type_id:
        statement = statement.where(ObjectInstance.object_type_id == type_id)
    
    # Filter by JSON properties if filter_criteria is provided
    if filter_criteria:
        for key, value in filter_criteria.items():
            # MySQL JSON extraction: properties->>'$.key' = value
            # Using SQLAlchemy's JSON extraction for MySQL
            json_path = f'$.{key}'
            json_extract = func.json_extract(ObjectInstance.properties, json_path)
            
            # Handle different value types
            if isinstance(value, str):
                # For strings, use JSON_UNQUOTE to remove quotes from JSON string
                statement = statement.where(
                    func.json_unquote(json_extract) == value
                )
            elif isinstance(value, (int, float)):
                # For numbers, compare directly (JSON_EXTRACT returns the number)
                statement = statement.where(json_extract == value)
            elif isinstance(value, bool):
                # For booleans, compare directly (JSON_EXTRACT returns the boolean)
                statement = statement.where(json_extract == value)
            else:
                # For other types (None, list, dict), use JSON equality
                # Convert to JSON string for comparison
                statement = statement.where(
                    func.cast(json_extract, text('CHAR')) == str(value)
                )
    
    statement = statement.offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())


# ==========================================
# Link Instance CRUD
# ==========================================

def create_link(
    session: Session,
    link_type_id: str,
    source_id: str,
    target_id: str,
    properties: Optional[Dict[str, Any]] = None
) -> LinkInstance:
    """Create a new LinkInstance (edge between objects)."""
    logger.info(f"Creating LinkInstance: {link_type_id} ({source_id} -> {target_id})")
    logger.debug(f"Link properties: {properties}")
    
    try:
        now = datetime.now()
        db_link = LinkInstance(
            link_type_id=link_type_id,
            source_instance_id=source_id,
            target_instance_id=target_id,
            properties=properties or {},
            created_at=now
        )
        session.add(db_link)
        session.commit()
        session.refresh(db_link)
        logger.info(f"LinkInstance created successfully: {db_link.id}")
        return db_link
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create LinkInstance: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create LinkInstance: {str(e)}")
        raise


def get_link(session: Session, link_id: str) -> Optional[LinkInstance]:
    """Get LinkInstance by ID."""
    return session.get(LinkInstance, link_id)


def delete_link(session: Session, link_id: str) -> bool:
    """Delete LinkInstance by ID."""
    logger.info(f"Deleting LinkInstance: {link_id}")
    
    try:
        db_link = session.get(LinkInstance, link_id)
        if not db_link:
            logger.warning(f"LinkInstance not found: {link_id}")
            return False
        
        session.delete(db_link)
        session.commit()
        logger.info(f"LinkInstance deleted successfully: {link_id}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete LinkInstance {link_id}: {str(e)}")
        raise


def get_links_for_object(
    session: Session,
    object_id: str
) -> List[LinkInstance]:
    """
    Get all LinkInstances where the object is source OR target.
    
    Args:
        session: Database session
        object_id: ObjectInstance ID to find links for
        
    Returns:
        List of LinkInstance objects (both incoming and outgoing)
    """
    statement = select(LinkInstance).where(
        or_(
            LinkInstance.source_instance_id == object_id,
            LinkInstance.target_instance_id == object_id
        )
    )
    results = session.exec(statement)
    return list(results.all())


def get_outgoing_links(
    session: Session,
    object_id: str,
    link_type_id: Optional[str] = None
) -> List[LinkInstance]:
    """
    Get LinkInstances where the object is the source.
    
    Args:
        session: Database session
        object_id: ObjectInstance ID (as source)
        link_type_id: Optional filter by link_type_id
        
    Returns:
        List of LinkInstance objects
    """
    statement = select(LinkInstance).where(
        LinkInstance.source_instance_id == object_id
    )
    if link_type_id:
        statement = statement.where(LinkInstance.link_type_id == link_type_id)
    results = session.exec(statement)
    return list(results.all())


def get_incoming_links(
    session: Session,
    object_id: str,
    link_type_id: Optional[str] = None
) -> List[LinkInstance]:
    """
    Get LinkInstances where the object is the target.
    
    Args:
        session: Database session
        object_id: ObjectInstance ID (as target)
        link_type_id: Optional filter by link_type_id
        
    Returns:
        List of LinkInstance objects
    """
    statement = select(LinkInstance).where(
        LinkInstance.target_instance_id == object_id
    )
    if link_type_id:
        statement = statement.where(LinkInstance.link_type_id == link_type_id)
    results = session.exec(statement)
    return list(results.all())


def list_links(
    session: Session,
    source_id: Optional[str] = None,
    target_id: Optional[str] = None,
    link_type_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[LinkInstance]:
    """
    List LinkInstances with optional filtering.
    
    Args:
        session: Database session
        source_id: Optional filter by source_instance_id
        target_id: Optional filter by target_instance_id
        link_type_id: Optional filter by link_type_id
        skip: Pagination offset
        limit: Pagination limit
        
    Returns:
        List of LinkInstance objects
    """
    statement = select(LinkInstance)
    
    # Apply filters
    if source_id:
        statement = statement.where(LinkInstance.source_instance_id == source_id)
    if target_id:
        statement = statement.where(LinkInstance.target_instance_id == target_id)
    if link_type_id:
        statement = statement.where(LinkInstance.link_type_id == link_type_id)
    
    statement = statement.offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())


# ==========================================
# DataSourceTable CRUD
# ==========================================

def create_datasource_table(session: Session, obj_in: DataSourceTableCreate) -> DataSourceTable:
    """Create a new DataSourceTable."""
    logger.info(f"Creating DataSourceTable: {obj_in.table_name}")
    
    try:
        obj_data = obj_in.model_dump()
        # Set created_at to current time if not provided
        if 'created_at' not in obj_data or obj_data['created_at'] is None:
            obj_data['created_at'] = datetime.now()
        db_obj = DataSourceTable(**obj_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"DataSourceTable created successfully: {obj_in.table_name} (ID: {db_obj.id})")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create DataSourceTable {obj_in.table_name}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create DataSourceTable {obj_in.table_name}: {str(e)}")
        raise


def get_datasource_table(session: Session, obj_id: str) -> Optional[DataSourceTable]:
    """Get DataSourceTable by ID."""
    return session.get(DataSourceTable, obj_id)


def get_datasource_table_by_name(session: Session, table_name: str) -> Optional[DataSourceTable]:
    """Get DataSourceTable by table name."""
    statement = select(DataSourceTable).where(DataSourceTable.table_name == table_name)
    result = session.exec(statement)
    return result.first()


def list_datasource_tables(
    session: Session,
    skip: int = 0,
    limit: int = 100
) -> List[DataSourceTable]:
    """
    List all DataSourceTables.
    
    支持两种架构：
    1. 旧架构：直接查询 sys_datasource_table 表
    2. 新架构：查询 sys_datasource_table 视图（映射自 sys_dataset）
    """
    try:
        statement = select(DataSourceTable).offset(skip).limit(limit)
        results = session.exec(statement)
        return list(results.all())
    except Exception as e:
        error_str = str(e)
        # 检查是表不存在还是视图不存在
        if "doesn't exist" in error_str or ("Table" in error_str and "not found" in error_str):
            logger.warning(f"sys_datasource_table not found (table or view), checking architecture: {e}")
            
            # 检查是否是新架构（有 sys_dataset 表）
            try:
                check_new_arch = text("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'sys_dataset'
                """)
                result = session.execute(check_new_arch)
                has_new_arch = result.scalar() > 0
                
                if has_new_arch:
                    # 新架构：创建兼容视图
                    logger.info("Detected new architecture (sys_dataset exists), creating compatibility view...")
                    create_view_sql = text("""
                        CREATE OR REPLACE VIEW `sys_datasource_table` AS
                        SELECT 
                            ds.id,
                            ds.storage_location as table_name,
                            'MySQL' as db_type,
                            (
                                SELECT JSON_ARRAYAGG(
                                    JSON_OBJECT(
                                        'name', dc.column_name,
                                        'type', dc.physical_type,
                                        'is_primary_key', dc.is_primary_key
                                    )
                                )
                                FROM sys_dataset_column dc
                                WHERE dc.dataset_id = ds.id
                            ) as columns_schema,
                            NOW() as created_at
                        FROM sys_dataset ds
                        WHERE ds.storage_type = 'MYSQL_TABLE'
                    """)
                    session.execute(create_view_sql)
                    session.commit()
                    logger.info("Compatibility view sys_datasource_table created successfully")
                else:
                    # 旧架构：创建表
                    logger.info("Detected old architecture, creating sys_datasource_table table...")
                    create_table_sql = text("""
                        CREATE TABLE IF NOT EXISTS `sys_datasource_table` (
                          `id` varchar(36) NOT NULL COMMENT 'UUID',
                          `table_name` varchar(100) NOT NULL COMMENT '原始数据表名',
                          `db_type` varchar(20) DEFAULT 'MySQL' COMMENT '数据库类型',
                          `columns_schema` json COMMENT '存储列定义 [{"name": "id", "type": "int"}, ...]',
                          `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
                          PRIMARY KEY (`id`),
                          UNIQUE KEY `ix_sys_datasource_table_name` (`table_name`)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                    """)
                    session.execute(create_table_sql)
                    session.commit()
                    logger.info("Table sys_datasource_table created successfully")
                
                # 重试查询
                statement = select(DataSourceTable).offset(skip).limit(limit)
                results = session.exec(statement)
                return list(results.all())
                
            except Exception as create_error:
                logger.error(f"Failed to create sys_datasource_table (table/view): {create_error}")
                raise
        else:
            raise


def delete_datasource_table(session: Session, obj_id: str) -> bool:
    """Delete a DataSourceTable."""
    logger.info(f"Deleting DataSourceTable: {obj_id}")
    
    try:
        db_obj = session.get(DataSourceTable, obj_id)
        if not db_obj:
            logger.warning(f"DataSourceTable {obj_id} not found")
            return False
        
        session.delete(db_obj)
        session.commit()
        logger.info(f"DataSourceTable {obj_id} deleted successfully")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete DataSourceTable {obj_id}: {str(e)}")
        raise


# ==========================================
# ExecutionLog CRUD
# ==========================================

def create_execution_log(
    session: Session,
    project_id: str,
    action_def_id: str,
    execution_status: str = "SUCCESS",
    source_object_id: Optional[str] = None,
    duration_ms: Optional[int] = None,
    error_message: Optional[str] = None,
    request_params: Optional[Dict[str, Any]] = None,
) -> ExecutionLog:
    """
    Create a new execution log entry.
    
    Args:
        session: Database session
        project_id: Project ID
        action_def_id: ActionDefinition ID
        execution_status: SUCCESS or FAILED
        source_object_id: Optional source object ID
        duration_ms: Execution duration in milliseconds
        error_message: Error message if failed
        request_params: Request parameters
        
    Returns:
        Created ExecutionLog object
    """
    logger.info(f"Creating execution log: action={action_def_id}, status={execution_status}")
    
    try:
        db_log = ExecutionLog(
            project_id=project_id,
            action_def_id=action_def_id,
            source_object_id=source_object_id,
            execution_status=execution_status,
            duration_ms=duration_ms,
            error_message=error_message,
            request_params=request_params,
            created_at=datetime.now()
        )
        session.add(db_log)
        session.commit()
        session.refresh(db_log)
        logger.info(f"Execution log created: {db_log.id}")
        return db_log
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create execution log: {str(e)}")
        raise


def list_execution_logs(
    session: Session,
    project_id: Optional[str] = None,
    action_def_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[ExecutionLog]:
    """
    List execution logs with optional filters.
    
    Args:
        session: Database session
        project_id: Optional filter by project ID
        action_def_id: Optional filter by action definition ID
        status: Optional filter by execution status
        skip: Pagination offset
        limit: Pagination limit
        
    Returns:
        List of ExecutionLog objects
    """
    statement = select(ExecutionLog)
    
    if project_id:
        statement = statement.where(ExecutionLog.project_id == project_id)
    if action_def_id:
        statement = statement.where(ExecutionLog.action_def_id == action_def_id)
    if status:
        statement = statement.where(ExecutionLog.execution_status == status)
    
    # Order by created_at descending (newest first)
    statement = statement.order_by(ExecutionLog.created_at.desc())
    statement = statement.offset(skip).limit(limit)
    
    results = session.exec(statement)
    return list(results.all())


def get_execution_log(session: Session, log_id: str) -> Optional[ExecutionLog]:
    """Get ExecutionLog by ID."""
    return session.get(ExecutionLog, log_id)