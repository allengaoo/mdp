"""
Context Binding CRUD operations for MDP Platform V3.1
Table: ctx_project_object_binding
"""
from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.core.logger import logger
from app.models.context import (
    ProjectObjectBinding,
    ProjectObjectBindingCreate,
    ProjectObjectBindingUpdate,
    ProjectObjectBindingRead,
    ProjectObjectBindingWithDetails,
)
from app.models.system import Project
from app.models.ontology import ObjectTypeDef, ObjectTypeVer


def create_project_object_binding(
    session: Session,
    data: ProjectObjectBindingCreate
) -> ProjectObjectBinding:
    """Create a new project-object binding."""
    logger.info(f"[V3] Creating ProjectObjectBinding: project={data.project_id}, object={data.object_def_id}")
    
    try:
        db_obj = ProjectObjectBinding(
            project_id=data.project_id,
            object_def_id=data.object_def_id,
            used_version_id=data.used_version_id,
            project_display_alias=data.project_display_alias,
            is_visible=data.is_visible,
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"[V3] ProjectObjectBinding created")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"[V3] Failed to create ProjectObjectBinding: {e}")
        raise


def get_project_object_binding(
    session: Session,
    project_id: str,
    object_def_id: str
) -> Optional[ProjectObjectBinding]:
    """Get a specific project-object binding."""
    statement = select(ProjectObjectBinding).where(
        ProjectObjectBinding.project_id == project_id,
        ProjectObjectBinding.object_def_id == object_def_id
    )
    return session.exec(statement).first()


def get_project_object_bindings(
    session: Session,
    project_id: str
) -> List[ProjectObjectBindingWithDetails]:
    """Get all object bindings for a project with details."""
    statement = select(ProjectObjectBinding).where(
        ProjectObjectBinding.project_id == project_id
    )
    bindings = session.exec(statement).all()
    
    results = []
    for binding in bindings:
        # Get object type definition
        obj_def = session.get(ObjectTypeDef, binding.object_def_id)
        # Get version
        obj_ver = session.get(ObjectTypeVer, binding.used_version_id)
        # Get project
        project = session.get(Project, binding.project_id)
        
        result = ProjectObjectBindingWithDetails(
            project_id=binding.project_id,
            object_def_id=binding.object_def_id,
            used_version_id=binding.used_version_id,
            project_display_alias=binding.project_display_alias,
            is_visible=binding.is_visible,
            project_name=project.name if project else None,
            object_type_api_name=obj_def.api_name if obj_def else None,
            object_type_display_name=obj_ver.display_name if obj_ver else None,
            version_number=obj_ver.version_number if obj_ver else None,
        )
        results.append(result)
    
    return results


def get_object_project_bindings(
    session: Session,
    object_def_id: str
) -> List[ProjectObjectBinding]:
    """Get all project bindings for an object type."""
    statement = select(ProjectObjectBinding).where(
        ProjectObjectBinding.object_def_id == object_def_id
    )
    return list(session.exec(statement).all())


def update_project_object_binding(
    session: Session,
    project_id: str,
    object_def_id: str,
    data: ProjectObjectBindingUpdate
) -> Optional[ProjectObjectBinding]:
    """Update an existing project-object binding."""
    logger.info(f"[V3] Updating ProjectObjectBinding: project={project_id}, object={object_def_id}")
    
    db_obj = get_project_object_binding(session, project_id, object_def_id)
    if not db_obj:
        logger.warning(f"[V3] ProjectObjectBinding not found")
        return None
    
    try:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(db_obj, field, value)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"[V3] ProjectObjectBinding updated")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"[V3] Failed to update ProjectObjectBinding: {e}")
        raise


def delete_project_object_binding(
    session: Session,
    project_id: str,
    object_def_id: str
) -> bool:
    """Delete a project-object binding."""
    logger.info(f"[V3] Deleting ProjectObjectBinding: project={project_id}, object={object_def_id}")
    
    db_obj = get_project_object_binding(session, project_id, object_def_id)
    if not db_obj:
        logger.warning(f"[V3] ProjectObjectBinding not found")
        return False
    
    try:
        session.delete(db_obj)
        session.commit()
        logger.info(f"[V3] ProjectObjectBinding deleted")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"[V3] Failed to delete ProjectObjectBinding: {e}")
        raise


def bind_all_object_types_to_project(
    session: Session,
    project_id: str
) -> int:
    """Bind all existing object types to a project (convenience method).
    Returns the number of bindings created.
    """
    from app.engine.v3.ontology_crud import list_object_type_defs
    
    defs = list_object_type_defs(session, limit=1000)
    count = 0
    
    for obj_def in defs:
        # Skip if already bound
        existing = get_project_object_binding(session, project_id, obj_def.id)
        if existing:
            continue
        
        # Get current version
        if obj_def.current_version_id:
            try:
                create_project_object_binding(session, ProjectObjectBindingCreate(
                    project_id=project_id,
                    object_def_id=obj_def.id,
                    used_version_id=obj_def.current_version_id,
                    is_visible=True,
                ))
                count += 1
            except Exception as e:
                logger.warning(f"[V3] Failed to bind {obj_def.api_name} to project: {e}")
    
    return count
