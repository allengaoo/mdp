"""
V3.1 API - Projects
Endpoints for project management
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.db import get_session
from app.models.system import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    ProjectWithStats,
)
from app.engine.v3 import project_crud

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=List[ProjectRead])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all projects."""
    projects = project_crud.list_projects(session, skip=skip, limit=limit)
    return projects


@router.get("/with-stats", response_model=List[ProjectWithStats])
def list_projects_with_stats(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all projects with aggregated statistics."""
    return project_crud.list_projects_with_stats(session, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: str,
    session: Session = Depends(get_session)
):
    """Get a specific project by ID."""
    project = project_crud.get_project(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )
    return project


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    session: Session = Depends(get_session)
):
    """Create a new project."""
    try:
        return project_crud.create_project(session, data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: str,
    data: ProjectUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing project."""
    project = project_crud.update_project(session, project_id, data)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    session: Session = Depends(get_session)
):
    """Delete a project."""
    success = project_crud.delete_project(session, project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )
    return None


# ==========================================
# Project Object Bindings
# ==========================================

from app.models.context import (
    ProjectObjectBindingCreate,
    ProjectObjectBindingUpdate,
    ProjectObjectBindingWithDetails,
)
from app.engine.v3 import context_crud


@router.get("/{project_id}/objects", response_model=List[ProjectObjectBindingWithDetails])
def get_project_objects(
    project_id: str,
    session: Session = Depends(get_session)
):
    """Get all object types bound to a project."""
    # Verify project exists
    project = project_crud.get_project(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )
    
    return context_crud.get_project_object_bindings(session, project_id)


@router.post("/{project_id}/objects", response_model=ProjectObjectBindingWithDetails, status_code=status.HTTP_201_CREATED)
def bind_object_to_project(
    project_id: str,
    data: ProjectObjectBindingCreate,
    session: Session = Depends(get_session)
):
    """Bind an object type to a project."""
    # Ensure project_id matches
    if data.project_id != project_id:
        data.project_id = project_id
    
    try:
        binding = context_crud.create_project_object_binding(session, data)
        # Return with details
        bindings = context_crud.get_project_object_bindings(session, project_id)
        for b in bindings:
            if b.object_def_id == data.object_def_id:
                return b
        return binding
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{project_id}/objects/{object_def_id}")
def update_project_object_binding(
    project_id: str,
    object_def_id: str,
    data: ProjectObjectBindingUpdate,
    session: Session = Depends(get_session)
):
    """Update a project-object binding."""
    binding = context_crud.update_project_object_binding(
        session, project_id, object_def_id, data
    )
    if not binding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Binding not found"
        )
    return binding


@router.delete("/{project_id}/objects/{object_def_id}", status_code=status.HTTP_204_NO_CONTENT)
def unbind_object_from_project(
    project_id: str,
    object_def_id: str,
    session: Session = Depends(get_session)
):
    """Remove an object type binding from a project."""
    success = context_crud.delete_project_object_binding(
        session, project_id, object_def_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Binding not found"
        )
    return None


# ==========================================
# Project-scoped Object Types & Link Types
# ==========================================

from typing import List as ListType
from app.models.ontology import ObjectTypeFullRead, LinkTypeFullRead, SharedPropertyDefRead
from app.engine.v3 import ontology_crud


@router.get("/{project_id}/object-types", response_model=ListType[ObjectTypeFullRead])
def list_project_object_types(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    List all object types bound to a project.
    Returns full object type info (definition + current version).
    """
    # Verify project exists
    project = project_crud.get_project(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )
    
    return ontology_crud.list_object_types_by_project(
        session, project_id, skip=skip, limit=limit
    )


@router.get("/{project_id}/link-types", response_model=ListType[LinkTypeFullRead])
def list_project_link_types(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    List all link types related to a project.
    A link type is included if its source OR target object type is bound to the project.
    """
    # Verify project exists
    project = project_crud.get_project(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )
    
    return ontology_crud.list_link_types_by_project(
        session, project_id, skip=skip, limit=limit
    )


@router.get("/{project_id}/shared-properties", response_model=ListType[SharedPropertyDefRead])
def list_project_shared_properties(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    List all shared properties used by a project.
    
    Returns distinct shared properties that are bound to any object type
    associated with the project via ctx_project_object_binding.
    
    Query path:
    Project → ProjectObjectBinding → ObjectTypeDef → ObjectTypeVer 
            → ObjectVerProperty → SharedPropertyDef
    """
    # Verify project exists
    project = project_crud.get_project(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )
    
    return ontology_crud.list_shared_properties_by_project(
        session, project_id, skip=skip, limit=limit
    )
