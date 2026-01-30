"""
Ontology CRUD operations for MDP Platform V3.1
Tables: meta_shared_property_def, meta_object_type_def, meta_object_type_ver,
        rel_object_ver_property, meta_link_type_def, meta_link_type_ver
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, desc
from sqlalchemy.exc import IntegrityError

from app.core.logger import logger
from app.models.ontology import (
    # ORM Models
    SharedPropertyDef,
    ObjectTypeDef,
    ObjectTypeVer,
    ObjectVerProperty,
    LinkTypeDef,
    LinkTypeVer,
    # DTOs
    SharedPropertyDefCreate,
    SharedPropertyDefUpdate,
    SharedPropertyDefRead,
    ObjectTypeDefCreate,
    ObjectTypeDefRead,
    ObjectTypeVerCreate,
    ObjectTypeVerUpdate,
    ObjectTypeVerRead,
    ObjectTypeFullRead,
    ObjectVerPropertyCreate,
    ObjectVerPropertyRead,
    LinkTypeDefCreate,
    LinkTypeDefRead,
    LinkTypeVerCreate,
    LinkTypeVerRead,
    LinkTypeFullRead,
    ObjectDefWithStats,
    TopologyNode,
    TopologyEdge,
    TopologyData,
)
from app.models.pipeline import PipelineDef, SyncTask
from app.models.system import Dataset, Connection
from app.models.context import ObjectMappingDef


# ==========================================
# Shared Property CRUD
# ==========================================

def create_shared_property(session: Session, data: SharedPropertyDefCreate) -> SharedPropertyDef:
    """Create a new shared property definition."""
    logger.info(f"[V3] Creating SharedProperty: {data.api_name}")
    
    try:
        db_obj = SharedPropertyDef(
            api_name=data.api_name,
            display_name=data.display_name,
            data_type=data.data_type,
            description=data.description,
            created_at=datetime.utcnow(),
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"[V3] SharedProperty created: {data.api_name} (ID: {db_obj.id})")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"[V3] Failed to create SharedProperty: {e}")
        raise


def get_shared_property(session: Session, prop_id: str) -> Optional[SharedPropertyDef]:
    """Get shared property by ID."""
    return session.get(SharedPropertyDef, prop_id)


def get_shared_property_by_name(session: Session, api_name: str) -> Optional[SharedPropertyDef]:
    """Get shared property by api_name."""
    statement = select(SharedPropertyDef).where(SharedPropertyDef.api_name == api_name)
    return session.exec(statement).first()


def list_shared_properties(session: Session, skip: int = 0, limit: int = 100) -> List[SharedPropertyDef]:
    """List all shared properties with pagination."""
    statement = select(SharedPropertyDef).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def list_shared_properties_by_project(
    session: Session,
    project_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[SharedPropertyDef]:
    """
    List shared properties used by a specific project.
    
    Query logic:
    - Project → ProjectObjectBinding → ObjectTypeDef
    - ObjectTypeDef → ObjectTypeVer (current_version_id)
    - ObjectTypeVer → ObjectVerProperty → SharedPropertyDef
    
    Returns distinct shared properties bound to any object type in the project.
    """
    from app.models.context import ProjectObjectBinding
    
    # Build the query to get distinct shared properties used by the project
    # Step 1: Get object_def_ids bound to this project
    # Step 2: For each object_def, get current_version_id
    # Step 3: For each version, get property bindings
    # Step 4: Return distinct shared properties
    
    statement = (
        select(SharedPropertyDef)
        .distinct()
        .join(ObjectVerProperty, ObjectVerProperty.property_def_id == SharedPropertyDef.id)
        .join(ObjectTypeVer, ObjectTypeVer.id == ObjectVerProperty.object_ver_id)
        .join(ObjectTypeDef, ObjectTypeDef.current_version_id == ObjectTypeVer.id)
        .join(ProjectObjectBinding, ProjectObjectBinding.object_def_id == ObjectTypeDef.id)
        .where(ProjectObjectBinding.project_id == project_id)
        .offset(skip)
        .limit(limit)
    )
    
    return list(session.exec(statement).all())


def update_shared_property(
    session: Session,
    prop_id: str,
    data: SharedPropertyDefUpdate
) -> Optional[SharedPropertyDef]:
    """Update an existing shared property."""
    logger.info(f"[V3] Updating SharedProperty: {prop_id}")
    
    db_obj = session.get(SharedPropertyDef, prop_id)
    if not db_obj:
        return None
    
    try:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(db_obj, field, value)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"[V3] SharedProperty updated: {prop_id}")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"[V3] Failed to update SharedProperty: {e}")
        raise


def delete_shared_property(session: Session, prop_id: str) -> bool:
    """Delete shared property by ID."""
    logger.info(f"[V3] Deleting SharedProperty: {prop_id}")
    
    db_obj = session.get(SharedPropertyDef, prop_id)
    if not db_obj:
        return False
    
    try:
        session.delete(db_obj)
        session.commit()
        logger.info(f"[V3] SharedProperty deleted: {prop_id}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"[V3] Failed to delete SharedProperty: {e}")
        raise


# ==========================================
# Object Type Definition CRUD
# ==========================================

def create_object_type_def(session: Session, data: ObjectTypeDefCreate) -> ObjectTypeDef:
    """Create a new object type definition."""
    logger.info(f"[V3] Creating ObjectTypeDef: {data.api_name}")
    
    try:
        db_obj = ObjectTypeDef(
            api_name=data.api_name,
            stereotype=data.stereotype,
            created_at=datetime.utcnow(),
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"[V3] ObjectTypeDef created: {data.api_name} (ID: {db_obj.id})")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"[V3] Failed to create ObjectTypeDef: {e}")
        raise


def get_object_type_def(session: Session, def_id: str) -> Optional[ObjectTypeDef]:
    """Get object type definition by ID."""
    return session.get(ObjectTypeDef, def_id)


def get_object_type_def_by_name(session: Session, api_name: str) -> Optional[ObjectTypeDef]:
    """Get object type definition by api_name."""
    statement = select(ObjectTypeDef).where(ObjectTypeDef.api_name == api_name)
    return session.exec(statement).first()


def list_object_type_defs(session: Session, skip: int = 0, limit: int = 100) -> List[ObjectTypeDef]:
    """List all object type definitions with pagination."""
    statement = select(ObjectTypeDef).offset(skip).limit(limit)
    return list(session.exec(statement).all())


# ==========================================
# Object Type Version CRUD
# ==========================================

def create_object_type_ver(
    session: Session,
    data: ObjectTypeVerCreate,
    set_as_current: bool = True
) -> ObjectTypeVer:
    """Create a new object type version."""
    logger.info(f"[V3] Creating ObjectTypeVer for def_id: {data.def_id}")
    
    try:
        db_obj = ObjectTypeVer(
            def_id=data.def_id,
            version_number=data.version_number,
            display_name=data.display_name,
            description=data.description,
            icon=data.icon,
            color=data.color,
            status=data.status,
            enable_global_search=data.enable_global_search,
            enable_geo_index=data.enable_geo_index,
            enable_vector_index=data.enable_vector_index,
            cache_ttl_seconds=data.cache_ttl_seconds,
            created_at=datetime.utcnow(),
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        
        # Optionally set as current version
        if set_as_current:
            obj_def = session.get(ObjectTypeDef, data.def_id)
            if obj_def:
                obj_def.current_version_id = db_obj.id
                session.add(obj_def)
                session.commit()
        
        logger.info(f"[V3] ObjectTypeVer created: {db_obj.id}")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"[V3] Failed to create ObjectTypeVer: {e}")
        raise


def get_object_type_ver(session: Session, ver_id: str) -> Optional[ObjectTypeVer]:
    """Get object type version by ID."""
    return session.get(ObjectTypeVer, ver_id)


def list_object_type_vers(session: Session, def_id: str) -> List[ObjectTypeVer]:
    """List all versions for an object type definition."""
    statement = select(ObjectTypeVer).where(ObjectTypeVer.def_id == def_id)
    return list(session.exec(statement).all())


def update_object_type_ver(
    session: Session,
    ver_id: str,
    data: ObjectTypeVerUpdate
) -> Optional[ObjectTypeVer]:
    """Update an existing object type version."""
    logger.info(f"[V3] Updating ObjectTypeVer: {ver_id}")
    
    db_obj = session.get(ObjectTypeVer, ver_id)
    if not db_obj:
        return None
    
    try:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(db_obj, field, value)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"[V3] ObjectTypeVer updated: {ver_id}")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"[V3] Failed to update ObjectTypeVer: {e}")
        raise


# ==========================================
# Object Type Datasource Query
# ==========================================

def get_object_type_datasource(
    session: Session,
    object_def_id: str,
    object_ver_id: Optional[str]
) -> Optional[Dict[str, Any]]:
    """
    Get datasource information for an object type.
    
    Query priority:
    1. Pipeline → Dataset (via object_ver_id)
    2. Mapping → Source Table (via object_def_id)
    
    Returns dict with datasource details including sync status.
    """
    datasource_info = None
    
    # Method 1: Query via Pipeline (preferred)
    if object_ver_id:
        pipeline_stmt = select(PipelineDef).where(
            PipelineDef.object_ver_id == object_ver_id,
            PipelineDef.is_active == True
        ).limit(1)
        pipeline = session.exec(pipeline_stmt).first()
        
        if pipeline:
            # Get Dataset info
            dataset = session.get(Dataset, pipeline.dataset_id)
            if dataset:
                # Get Connection info
                connection = session.get(Connection, dataset.connection_id)
                
                # Get latest sync status from SyncTask
                sync_status = None
                last_sync_time = None
                rows_processed = None
                
                sync_stmt = (
                    select(SyncTask)
                    .where(SyncTask.pipeline_id == pipeline.id)
                    .order_by(desc(SyncTask.start_time))
                    .limit(1)
                )
                latest_sync = session.exec(sync_stmt).first()
                
                if latest_sync:
                    sync_status = latest_sync.status
                    last_sync_time = latest_sync.start_time.isoformat() if latest_sync.start_time else None
                    rows_processed = latest_sync.rows_processed
                
                # Extract table name from dataset location_config
                table_name = None
                if isinstance(dataset.location_config, dict):
                    table_name = dataset.location_config.get("table") or dataset.location_config.get("table_name")
                
                datasource_info = {
                    "type": "pipeline",
                    "dataset_id": dataset.id,
                    "dataset_name": dataset.name,
                    "table_name": table_name,
                    "db_type": connection.conn_type if connection else None,
                    "connection_id": dataset.connection_id,
                    "connection_name": connection.name if connection else None,
                    "pipeline_id": pipeline.id,
                    "pipeline_mode": pipeline.mode,
                    "sync_status": sync_status,
                    "last_sync_time": last_sync_time,
                    "rows_processed": rows_processed,
                }
    
    # Method 2: Query via Mapping (fallback if no Pipeline)
    if not datasource_info:
        mapping_stmt = select(ObjectMappingDef).where(
            ObjectMappingDef.object_def_id == object_def_id,
            ObjectMappingDef.status == "PUBLISHED"
        ).limit(1)
        mapping = session.exec(mapping_stmt).first()
        
        if mapping:
            # Get Connection info
            connection = session.get(Connection, mapping.source_connection_id)
            
            datasource_info = {
                "type": "mapping",
                "source_table_name": mapping.source_table_name,
                "connection_id": mapping.source_connection_id,
                "connection_name": connection.name if connection else None,
                "db_type": connection.conn_type if connection else None,
                "mapping_id": mapping.id,
            }
    
    return datasource_info


# ==========================================
# Object Type Full View (Def + Version)
# ==========================================

def get_object_type_full(session: Session, def_id: str) -> Optional[ObjectTypeFullRead]:
    """Get object type with definition and current version combined."""
    obj_def = session.get(ObjectTypeDef, def_id)
    if not obj_def:
        return None
    
    result = ObjectTypeFullRead(
        id=obj_def.id,
        api_name=obj_def.api_name,
        stereotype=obj_def.stereotype,
        properties=[],
    )
    
    # Get current version if exists
    if obj_def.current_version_id:
        ver = session.get(ObjectTypeVer, obj_def.current_version_id)
        if ver:
            result.version_id = ver.id
            result.version_number = ver.version_number
            result.display_name = ver.display_name
            result.description = ver.description
            result.icon = ver.icon
            result.color = ver.color
            result.status = ver.status
            
            # Get properties
            result.properties = get_object_ver_properties(session, ver.id)
            
            # Get datasource information
            result.datasource = get_object_type_datasource(
                session,
                object_def_id=obj_def.id,
                object_ver_id=ver.id
            )
    
    return result


def list_object_types_full(
    session: Session,
    skip: int = 0,
    limit: int = 100
) -> List[ObjectTypeFullRead]:
    """List all object types with full info (def + current version)."""
    defs = list_object_type_defs(session, skip=skip, limit=limit)
    results = []
    for obj_def in defs:
        full = get_object_type_full(session, obj_def.id)
        if full:
            results.append(full)
    return results


# ==========================================
# Object Version Property Binding
# ==========================================

def bind_property_to_object_ver(
    session: Session,
    object_ver_id: str,
    data: ObjectVerPropertyCreate
) -> ObjectVerProperty:
    """Bind a property to an object type version.
    
    属性可以是：
    - 本地属性：property_def_id 为空，使用 local_* 字段
    - 共享属性引用：property_def_id 指向 SharedPropertyDef
    """
    prop_name = data.local_api_name or data.property_def_id or "unknown"
    logger.info(f"[V3] Binding property '{prop_name}' to version {object_ver_id}")
    
    try:
        db_obj = ObjectVerProperty(
            object_ver_id=object_ver_id,
            property_def_id=data.property_def_id,  # 可为空（本地属性）
            local_api_name=data.local_api_name,
            local_display_name=data.local_display_name,
            local_data_type=data.local_data_type,
            is_primary_key=data.is_primary_key,
            is_required=data.is_required,
            is_title=data.is_title,
            default_value=data.default_value,
            validation_rules=data.validation_rules,
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"[V3] Property bound: {db_obj.id}")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"[V3] Failed to bind property: {e}")
        raise


def get_object_ver_properties(
    session: Session,
    object_ver_id: str
) -> List[Dict[str, Any]]:
    """Get all properties bound to an object type version.
    
    返回本地属性和共享属性引用，统一格式。
    """
    statement = select(ObjectVerProperty).where(
        ObjectVerProperty.object_ver_id == object_ver_id
    )
    bindings = session.exec(statement).all()
    
    result = []
    for binding in bindings:
        # 尝试获取共享属性定义（若有）
        prop_def = None
        if binding.property_def_id:
            prop_def = session.get(SharedPropertyDef, binding.property_def_id)
        
        if prop_def:
            # 共享属性引用：从 SharedPropertyDef 获取类型信息
            result.append({
                "binding_id": binding.id,
                "property_def_id": binding.property_def_id,
                "shared_property_api_name": prop_def.api_name,
                "shared_property_display_name": prop_def.display_name,
                "api_name": binding.local_api_name or prop_def.api_name,
                "display_name": binding.local_display_name or prop_def.display_name,
                "data_type": binding.local_data_type or prop_def.data_type,
                "is_primary_key": binding.is_primary_key,
                "is_required": binding.is_required,
                "is_title": binding.is_title,
                "default_value": binding.default_value,
                "validation_rules": binding.validation_rules,
            })
        else:
            # 本地属性：从 binding 的 local_* 字段获取类型信息
            result.append({
                "binding_id": binding.id,
                "property_def_id": None,
                "shared_property_api_name": None,
                "shared_property_display_name": None,
                "api_name": binding.local_api_name,
                "display_name": binding.local_display_name or binding.local_api_name,
                "data_type": binding.local_data_type or "STRING",
                "is_primary_key": binding.is_primary_key,
                "is_required": binding.is_required,
                "is_title": binding.is_title,
                "default_value": binding.default_value,
                "validation_rules": binding.validation_rules,
            })
    
    return result


def unbind_property_from_object_ver(
    session: Session,
    binding_id: int
) -> bool:
    """Remove a property binding from an object type version."""
    logger.info(f"[V3] Unbinding property: {binding_id}")
    
    db_obj = session.get(ObjectVerProperty, binding_id)
    if not db_obj:
        return False
    
    try:
        session.delete(db_obj)
        session.commit()
        logger.info(f"[V3] Property unbound: {binding_id}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"[V3] Failed to unbind property: {e}")
        raise


# ==========================================
# Link Type Definition CRUD
# ==========================================

def create_link_type_def(session: Session, data: LinkTypeDefCreate) -> LinkTypeDef:
    """Create a new link type definition."""
    logger.info(f"[V3] Creating LinkTypeDef: {data.api_name}")
    
    try:
        db_obj = LinkTypeDef(
            api_name=data.api_name,
            created_at=datetime.utcnow(),
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"[V3] LinkTypeDef created: {data.api_name} (ID: {db_obj.id})")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"[V3] Failed to create LinkTypeDef: {e}")
        raise


def get_link_type_def(session: Session, def_id: str) -> Optional[LinkTypeDef]:
    """Get link type definition by ID."""
    return session.get(LinkTypeDef, def_id)


def get_link_type_def_by_name(session: Session, api_name: str) -> Optional[LinkTypeDef]:
    """Get link type definition by api_name."""
    statement = select(LinkTypeDef).where(LinkTypeDef.api_name == api_name)
    return session.exec(statement).first()


def list_link_type_defs(session: Session, skip: int = 0, limit: int = 100) -> List[LinkTypeDef]:
    """List all link type definitions with pagination."""
    statement = select(LinkTypeDef).offset(skip).limit(limit)
    return list(session.exec(statement).all())


# ==========================================
# Link Type Version CRUD
# ==========================================

def create_link_type_ver(
    session: Session,
    data: LinkTypeVerCreate,
    set_as_current: bool = True
) -> LinkTypeVer:
    """Create a new link type version."""
    logger.info(f"[V3] Creating LinkTypeVer for def_id: {data.def_id}")
    
    try:
        db_obj = LinkTypeVer(
            def_id=data.def_id,
            version_number=data.version_number,
            display_name=data.display_name,
            source_object_def_id=data.source_object_def_id,
            target_object_def_id=data.target_object_def_id,
            cardinality=data.cardinality,
            status=data.status,
            created_at=datetime.utcnow(),
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        
        # Optionally set as current version
        if set_as_current:
            link_def = session.get(LinkTypeDef, data.def_id)
            if link_def:
                link_def.current_version_id = db_obj.id
                session.add(link_def)
                session.commit()
        
        logger.info(f"[V3] LinkTypeVer created: {db_obj.id}")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"[V3] Failed to create LinkTypeVer: {e}")
        raise


def get_link_type_ver(session: Session, ver_id: str) -> Optional[LinkTypeVer]:
    """Get link type version by ID."""
    return session.get(LinkTypeVer, ver_id)


# ==========================================
# Link Type Full View (Def + Version)
# ==========================================

def get_link_type_full(session: Session, def_id: str) -> Optional[LinkTypeFullRead]:
    """Get link type with definition and current version combined."""
    link_def = session.get(LinkTypeDef, def_id)
    if not link_def:
        return None
    
    result = LinkTypeFullRead(
        id=link_def.id,
        api_name=link_def.api_name,
    )
    
    # Get current version if exists
    if link_def.current_version_id:
        ver = session.get(LinkTypeVer, link_def.current_version_id)
        if ver:
            result.version_id = ver.id
            result.version_number = ver.version_number
            result.display_name = ver.display_name
            result.source_object_def_id = ver.source_object_def_id
            result.target_object_def_id = ver.target_object_def_id
            result.cardinality = ver.cardinality
            result.status = ver.status
            
            # Get source/target type names
            source_def = session.get(ObjectTypeDef, ver.source_object_def_id)
            target_def = session.get(ObjectTypeDef, ver.target_object_def_id)
            if source_def:
                result.source_type_name = source_def.api_name
            if target_def:
                result.target_type_name = target_def.api_name
    
    return result


def list_link_types_full(
    session: Session,
    skip: int = 0,
    limit: int = 100
) -> List[LinkTypeFullRead]:
    """List all link types with full info (def + current version)."""
    defs = list_link_type_defs(session, skip=skip, limit=limit)
    results = []
    for link_def in defs:
        full = get_link_type_full(session, link_def.id)
        if full:
            results.append(full)
    return results


# ==========================================
# Project-scoped Object Type & Link Type Queries
# ==========================================

from app.models.context import ProjectObjectBinding


def list_object_types_by_project(
    session: Session,
    project_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[ObjectTypeFullRead]:
    """
    List object types bound to a specific project.
    Uses ctx_project_object_binding to filter.
    """
    # Get object_def_ids bound to this project
    statement = select(ProjectObjectBinding.object_def_id).where(
        ProjectObjectBinding.project_id == project_id
    ).offset(skip).limit(limit)
    
    object_def_ids = list(session.exec(statement).all())
    
    if not object_def_ids:
        return []
    
    # Get full object type info for each
    results = []
    for def_id in object_def_ids:
        full = get_object_type_full(session, def_id)
        if full:
            results.append(full)
    
    return results


def list_link_types_by_project(
    session: Session,
    project_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[LinkTypeFullRead]:
    """
    List link types related to a specific project.
    A link type is related if its source OR target object type is bound to the project.
    """
    # First, get all object_def_ids bound to this project
    binding_stmt = select(ProjectObjectBinding.object_def_id).where(
        ProjectObjectBinding.project_id == project_id
    )
    object_def_ids = set(session.exec(binding_stmt).all())
    
    if not object_def_ids:
        return []
    
    # Get all link type versions where source OR target matches project objects
    from sqlalchemy import or_
    
    link_ver_stmt = select(LinkTypeVer).where(
        or_(
            LinkTypeVer.source_object_def_id.in_(object_def_ids),
            LinkTypeVer.target_object_def_id.in_(object_def_ids)
        )
    )
    link_versions = session.exec(link_ver_stmt).all()
    
    # Get unique link def IDs
    link_def_ids = set()
    for lv in link_versions:
        link_def_ids.add(lv.def_id)
    
    # Get full link type info for each (with pagination)
    results = []
    for def_id in list(link_def_ids)[skip:skip+limit]:
        full = get_link_type_full(session, def_id)
        if full:
            results.append(full)
    
    return results


def list_shared_properties_by_project(
    session: Session,
    project_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[SharedPropertyDef]:
    """
    List shared properties used by a specific project.
    
    Returns distinct shared properties that are bound to:
    1. Any object type associated with the project via ctx_project_object_binding
    2. Any link type where source OR target object type is associated with the project
    
    Query path:
    - Object Types: Project → ProjectObjectBinding → ObjectTypeDef → ObjectTypeVer → ObjectVerProperty → SharedPropertyDef
    - Link Types: Project → ProjectObjectBinding → ObjectTypeDef (source/target) → LinkTypeVer → LinkVerProperty → SharedPropertyDef
    """
    from app.models.context import ProjectObjectBinding
    from app.models.ontology import LinkVerProperty, LinkTypeVer
    from sqlalchemy import or_
    
    # Step 1: Get all object_def_ids bound to this project
    binding_stmt = select(ProjectObjectBinding.object_def_id).where(
        ProjectObjectBinding.project_id == project_id
    )
    object_def_ids = list(session.exec(binding_stmt).all())
    
    if not object_def_ids:
        return []
    
    # --- Part A: Shared Properties from Object Types ---
    # Step 2: Get current version IDs for these object types
    obj_def_stmt = select(ObjectTypeDef.current_version_id).where(
        ObjectTypeDef.id.in_(object_def_ids),
        ObjectTypeDef.current_version_id.isnot(None)
    )
    obj_version_ids = [v for v in session.exec(obj_def_stmt).all() if v is not None]
    
    obj_prop_ids = set()
    if obj_version_ids:
        # Step 3: Get distinct property_def_ids from rel_object_ver_property
        prop_binding_stmt = select(ObjectVerProperty.property_def_id).where(
            ObjectVerProperty.object_ver_id.in_(obj_version_ids),
            ObjectVerProperty.property_def_id.isnot(None)
        ).distinct()
        obj_prop_ids = set(session.exec(prop_binding_stmt).all())
    
    # --- Part B: Shared Properties from Link Types ---
    # Step 4: Find link versions where source OR target is in object_def_ids
    # Note: A link is considered "in the project" if it connects objects in the project
    link_ver_stmt = select(LinkTypeVer.id).where(
        or_(
            LinkTypeVer.source_object_def_id.in_(object_def_ids),
            LinkTypeVer.target_object_def_id.in_(object_def_ids)
        )
    )
    link_version_ids = list(session.exec(link_ver_stmt).all())
    
    link_prop_ids = set()
    if link_version_ids:
        # Step 5: Get distinct property_def_ids from rel_link_ver_property
        link_prop_binding_stmt = select(LinkVerProperty.property_def_id).where(
            LinkVerProperty.link_ver_id.in_(link_version_ids)
        ).distinct()
        link_prop_ids = set(session.exec(link_prop_binding_stmt).all())
    
    # --- Combine and Fetch ---
    all_prop_ids = list(obj_prop_ids | link_prop_ids)
    
    if not all_prop_ids:
        return []
    
    # Step 6: Get the shared property definitions
    props_stmt = select(SharedPropertyDef).where(
        SharedPropertyDef.id.in_(all_prop_ids)
    ).offset(skip).limit(limit)
    
    return list(session.exec(props_stmt).all())


# ==========================================
# Object Type with Statistics
# ==========================================

def get_object_def_with_stats(session: Session, def_id: str) -> Optional[ObjectDefWithStats]:
    """
    Get a single object type definition with aggregated statistics.
    
    Statistics include:
    - property_count: Number of properties bound to current version
    - instance_count: Placeholder (0), requires instance table
    """
    from sqlmodel import func
    
    obj_def = session.get(ObjectTypeDef, def_id)
    if not obj_def:
        return None
    
    # Initialize result with definition data
    result = ObjectDefWithStats(
        id=obj_def.id,
        api_name=obj_def.api_name,
        stereotype=obj_def.stereotype,
        created_at=obj_def.created_at,
    )
    
    # Get current version info if exists
    if obj_def.current_version_id:
        ver = session.get(ObjectTypeVer, obj_def.current_version_id)
        if ver:
            result.display_name = ver.display_name
            result.description = ver.description
            result.status = ver.status
            result.updated_at = ver.created_at  # Use version created_at as updated_at
            
            # Count properties bound to this version
            prop_count_stmt = select(func.count(ObjectVerProperty.id)).where(
                ObjectVerProperty.object_ver_id == ver.id
            )
            result.property_count = session.exec(prop_count_stmt).one() or 0
    
    # instance_count remains 0 (placeholder, requires instance table)
    
    return result


def list_object_defs_with_stats(
    session: Session,
    project_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[ObjectDefWithStats]:
    """
    List all object type definitions with aggregated statistics.
    
    Args:
        session: Database session
        project_id: Optional project ID to filter by (via ctx_project_object_binding)
        skip: Pagination offset
        limit: Pagination limit
    
    Returns:
        List of ObjectDefWithStats with property_count and instance_count
    """
    if project_id:
        # Filter by project: get object_def_ids bound to this project
        binding_stmt = select(ProjectObjectBinding.object_def_id).where(
            ProjectObjectBinding.project_id == project_id
        ).offset(skip).limit(limit)
        object_def_ids = list(session.exec(binding_stmt).all())
        
        if not object_def_ids:
            return []
        
        # Get stats for each object type
        results = []
        for def_id in object_def_ids:
            stats = get_object_def_with_stats(session, def_id)
            if stats:
                results.append(stats)
        return results
    else:
        # No project filter: get all object types
        defs = list_object_type_defs(session, skip=skip, limit=limit)
        results = []
        for obj_def in defs:
            stats = get_object_def_with_stats(session, obj_def.id)
            if stats:
                results.append(stats)
        return results


# ==========================================
# Topology Graph Data
# ==========================================

def get_topology_data(session: Session) -> TopologyData:
    """
    Get topology graph data for visualization.
    
    Nodes: Object types with current version info
    Edges: Link types connecting object types
    
    SQL Logic:
    - Nodes: SELECT from meta_object_type_def JOIN meta_object_type_ver
    - Edges: SELECT from meta_link_type_def JOIN meta_link_type_ver
             with validation that source/target objects exist
    """
    nodes: List[TopologyNode] = []
    edges: List[TopologyEdge] = []
    
    # Build a set of valid object def IDs for edge validation
    valid_object_ids = set()
    
    # ==========================================
    # Query Nodes: Object Types with current version
    # ==========================================
    obj_defs = list_object_type_defs(session, skip=0, limit=1000)
    
    for obj_def in obj_defs:
        # Only include objects with a current version
        if not obj_def.current_version_id:
            continue
        
        # Get version info
        ver = session.get(ObjectTypeVer, obj_def.current_version_id)
        if not ver:
            continue
        
        valid_object_ids.add(obj_def.id)
        
        nodes.append(TopologyNode(
            id=obj_def.id,
            api_name=obj_def.api_name,
            display_name=ver.display_name,
            stereotype=obj_def.stereotype,
            icon=ver.icon,
            color=ver.color,
        ))
    
    # ==========================================
    # Query Edges: Link Types with current version
    # ==========================================
    link_defs = list_link_type_defs(session, skip=0, limit=1000)
    
    for link_def in link_defs:
        # Only include links with a current version
        if not link_def.current_version_id:
            continue
        
        # Get version info
        ver = session.get(LinkTypeVer, link_def.current_version_id)
        if not ver:
            continue
        
        # Validate that both source and target exist in our nodes
        if ver.source_object_def_id not in valid_object_ids:
            logger.warning(f"[Topology] Link {link_def.api_name}: source {ver.source_object_def_id} not found")
            continue
        if ver.target_object_def_id not in valid_object_ids:
            logger.warning(f"[Topology] Link {link_def.api_name}: target {ver.target_object_def_id} not found")
            continue
        
        edges.append(TopologyEdge(
            id=link_def.id,
            api_name=link_def.api_name,
            display_name=ver.display_name,
            source=ver.source_object_def_id,
            target=ver.target_object_def_id,
            cardinality=ver.cardinality,
        ))
    
    logger.info(f"[Topology] Generated graph with {len(nodes)} nodes and {len(edges)} edges")
    
    return TopologyData(nodes=nodes, edges=edges)
