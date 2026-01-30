"""
V3.1 API - Ontology
Endpoints for shared properties, object types, and link types
"""
import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from pydantic import BaseModel

from app.core.db import get_session
from app.core.logger import logger
from app.models.ontology import (
    # Shared Property
    SharedPropertyDefCreate,
    SharedPropertyDefUpdate,
    SharedPropertyDefRead,
    # Object Type
    ObjectTypeDefCreate,
    ObjectTypeDefRead,
    ObjectTypeVerCreate,
    ObjectTypeVerUpdate,
    ObjectTypeVerRead,
    ObjectTypeFullRead,
    ObjectVerPropertyCreate,
    ObjectDefWithStats,
    # Link Type
    LinkTypeDefCreate,
    LinkTypeDefRead,
    LinkTypeVerCreate,
    LinkTypeFullRead,
    # Topology
    TopologyData,
)
from app.engine.v3 import ontology_crud
from app.engine import meta_crud
from app.models.meta import ActionDefWithFunction, FunctionDefForList

router = APIRouter(prefix="/ontology", tags=["Ontology"])


# ==========================================
# Shared Properties
# ==========================================

@router.get("/properties", response_model=List[SharedPropertyDefRead])
def list_shared_properties(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    List shared property definitions.
    
    Optionally filter by project_id to get only properties used in that project
    (referenced by object types or link types in the project).
    """
    if project_id:
        return ontology_crud.list_shared_properties_by_project(session, project_id, skip=skip, limit=limit)
    return ontology_crud.list_shared_properties(session, skip=skip, limit=limit)


@router.get("/properties/{prop_id}", response_model=SharedPropertyDefRead)
def get_shared_property(
    prop_id: str,
    session: Session = Depends(get_session)
):
    """Get a specific shared property by ID."""
    prop = ontology_crud.get_shared_property(session, prop_id)
    if not prop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SharedProperty not found: {prop_id}"
        )
    return prop


@router.post("/properties", response_model=SharedPropertyDefRead, status_code=status.HTTP_201_CREATED)
def create_shared_property(
    data: SharedPropertyDefCreate,
    session: Session = Depends(get_session)
):
    """Create a new shared property definition."""
    try:
        return ontology_crud.create_shared_property(session, data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/properties/{prop_id}", response_model=SharedPropertyDefRead)
def update_shared_property(
    prop_id: str,
    data: SharedPropertyDefUpdate,
    session: Session = Depends(get_session)
):
    """Update a shared property definition."""
    prop = ontology_crud.update_shared_property(session, prop_id, data)
    if not prop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SharedProperty not found: {prop_id}"
        )
    return prop


@router.delete("/properties/{prop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shared_property(
    prop_id: str,
    session: Session = Depends(get_session)
):
    """Delete a shared property definition."""
    success = ontology_crud.delete_shared_property(session, prop_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SharedProperty not found: {prop_id}"
        )
    return None


# ==========================================
# Object Types
# ==========================================

@router.get("/objects/with-stats", response_model=List[ObjectDefWithStats])
def list_object_defs_with_stats(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    List all object type definitions with aggregated statistics.
    
    Returns object types with:
    - property_count: Number of properties bound to current version
    - instance_count: Number of data instances (placeholder)
    
    Optionally filter by project_id to get only object types bound to that project.
    """
    return ontology_crud.list_object_defs_with_stats(
        session, project_id=project_id, skip=skip, limit=limit
    )


@router.get("/object-types", response_model=List[ObjectTypeFullRead])
def list_object_types(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all object types with current version info."""
    return ontology_crud.list_object_types_full(session, skip=skip, limit=limit)


@router.get("/object-types/{def_id}", response_model=ObjectTypeFullRead)
def get_object_type(
    def_id: str,
    session: Session = Depends(get_session)
):
    """Get a specific object type with current version."""
    obj = ontology_crud.get_object_type_full(session, def_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ObjectType not found: {def_id}"
        )
    return obj


@router.post("/object-types", response_model=ObjectTypeFullRead, status_code=status.HTTP_201_CREATED)
def create_object_type(
    data: ObjectTypeDefCreate,
    session: Session = Depends(get_session)
):
    """Create a new object type definition with initial version."""
    try:
        # Create definition
        obj_def = ontology_crud.create_object_type_def(session, data)
        
        # Create initial version (v1.0)
        ver_data = ObjectTypeVerCreate(
            def_id=obj_def.id,
            version_number="1.0",
            display_name=data.api_name,  # Use api_name as initial display_name
            status="DRAFT",
        )
        ontology_crud.create_object_type_ver(session, ver_data, set_as_current=True)
        
        # Return full view
        return ontology_crud.get_object_type_full(session, obj_def.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/object-types/{def_id}/versions", response_model=ObjectTypeVerRead, status_code=status.HTTP_201_CREATED)
def create_object_type_version(
    def_id: str,
    data: ObjectTypeVerCreate,
    session: Session = Depends(get_session)
):
    """Create a new version for an object type."""
    # Verify object type exists
    obj_def = ontology_crud.get_object_type_def(session, def_id)
    if not obj_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ObjectType not found: {def_id}"
        )
    
    # Ensure def_id matches
    data.def_id = def_id
    
    try:
        return ontology_crud.create_object_type_ver(session, data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/object-types/{def_id}/versions/{ver_id}", response_model=ObjectTypeVerRead)
def update_object_type_version(
    def_id: str,
    ver_id: str,
    data: ObjectTypeVerUpdate,
    session: Session = Depends(get_session)
):
    """Update an object type version."""
    ver = ontology_crud.update_object_type_ver(session, ver_id, data)
    if not ver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ObjectTypeVersion not found: {ver_id}"
        )
    return ver


@router.get("/object-types/{def_id}/versions", response_model=List[ObjectTypeVerRead])
def list_object_type_versions(
    def_id: str,
    session: Session = Depends(get_session)
):
    """List all versions for an object type."""
    return ontology_crud.list_object_type_vers(session, def_id)


# ==========================================
# Object Type Properties
# ==========================================

@router.get("/object-types/{def_id}/properties", response_model=List[Dict[str, Any]])
def get_object_type_properties(
    def_id: str,
    session: Session = Depends(get_session)
):
    """Get all properties for the current version of an object type."""
    obj = ontology_crud.get_object_type_full(session, def_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ObjectType not found: {def_id}"
        )
    
    if not obj.version_id:
        return []
    
    return ontology_crud.get_object_ver_properties(session, obj.version_id)


@router.post("/object-types/{def_id}/properties", status_code=status.HTTP_201_CREATED)
def bind_property_to_object_type(
    def_id: str,
    data: ObjectVerPropertyCreate,
    session: Session = Depends(get_session)
):
    """Bind a shared property to the current version of an object type."""
    obj = ontology_crud.get_object_type_full(session, def_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ObjectType not found: {def_id}"
        )
    
    if not obj.version_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ObjectType has no current version"
        )
    
    try:
        return ontology_crud.bind_property_to_object_ver(session, obj.version_id, data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==========================================
# Link Types
# ==========================================

@router.get("/link-types", response_model=List[LinkTypeFullRead])
def list_link_types(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all link types with current version info."""
    return ontology_crud.list_link_types_full(session, skip=skip, limit=limit)


@router.get("/link-types/{def_id}", response_model=LinkTypeFullRead)
def get_link_type(
    def_id: str,
    session: Session = Depends(get_session)
):
    """Get a specific link type with current version."""
    link = ontology_crud.get_link_type_full(session, def_id)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LinkType not found: {def_id}"
        )
    return link


@router.post("/link-types", response_model=LinkTypeFullRead, status_code=status.HTTP_201_CREATED)
def create_link_type(
    data: LinkTypeDefCreate,
    source_object_def_id: str,
    target_object_def_id: str,
    cardinality: str = "MANY_TO_MANY",
    display_name: str = None,
    session: Session = Depends(get_session)
):
    """Create a new link type definition with initial version."""
    try:
        # Create definition
        link_def = ontology_crud.create_link_type_def(session, data)
        
        # Create initial version
        ver_data = LinkTypeVerCreate(
            def_id=link_def.id,
            version_number="1.0",
            display_name=display_name or data.api_name,
            source_object_def_id=source_object_def_id,
            target_object_def_id=target_object_def_id,
            cardinality=cardinality,
            status="DRAFT",
        )
        ontology_crud.create_link_type_ver(session, ver_data, set_as_current=True)
        
        # Return full view
        return ontology_crud.get_link_type_full(session, link_def.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==========================================
# Topology Graph
# ==========================================

@router.get("/topology", response_model=TopologyData)
def get_topology(
    session: Session = Depends(get_session)
):
    """
    Get topology graph data for visualization.
    
    Returns:
    - nodes: List of object types with display info (id, api_name, display_name, icon, color)
    - edges: List of link types connecting objects (id, api_name, display_name, source, target, cardinality)
    
    Data is filtered to only include:
    - Object types with a current version
    - Link types where both source and target objects exist
    """
    return ontology_crud.get_topology_data(session)


# ==========================================
# Actions & Logic
# ==========================================

@router.get("/actions/with-functions", response_model=List[ActionDefWithFunction])
def list_actions_with_functions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """
    List all action definitions with resolved function details.
    
    Returns actions with their bound function's api_name and display_name.
    Used by the Actions & Logic page.
    """
    return meta_crud.list_actions_with_functions(session, skip=skip, limit=limit)


@router.get("/functions/for-list", response_model=List[FunctionDefForList])
def list_functions_for_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """
    List all function definitions for display.
    
    Returns functions with code_content for drawer preview.
    Used by the Actions & Logic page.
    """
    return meta_crud.list_functions_for_list(session, skip=skip, limit=limit)


# ==========================================
# Action Execution
# ==========================================

class ActionExecuteRequest(BaseModel):
    """Request body for action execution."""
    params: Dict[str, Any] = {}
    project_id: Optional[str] = "default-project"


class ActionExecuteResponse(BaseModel):
    """Response for action execution."""
    success: bool
    result: Any = None
    execution_time_ms: int
    log_id: str
    stdout: Optional[str] = None
    error_message: Optional[str] = None


@router.get("/actions/{action_id}/details")
def get_action_details(
    action_id: str,
    session: Session = Depends(get_session)
):
    """
    Get action details including input parameters schema.
    
    Returns action with its bound function's input_params_schema
    for dynamic form rendering.
    """
    from sqlmodel import select
    from app.models.meta import ActionDefinition, FunctionDefinition
    
    # Get action
    action = session.get(ActionDefinition, action_id)
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action not found: {action_id}"
        )
    
    # Get bound function
    function = session.get(FunctionDefinition, action.backing_function_id)
    
    return {
        "id": action.id,
        "api_name": action.api_name,
        "display_name": action.display_name,
        "backing_function_id": action.backing_function_id,
        "function_api_name": function.api_name if function else None,
        "function_display_name": function.display_name if function else None,
        "input_params_schema": function.input_params_schema if function else None,
    }


@router.post("/actions/{action_id}/execute", response_model=ActionExecuteResponse)
def execute_action(
    action_id: str,
    request: ActionExecuteRequest,
    session: Session = Depends(get_session)
):
    """
    Execute an action and log the result.
    
    1. Finds the ActionDefinition by ID
    2. Gets the bound FunctionDefinition
    3. Executes the function code using function_runner
    4. Logs the execution to sys_action_log
    5. Returns the result
    """
    from sqlmodel import select
    from app.models.meta import ActionDefinition, FunctionDefinition
    from app.models.data import ExecutionLog
    from app.engine.function_runner import execute_code_direct
    
    start_time = time.time()
    log_id = str(uuid.uuid4())
    
    logger.info(f"Executing action: {action_id}")
    logger.debug(f"Execution params: {request.params}")
    
    # Step 1: Get ActionDefinition
    action = session.get(ActionDefinition, action_id)
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action not found: {action_id}"
        )
    
    # Step 2: Get bound FunctionDefinition
    function = session.get(FunctionDefinition, action.backing_function_id)
    if not function:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bound function not found: {action.backing_function_id}"
        )
    
    if not function.code_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Function '{function.api_name}' has no code content"
        )
    
    logger.info(f"Executing function: {function.api_name}")
    
    # Step 3: Execute the function code
    execution_result = execute_code_direct(
        code_content=function.code_content,
        context=request.params,
        session=session
    )
    
    execution_time_ms = int((time.time() - start_time) * 1000)
    
    # Step 4: Log execution to sys_action_log
    execution_log = ExecutionLog(
        id=log_id,
        project_id=request.project_id or "default-project",
        action_def_id=action_id,
        trigger_user_id=None,  # Could be extracted from auth context
        input_params=request.params,
        execution_status="SUCCESS" if execution_result.success else "FAILED",
        error_message=execution_result.error_message,
        duration_ms=execution_time_ms,
        created_at=datetime.utcnow()
    )
    
    session.add(execution_log)
    session.commit()
    
    logger.info(f"Action execution logged: {log_id} | Status: {execution_log.execution_status} | Duration: {execution_time_ms}ms")
    
    # Step 5: Return response
    if execution_result.success:
        return ActionExecuteResponse(
            success=True,
            result=execution_result.result,
            execution_time_ms=execution_time_ms,
            log_id=log_id,
            stdout=execution_result.stdout if execution_result.stdout else None,
        )
    else:
        return ActionExecuteResponse(
            success=False,
            result=None,
            execution_time_ms=execution_time_ms,
            log_id=log_id,
            stdout=execution_result.stdout if execution_result.stdout else None,
            error_message=execution_result.error_message,
        )
