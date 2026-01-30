"""
Mapping CRUD operations for MDP Platform V3.1
Tables: ctx_object_mapping_def, ctx_link_mapping_def
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy import create_engine, text, inspect

from app.core.logger import logger
from app.core.config import settings
from app.models.context import (
    ObjectMappingDef,
    ObjectMappingDefCreate,
    ObjectMappingDefUpdate,
    ObjectMappingDefRead,
    ObjectMappingDefWithDetails,
    LinkMappingDef,
    LinkMappingDefCreate,
    LinkMappingDefUpdate,
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


def update_mapping_table_name(
    session: Session,
    mapping_id: str,
    new_table_name: str
) -> Optional[ObjectMappingDef]:
    """Update mapping's source_table_name and regenerate mapping_spec if needed."""
    mapping = session.get(ObjectMappingDef, mapping_id)
    if not mapping:
        return None
    
    old_table_name = mapping.source_table_name
    mapping.source_table_name = new_table_name
    
    # Regenerate mapping_spec based on new table structure
    new_mapping_spec = generate_mapping_spec_from_table(new_table_name)
    if new_mapping_spec.get("nodes"):
        mapping.mapping_spec = new_mapping_spec
        logger.info(f"[Mapping] Regenerated mapping_spec for table {new_table_name}")
    
    mapping.updated_at = datetime.utcnow()
    session.add(mapping)
    session.commit()
    session.refresh(mapping)
    logger.info(f"[Mapping] Updated mapping {mapping_id} table name: {old_table_name} -> {new_table_name}")
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


def get_mapping_by_table(
    session: Session,
    source_connection_id: str,
    source_table_name: str
) -> Optional[ObjectMappingDef]:
    """Get mapping by connection ID and table name."""
    stmt = select(ObjectMappingDef).where(
        ObjectMappingDef.source_connection_id == source_connection_id,
        ObjectMappingDef.source_table_name == source_table_name
    )
    return session.exec(stmt).first()


def list_mappings_by_connection(
    session: Session,
    source_connection_id: str
) -> List[ObjectMappingDef]:
    """List all mappings for a specific connection."""
    stmt = select(ObjectMappingDef).where(
        ObjectMappingDef.source_connection_id == source_connection_id
    )
    return list(session.exec(stmt).all())


def generate_mapping_spec_from_table(table_name: str) -> Dict[str, Any]:
    """
    Generate a basic mapping_spec from table structure.
    
    Creates a React Flow graph with:
    - Source nodes for each column
    - Direct edges from source to target (no transformation)
    - Target nodes (to be configured by user)
    
    Args:
        table_name: Table name in mdp_raw_store
        
    Returns:
        Dict with 'nodes' and 'edges' keys
    """
    try:
        # Connect to raw store
        engine = create_engine(settings.raw_store_database_url, pool_pre_ping=True)
        inspector = inspect(engine)
        
        # Get table columns
        if not inspector.has_table(table_name):
            logger.warning(f"[Mapping] Table {table_name} does not exist in raw store")
            return {"nodes": [], "edges": []}
        
        columns = inspector.get_columns(table_name)
        
        # Generate nodes and edges
        nodes = []
        edges = []
        
        for col in columns:
            col_name = col['name']
            col_type = str(col['type'])
            
            # Skip internal columns
            if col_name.startswith('_'):
                continue
            
            # Create source node
            source_node_id = f"source_{col_name}"
            nodes.append({
                "id": source_node_id,
                "type": "sourceColumn",
                "data": {
                    "column": col_name,
                    "type": col_type
                },
                "position": {"x": 0, "y": 0}  # Will be positioned by frontend
            })
            
            # Create target node (placeholder - user will configure)
            target_node_id = f"target_{col_name}"
            nodes.append({
                "id": target_node_id,
                "type": "targetProperty",
                "data": {
                    "property": "",  # Empty - user will fill
                    "type": _infer_property_type(col_type)
                },
                "position": {"x": 0, "y": 0}  # Will be positioned by frontend
            })
            
            # Create direct edge (no transformation)
            edges.append({
                "id": f"edge_{col_name}",
                "source": source_node_id,
                "target": target_node_id,
                "type": "default"
            })
        
        engine.dispose()
        
        return {
            "nodes": nodes,
            "edges": edges
        }
        
    except Exception as e:
        logger.error(f"[Mapping] Failed to generate mapping spec from table {table_name}: {e}")
        return {"nodes": [], "edges": []}


def _infer_property_type(sql_type: str) -> str:
    """Infer property type from SQL column type."""
    sql_type_lower = sql_type.lower()
    
    if 'int' in sql_type_lower or 'bigint' in sql_type_lower or 'smallint' in sql_type_lower:
        return "number"
    elif 'float' in sql_type_lower or 'double' in sql_type_lower or 'decimal' in sql_type_lower:
        return "number"
    elif 'bool' in sql_type_lower or 'tinyint' in sql_type_lower:
        return "boolean"
    elif 'date' in sql_type_lower or 'time' in sql_type_lower or 'timestamp' in sql_type_lower:
        return "datetime"
    elif 'json' in sql_type_lower:
        return "object"
    else:
        return "string"


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


# ==========================================
# Link Mapping CRUD
# ==========================================

def create_link_mapping(session: Session, data: LinkMappingDefCreate) -> LinkMappingDef:
    """Create a new link mapping definition."""
    mapping = LinkMappingDef(
        link_def_id=data.link_def_id,
        source_connection_id=data.source_connection_id,
        join_table_name=data.join_table_name,
        source_key_column=data.source_key_column,
        target_key_column=data.target_key_column,
        property_mappings=data.property_mappings or {},
        status="DRAFT",
    )
    session.add(mapping)
    session.commit()
    session.refresh(mapping)
    logger.info(f"[Mapping] Created link mapping: {mapping.id}")
    return mapping


def get_link_mapping(session: Session, mapping_id: str) -> Optional[LinkMappingDef]:
    """Get link mapping by ID."""
    return session.get(LinkMappingDef, mapping_id)


def get_link_mapping_by_def_id(session: Session, link_def_id: str) -> Optional[LinkMappingDef]:
    """Get link mapping by link definition ID."""
    stmt = select(LinkMappingDef).where(LinkMappingDef.link_def_id == link_def_id)
    return session.exec(stmt).first()


def update_link_mapping(
    session: Session,
    mapping_id: str,
    data: LinkMappingDefUpdate
) -> Optional[LinkMappingDef]:
    """Update link mapping definition."""
    mapping = session.get(LinkMappingDef, mapping_id)
    if not mapping:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(mapping, key, value)
    
    mapping.updated_at = datetime.utcnow()
    session.add(mapping)
    session.commit()
    session.refresh(mapping)
    logger.info(f"[Mapping] Updated link mapping: {mapping_id}")
    return mapping


def delete_link_mapping(session: Session, mapping_id: str) -> bool:
    """Delete link mapping by ID."""
    mapping = session.get(LinkMappingDef, mapping_id)
    if not mapping:
        return False
    
    session.delete(mapping)
    session.commit()
    logger.info(f"[Mapping] Deleted link mapping: {mapping_id}")
    return True
