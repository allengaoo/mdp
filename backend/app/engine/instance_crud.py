"""
CRUD operations for instance models (ObjectInstance, LinkInstance, DataSourceTable).
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, or_
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError

from app.core.logger import logger
from app.models.data import (
    ObjectInstance, LinkInstance,
    DataSourceTable, DataSourceTableCreate, DataSourceTableRead
)


# ==========================================
# Object Instance CRUD
# ==========================================

def create_object(
    session: Session,
    type_id: str,
    properties: Optional[Dict[str, Any]] = None
) -> ObjectInstance:
    """Create a new ObjectInstance."""
    logger.info(f"Creating ObjectInstance of type: {type_id}")
    logger.debug(f"Properties: {properties}")
    
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
        logger.info(f"ObjectInstance created successfully: {db_obj.id} (Type: {type_id})")
        return db_obj
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
    Update ObjectInstance properties using JSON merge.
    
    Args:
        session: Database session
        obj_id: ObjectInstance ID
        properties_patch: Dictionary of properties to merge (not replace)
        
    Returns:
        Updated ObjectInstance or None if not found
    """
    logger.info(f"Updating ObjectInstance: {obj_id}")
    logger.info(f"Updated Object {obj_id} | Patch: {properties_patch}")
    
    try:
        db_obj = session.get(ObjectInstance, obj_id)
        if not db_obj:
            logger.warning(f"ObjectInstance not found: {obj_id}")
            return None
        
        # Perform JSON merge: existing_data.update(new_data)
        existing_properties = db_obj.properties or {}
        existing_properties.update(properties_patch)
        db_obj.properties = existing_properties
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"ObjectInstance updated successfully: {obj_id}")
        logger.debug(f"Updated properties: {db_obj.properties}")
        return db_obj
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update ObjectInstance {obj_id}: {str(e)}")
        raise


def delete_object(session: Session, obj_id: str) -> bool:
    """Delete ObjectInstance by ID."""
    logger.info(f"Deleting ObjectInstance: {obj_id}")
    
    try:
        db_obj = session.get(ObjectInstance, obj_id)
        if not db_obj:
            logger.warning(f"ObjectInstance not found: {obj_id}")
            return False
        
        session.delete(db_obj)
        session.commit()
        logger.info(f"ObjectInstance deleted successfully: {obj_id}")
        return True
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
    """List all DataSourceTables."""
    statement = select(DataSourceTable).offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())


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
