"""
Mapping CRUD operations for MDP Platform V3.1
Tables: ctx_object_mapping_def
"""
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from app.core.logger import logger
from app.models.context import (
    ObjectMappingDef,
    ObjectMappingDefCreate,
    ObjectMappingDefUpdate,
    ObjectMappingDefRead,
    ObjectMappingDefWithDetails,
)


# ==========================================
# Mapping Definition CRUD
# ==========================================

def create_mapping(session: Session, data: ObjectMappingDefCreate) -> ObjectMappingDef:
    """Create a new mapping definition."""
    mapping = ObjectMappingDef(
        object_def_id=data.object_def_id,
        source_connection_id=data.source_connection_id,
        source_table_name=data.source_table_name,
        mapping_spec=data.mapping_spec,
        status="DRAFT",
    )
    session.add(mapping)
    session.commit()
    session.refresh(mapping)
    logger.info(f"[Mapping] Created mapping: {mapping.id}")
    return mapping


def get_mapping(session: Session, mapping_id: str) -> Optional[ObjectMappingDef]:
    """Get mapping by ID."""
    return session.get(ObjectMappingDef, mapping_id)


def list_mappings(
    session: Session,
    object_def_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[ObjectMappingDef]:
    """List mappings with optional filters."""
    stmt = select(ObjectMappingDef)
    
    if object_def_id:
        stmt = stmt.where(ObjectMappingDef.object_def_id == object_def_id)
    if status:
        stmt = stmt.where(ObjectMappingDef.status == status)
    
    stmt = stmt.offset(skip).limit(limit)
    return list(session.exec(stmt).all())


def update_mapping(
    session: Session,
    mapping_id: str,
    data: ObjectMappingDefUpdate
) -> Optional[ObjectMappingDef]:
    """Update mapping definition."""
    mapping = session.get(ObjectMappingDef, mapping_id)
    if not mapping:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(mapping, key, value)
    
    mapping.updated_at = datetime.utcnow()
    session.add(mapping)
    session.commit()
    session.refresh(mapping)
    logger.info(f"[Mapping] Updated mapping: {mapping_id}")
    return mapping


def delete_mapping(session: Session, mapping_id: str) -> bool:
    """Delete mapping by ID."""
    mapping = session.get(ObjectMappingDef, mapping_id)
    if not mapping:
        return False
    
    session.delete(mapping)
    session.commit()
    logger.info(f"[Mapping] Deleted mapping: {mapping_id}")
    return True


def publish_mapping(session: Session, mapping_id: str) -> Optional[ObjectMappingDef]:
    """Publish a mapping (change status to PUBLISHED)."""
    mapping = session.get(ObjectMappingDef, mapping_id)
    if not mapping:
        return None
    
    mapping.status = "PUBLISHED"
    mapping.updated_at = datetime.utcnow()
    session.add(mapping)
    session.commit()
    session.refresh(mapping)
    logger.info(f"[Mapping] Published mapping: {mapping_id}")
    return mapping
