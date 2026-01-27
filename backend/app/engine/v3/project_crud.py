"""
Project CRUD operations for MDP Platform V3.1
Table: sys_project
"""
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.core.logger import logger
from app.models.system import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    ProjectWithStats,
)


def create_project(session: Session, data: ProjectCreate) -> Project:
    """Create a new project."""
    logger.info(f"[V3] Creating Project: {data.name}")
    
    try:
        db_obj = Project(
            name=data.name,
            description=data.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"[V3] Project created: {data.name} (ID: {db_obj.id})")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"[V3] Failed to create Project: {e}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"[V3] Unexpected error creating Project: {e}")
        raise


def get_project(session: Session, project_id: str) -> Optional[Project]:
    """Get project by ID."""
    return session.get(Project, project_id)


def list_projects(session: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    """List all projects with pagination."""
    statement = select(Project).offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())


def update_project(
    session: Session,
    project_id: str,
    data: ProjectUpdate
) -> Optional[Project]:
    """Update an existing project."""
    logger.info(f"[V3] Updating Project: {project_id}")
    
    db_obj = session.get(Project, project_id)
    if not db_obj:
        logger.warning(f"[V3] Project not found: {project_id}")
        return None
    
    try:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(db_obj, field, value)
        
        db_obj.updated_at = datetime.utcnow()
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"[V3] Project updated: {project_id}")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"[V3] Failed to update Project: {e}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"[V3] Unexpected error updating Project: {e}")
        raise


def delete_project(session: Session, project_id: str) -> bool:
    """Delete project by ID."""
    logger.info(f"[V3] Deleting Project: {project_id}")
    
    db_obj = session.get(Project, project_id)
    if not db_obj:
        logger.warning(f"[V3] Project not found: {project_id}")
        return False
    
    try:
        session.delete(db_obj)
        session.commit()
        logger.info(f"[V3] Project deleted: {project_id}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"[V3] Failed to delete Project: {e}")
        raise


def get_project_with_stats(session: Session, project_id: str) -> Optional[ProjectWithStats]:
    """Get project with aggregated statistics."""
    from sqlmodel import func
    from app.models.context import ProjectObjectBinding
    from app.models.ontology import LinkTypeVer
    
    project = get_project(session, project_id)
    if not project:
        return None
    
    # Count object bindings
    object_count_stmt = select(func.count(ProjectObjectBinding.object_def_id)).where(
        ProjectObjectBinding.project_id == project_id
    )
    object_count = session.exec(object_count_stmt).one() or 0
    
    # Get all object_def_ids bound to this project
    object_ids_stmt = select(ProjectObjectBinding.object_def_id).where(
        ProjectObjectBinding.project_id == project_id
    )
    object_def_ids = list(session.exec(object_ids_stmt).all())
    
    # Count link types where source OR target is bound to this project
    link_count = 0
    if object_def_ids:
        from sqlalchemy import or_
        link_count_stmt = select(func.count(func.distinct(LinkTypeVer.def_id))).where(
            or_(
                LinkTypeVer.source_object_def_id.in_(object_def_ids),
                LinkTypeVer.target_object_def_id.in_(object_def_ids)
            )
        )
        link_count = session.exec(link_count_stmt).one() or 0
    
    return ProjectWithStats(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
        object_count=object_count,
        link_count=link_count,
    )


def list_projects_with_stats(session: Session, skip: int = 0, limit: int = 100) -> List[ProjectWithStats]:
    """List all projects with aggregated statistics."""
    projects = list_projects(session, skip=skip, limit=limit)
    return [get_project_with_stats(session, p.id) for p in projects if get_project_with_stats(session, p.id)]
