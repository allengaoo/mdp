"""
CRUD operations for meta models (ObjectType, LinkType, FunctionDefinition, ActionDefinition).
"""
from typing import List, Optional, Dict
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.core.logger import logger
from app.models.meta import (
    Project, ProjectCreate, ProjectRead,
    ObjectType, ObjectTypeCreate, ObjectTypeUpdate, ObjectTypeRead,
    LinkType, LinkTypeCreate, LinkTypeUpdate, LinkTypeRead,
    FunctionDefinition, FunctionDefinitionCreate, FunctionDefinitionUpdate, FunctionDefinitionRead,
    ActionDefinition, ActionDefinitionCreate, ActionDefinitionRead,
    SharedProperty, SharedPropertyCreate, SharedPropertyUpdate, SharedPropertyRead
)


# ==========================================
# ObjectType CRUD
# ==========================================

def create_object_type(session: Session, obj_in: ObjectTypeCreate) -> ObjectType:
    """Create a new ObjectType."""
    logger.info(f"Creating ObjectType: {obj_in.api_name}")
    
    try:
        obj_data = obj_in.model_dump()
        # Set created_at and updated_at to current time if not provided
        now = datetime.now()
        if 'created_at' not in obj_data or obj_data['created_at'] is None:
            obj_data['created_at'] = now
        if 'updated_at' not in obj_data or obj_data['updated_at'] is None:
            obj_data['updated_at'] = now
        db_obj = ObjectType(**obj_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"ObjectType created successfully: {obj_in.api_name} (ID: {db_obj.id})")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create ObjectType {obj_in.api_name}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create ObjectType {obj_in.api_name}: {str(e)}")
        raise


def get_object_type(session: Session, obj_id: str) -> Optional[ObjectType]:
    """Get ObjectType by ID."""
    return session.get(ObjectType, obj_id)


def get_object_type_by_name(session: Session, api_name: str) -> Optional[ObjectType]:
    """Get ObjectType by api_name."""
    statement = select(ObjectType).where(ObjectType.api_name == api_name)
    result = session.exec(statement).first()
    return result


def list_object_types(session: Session, skip: int = 0, limit: int = 100) -> List[ObjectType]:
    """List all ObjectTypes with pagination."""
    statement = select(ObjectType).offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())


def update_object_type(
    session: Session,
    obj_id: str,
    obj_in: ObjectTypeUpdate
) -> Optional[ObjectType]:
    """Update an existing ObjectType."""
    logger.info(f"Updating ObjectType: {obj_id}")
    
    try:
        db_obj = session.get(ObjectType, obj_id)
        if not db_obj:
            logger.warning(f"ObjectType not found: {obj_id}")
            return None
        
        # Update fields
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"ObjectType updated successfully: {obj_id}")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to update ObjectType {obj_id}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update ObjectType {obj_id}: {str(e)}")
        raise


def delete_object_type(session: Session, obj_id: str) -> bool:
    """Delete ObjectType by ID."""
    logger.info(f"Deleting ObjectType: {obj_id}")
    
    try:
        db_obj = session.get(ObjectType, obj_id)
        if not db_obj:
            logger.warning(f"ObjectType not found: {obj_id}")
            return False
        
        session.delete(db_obj)
        session.commit()
        logger.info(f"ObjectType deleted successfully: {obj_id}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete ObjectType {obj_id}: {str(e)}")
        raise


# ==========================================
# LinkType CRUD
# ==========================================

def create_link_type(session: Session, obj_in: LinkTypeCreate) -> LinkType:
    """Create a new LinkType."""
    logger.info(f"Creating LinkType: {obj_in.api_name}")
    
    try:
        db_obj = LinkType(**obj_in.model_dump())
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"LinkType created successfully: {obj_in.api_name} (ID: {db_obj.id})")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create LinkType {obj_in.api_name}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create LinkType {obj_in.api_name}: {str(e)}")
        raise


def get_link_type(session: Session, obj_id: str) -> Optional[LinkType]:
    """Get LinkType by ID."""
    return session.get(LinkType, obj_id)


def list_link_types(session: Session, skip: int = 0, limit: int = 100) -> List[LinkType]:
    """List all LinkTypes with pagination."""
    statement = select(LinkType).offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())


def update_link_type(
    session: Session,
    obj_id: str,
    obj_in: LinkTypeUpdate
) -> Optional[LinkType]:
    """Update an existing LinkType."""
    logger.info(f"Updating LinkType: {obj_id}")
    
    try:
        db_obj = session.get(LinkType, obj_id)
        if not db_obj:
            logger.warning(f"LinkType not found: {obj_id}")
            return None
        
        # Update fields
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"LinkType updated successfully: {obj_id}")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to update LinkType {obj_id}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update LinkType {obj_id}: {str(e)}")
        raise


def delete_link_type(session: Session, obj_id: str) -> bool:
    """Delete LinkType by ID."""
    logger.info(f"Deleting LinkType: {obj_id}")
    
    try:
        db_obj = session.get(LinkType, obj_id)
        if not db_obj:
            logger.warning(f"LinkType not found: {obj_id}")
            return False
        
        session.delete(db_obj)
        session.commit()
        logger.info(f"LinkType deleted successfully: {obj_id}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete LinkType {obj_id}: {str(e)}")
        raise


# ==========================================
# FunctionDefinition CRUD
# ==========================================

def create_function_definition(session: Session, obj_in: FunctionDefinitionCreate) -> FunctionDefinition:
    """Create a new FunctionDefinition."""
    logger.info(f"Creating FunctionDefinition: {obj_in.api_name}")
    
    try:
        db_obj = FunctionDefinition(**obj_in.model_dump())
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"FunctionDefinition created successfully: {obj_in.api_name} (ID: {db_obj.id})")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create FunctionDefinition {obj_in.api_name}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create FunctionDefinition {obj_in.api_name}: {str(e)}")
        raise


def get_function_definition(session: Session, obj_id: str) -> Optional[FunctionDefinition]:
    """Get FunctionDefinition by ID."""
    return session.get(FunctionDefinition, obj_id)


def list_function_definitions(session: Session, skip: int = 0, limit: int = 100) -> List[FunctionDefinition]:
    """List all FunctionDefinitions with pagination."""
    statement = select(FunctionDefinition).offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())


def update_function_definition(session: Session, obj_id: str, obj_in: FunctionDefinitionUpdate) -> Optional[FunctionDefinition]:
    """Update an existing FunctionDefinition."""
    logger.info(f"Updating FunctionDefinition: {obj_id}")
    
    try:
        db_obj = session.get(FunctionDefinition, obj_id)
        if not db_obj:
            return None
        
        # Update only provided fields
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"FunctionDefinition updated successfully: {obj_id}")
        return db_obj
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update FunctionDefinition {obj_id}: {str(e)}")
        raise


def delete_function_definition(session: Session, obj_id: str) -> bool:
    """Delete FunctionDefinition by ID."""
    logger.info(f"Deleting FunctionDefinition: {obj_id}")
    
    try:
        db_obj = session.get(FunctionDefinition, obj_id)
        if not db_obj:
            logger.warning(f"FunctionDefinition not found: {obj_id}")
            return False
        
        session.delete(db_obj)
        session.commit()
        logger.info(f"FunctionDefinition deleted successfully: {obj_id}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete FunctionDefinition {obj_id}: {str(e)}")
        raise


# ==========================================
# ActionDefinition CRUD
# ==========================================

def create_action_definition(session: Session, obj_in: ActionDefinitionCreate) -> ActionDefinition:
    """Create a new ActionDefinition."""
    logger.info(f"Creating ActionDefinition: {obj_in.api_name}")
    
    try:
        db_obj = ActionDefinition(**obj_in.model_dump())
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"ActionDefinition created successfully: {obj_in.api_name} (ID: {db_obj.id})")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create ActionDefinition {obj_in.api_name}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create ActionDefinition {obj_in.api_name}: {str(e)}")
        raise


def get_action_definition(session: Session, obj_id: str) -> Optional[ActionDefinition]:
    """Get ActionDefinition by ID."""
    return session.get(ActionDefinition, obj_id)


def get_action_definition_by_name(session: Session, api_name: str) -> Optional[ActionDefinition]:
    """Get ActionDefinition by api_name."""
    statement = select(ActionDefinition).where(ActionDefinition.api_name == api_name)
    result = session.exec(statement).first()
    return result


def list_action_definitions(session: Session, skip: int = 0, limit: int = 100) -> List[ActionDefinition]:
    """List all ActionDefinitions with pagination."""
    statement = select(ActionDefinition).offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())


def delete_action_definition(session: Session, obj_id: str) -> bool:
    """Delete ActionDefinition by ID."""
    logger.info(f"Deleting ActionDefinition: {obj_id}")
    
    try:
        db_obj = session.get(ActionDefinition, obj_id)
        if not db_obj:
            logger.warning(f"ActionDefinition not found: {obj_id}")
            return False
        
        session.delete(db_obj)
        session.commit()
        logger.info(f"ActionDefinition deleted successfully: {obj_id}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete ActionDefinition {obj_id}: {str(e)}")
        raise


# ==========================================
# SharedProperty CRUD
# ==========================================

def create_shared_property(session: Session, obj_in: SharedPropertyCreate) -> SharedProperty:
    """Create a new SharedProperty."""
    logger.info(f"Creating SharedProperty: {obj_in.api_name}")
    
    try:
        obj_data = obj_in.model_dump()
        # Set created_at to current time if not provided
        if 'created_at' not in obj_data or obj_data['created_at'] is None:
            obj_data['created_at'] = datetime.now()
        db_obj = SharedProperty(**obj_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"SharedProperty created successfully: {obj_in.api_name} (ID: {db_obj.id})")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create SharedProperty {obj_in.api_name}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create SharedProperty {obj_in.api_name}: {str(e)}")
        raise


def get_shared_property(session: Session, obj_id: str) -> Optional[SharedProperty]:
    """Get SharedProperty by ID."""
    return session.get(SharedProperty, obj_id)


def get_shared_property_by_name(session: Session, api_name: str, project_id: Optional[str] = None) -> Optional[SharedProperty]:
    """Get SharedProperty by api_name, optionally filtered by project_id."""
    statement = select(SharedProperty).where(SharedProperty.api_name == api_name)
    if project_id:
        statement = statement.where(SharedProperty.project_id == project_id)
    return session.exec(statement).first()


def list_shared_properties(
    session: Session,
    project_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[SharedProperty]:
    """List SharedProperties, optionally filtered by project_id."""
    statement = select(SharedProperty)
    if project_id:
        statement = statement.where(SharedProperty.project_id == project_id)
    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_shared_property(
    session: Session,
    obj_id: str,
    obj_in: SharedPropertyUpdate
) -> Optional[SharedProperty]:
    """Update an existing SharedProperty."""
    logger.info(f"Updating SharedProperty: {obj_id}")
    
    try:
        db_obj = session.get(SharedProperty, obj_id)
        if not db_obj:
            logger.warning(f"SharedProperty not found: {obj_id}")
            return None
        
        # Update fields
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"SharedProperty updated successfully: {obj_id}")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to update SharedProperty {obj_id}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update SharedProperty {obj_id}: {str(e)}")
        raise


def delete_shared_property(session: Session, obj_id: str) -> bool:
    """Delete SharedProperty by ID."""
    logger.info(f"Deleting SharedProperty: {obj_id}")
    
    try:
        db_obj = session.get(SharedProperty, obj_id)
        if not db_obj:
            logger.warning(f"SharedProperty not found: {obj_id}")
            return False
        
        session.delete(db_obj)
        session.commit()
        logger.info(f"SharedProperty deleted successfully: {obj_id}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete SharedProperty {obj_id}: {str(e)}")
        raise


# ==========================================
# Project CRUD
# ==========================================

def list_projects(session: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    """List all Projects with pagination."""
    statement = select(Project).offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())


def list_projects_with_stats(session: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
    """
    List all Projects with aggregated statistics (objectCount, linkCount).
    Returns a list of dictionaries with project data and counts.
    """
    from sqlmodel import func
    from sqlalchemy import or_
    
    # Get all projects
    projects = list_projects(session, skip=skip, limit=limit)
    
    result = []
    for project in projects:
        # Count object types for this project
        object_count_statement = select(func.count(ObjectType.id)).where(
            ObjectType.project_id == project.id
        )
        object_count = session.exec(object_count_statement).one() or 0
        
        # Count link types for this project
        # Link types don't have project_id directly, so we count links where
        # either source_type_id or target_type_id belongs to this project
        source_type_ids_statement = select(ObjectType.id).where(
            ObjectType.project_id == project.id
        )
        source_type_ids_result = session.exec(source_type_ids_statement).all()
        source_type_ids = list(source_type_ids_result) if source_type_ids_result else []
        
        link_count = 0
        if source_type_ids:
            link_count_statement = select(func.count(LinkType.id)).where(
                or_(
                    LinkType.source_type_id.in_(source_type_ids),
                    LinkType.target_type_id.in_(source_type_ids)
                )
            )
            link_count = session.exec(link_count_statement).one() or 0
        
        result.append({
            "id": project.id,
            "title": project.name,
            "description": project.description,
            "tags": [],  # Default empty, can be extended later
            "objectCount": object_count,
            "linkCount": link_count,
            "updatedAt": project.created_at,  # Use created_at as updatedAt for now
        })
    
    return result
