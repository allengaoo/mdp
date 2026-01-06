"""
Runtime operations API endpoints: Action execution and data querying.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from pydantic import BaseModel

from app.core.db import get_session
from app.engine import meta_crud, instance_crud, function_runner
from app.core.logger import logger
from app.models.meta import ObjectType, Project
from app.schemas.api_payloads import ActionRunRequest

router = APIRouter(prefix="/execute", tags=["execute"])


# ==========================================
# Request/Response Models
# ==========================================


class ActionRunResponse(BaseModel):
    """Response model for action execution."""
    success: bool
    result: Any
    action_api_name: str
    source_id: str
    message: Optional[str] = None


class ObjectCreateRequest(BaseModel):
    """Request model for creating object instance."""
    properties: Optional[Dict[str, Any]] = None


# ==========================================
# Action Execution Endpoint
# ==========================================

@router.post("/action/run", response_model=ActionRunResponse, status_code=status.HTTP_200_OK)
def run_action(
    request: ActionRunRequest,
    session: Session = Depends(get_session)
):
    """
    Execute an action by its api_name.
    
    Steps:
    1. Lookup ActionDefinition by api_name to get backing_function_id
    2. Fetch source ObjectInstance by source_id
    3. Build context dictionary
    4. Call function_runner.execute_function
    5. Persist updates if result contains "updates" key
    6. Return result
    """
    try:
        # Step 1: Lookup ActionDefinition by api_name
        action_def = meta_crud.get_action_definition_by_name(session, request.action_api_name)
        if not action_def:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ActionDefinition not found: {request.action_api_name}"
            )
        
        # Step 2: Fetch source ObjectInstance
        source_id = request.effective_source_id
        if not source_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="source_object_id or source_id is required"
            )
        
        source_obj = instance_crud.get_object(session, source_id)
        if not source_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ObjectInstance not found: {source_id}"
            )
        
        # Step 3: Build context dictionary
        context = {
            "source": {
                "id": source_obj.id,
                "object_type_id": source_obj.object_type_id,
                "properties": source_obj.properties or {}
            },
            "params": request.params or {}
        }
        
        # Step 4: Execute the function
        function_id = action_def.backing_function_id
        result = function_runner.execute_function(
            session=session,
            function_id=function_id,
            context=context
        )
        
        # Step 5: Persist updates if result contains "updates" key
        if isinstance(result, dict) and "updates" in result:
            updates = result.get("updates", [])
            if isinstance(updates, list):
                for update in updates:
                    if isinstance(update, dict) and "id" in update:
                        obj_id = update["id"]
                        properties_patch = update.get("properties", {})
                        if properties_patch:
                            updated_obj = instance_crud.update_object(
                                session=session,
                                obj_id=obj_id,
                                properties_patch=properties_patch
                            )
                            if not updated_obj:
                                logger.warning(f"Failed to update object {obj_id} from action result")
        
        # Step 6: Return result
        return ActionRunResponse(
            success=True,
            result=result,
            action_api_name=request.action_api_name,
            source_id=request.effective_source_id or "",
            message="Action executed successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (404, etc.)
        raise
    except ValueError as e:
        # Handle ValueError from function_runner (e.g., function not found)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SyntaxError as e:
        # Handle syntax errors in function code
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Syntax error in function code: {str(e)}"
        )
    except Exception as e:
        # Handle other runtime errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Action execution failed: {str(e)}"
        )


# ==========================================
# Data Query Endpoints
# ==========================================

@router.get("/objects/{type_api_name}", response_model=List[Dict[str, Any]])
def list_objects_by_type(
    type_api_name: str,
    filters: Optional[str] = Query(None, description="JSON string for property filters, e.g., '{\"status\": \"Ready\", \"fuel\": 80}'"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """
    Query objects by type api_name with optional JSON property filters.
    
    Query Parameters:
    - type_api_name: The api_name of the ObjectType (e.g., "fighter")
    - filters: Optional JSON string for property filters (e.g., '{"status": "Ready", "fuel": 80}')
    - skip: Pagination offset (default: 0)
    - limit: Pagination limit (default: 100, max: 1000)
    
    Example:
    GET /execute/objects/fighter?filters={"status":"Ready","fuel":80}
    """
    import json
    try:
        # Step 1: Resolve type_api_name to type_id
        object_type = meta_crud.get_object_type_by_name(session, type_api_name)
        if not object_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ObjectType not found: {type_api_name}"
            )
        
        # Step 2: Parse filter_criteria from JSON string
        filter_criteria = None
        if filters:
            try:
                filter_criteria = json.loads(filters)
                if not isinstance(filter_criteria, dict):
                    raise ValueError("Filters must be a JSON object")
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid JSON in filters parameter: {str(e)}"
                )
        
        # Step 3: Call instance_crud.list_objects
        objects = instance_crud.list_objects(
            session=session,
            type_id=object_type.id,
            filter_criteria=filter_criteria,
            skip=skip,
            limit=limit
        )
        
        # Step 4: Convert to JSON-serializable format
        result = []
        for obj in objects:
            obj_dict = {
                "id": obj.id,
                "object_type_id": obj.object_type_id,
                "properties": obj.properties or {},
                "created_at": obj.created_at.isoformat() if obj.created_at else None,
                "updated_at": obj.updated_at.isoformat() if obj.updated_at else None
            }
            result.append(obj_dict)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query objects: {str(e)}"
        )


@router.post("/objects/{type_api_name}", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_object_by_type(
    type_api_name: str,
    request: ObjectCreateRequest,
    session: Session = Depends(get_session)
):
    """
    Create a new ObjectInstance by type api_name.
    
    This endpoint allows creating object instances directly via API,
    useful for initial data loading or programmatic instance creation.
    """
    try:
        # Step 1: Resolve type_api_name to type_id
        object_type = meta_crud.get_object_type_by_name(session, type_api_name)
        if not object_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ObjectType not found: {type_api_name}"
            )
        
        # Step 2: Call instance_crud.create_object
        obj = instance_crud.create_object(
            session=session,
            type_id=object_type.id,
            properties=request.properties
        )
        
        # Step 3: Convert to JSON-serializable format
        return {
            "id": obj.id,
            "object_type_id": obj.object_type_id,
            "properties": obj.properties or {},
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create object: {str(e)}"
        )


# ==========================================
# Link Query Endpoints
# ==========================================

@router.get("/links", response_model=List[Dict[str, Any]])
def list_links(
    source_id: Optional[str] = Query(None, description="Filter by source instance ID"),
    target_id: Optional[str] = Query(None, description="Filter by target instance ID"),
    link_type_id: Optional[str] = Query(None, description="Filter by link type ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """
    Query link instances with optional filters.
    
    Query Parameters:
    - source_id: Optional filter by source instance ID
    - target_id: Optional filter by target instance ID
    - link_type_id: Optional filter by link type ID
    - skip: Pagination offset (default: 0)
    - limit: Pagination limit (default: 100, max: 1000)
    
    Example:
    GET /execute/links?source_id=xxx
    GET /execute/links?target_id=yyy&link_type_id=zzz
    """
    try:
        links = instance_crud.list_links(
            session=session,
            source_id=source_id,
            target_id=target_id,
            link_type_id=link_type_id,
            skip=skip,
            limit=limit
        )
        
        # Convert to JSON-serializable format
        result = []
        for link in links:
            link_dict = {
                "id": link.id,
                "link_type_id": link.link_type_id,
                "source_instance_id": link.source_instance_id,
                "target_instance_id": link.target_instance_id,
                "properties": link.properties or {},
                "created_at": link.created_at.isoformat() if link.created_at else None
            }
            result.append(link_dict)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query links: {str(e)}"
        )


# ==========================================
# Physical Properties Endpoint
# ==========================================

@router.get("/project/{project_id}/physical-properties")
def get_physical_properties(
    project_id: str,
    session: Session = Depends(get_session)
):
    """
    Get physical properties for a project.
    Physical properties are aggregated from all ObjectTypes' property_schema in the project.
    """
    try:
        # Verify project exists
        project = session.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        # Get all ObjectTypes for this project
        object_types = meta_crud.list_object_types(session, skip=0, limit=1000)
        project_object_types = [ot for ot in object_types if ot.project_id == project_id]
        
        # Aggregate property schemas
        physical_properties = {}
        for obj_type in project_object_types:
            if obj_type.property_schema:
                # property_schema is a dict like {"fuel": "number", "status": "string"}
                for prop_key, prop_type in obj_type.property_schema.items():
                    if prop_key not in physical_properties:
                        physical_properties[prop_key] = {
                            "key": prop_key,
                            "type": prop_type,
                            "used_in": []
                        }
                    physical_properties[prop_key]["used_in"].append({
                        "object_type_id": obj_type.id,
                        "object_type_api_name": obj_type.api_name,
                        "object_type_display_name": obj_type.display_name
                    })
        
        # Convert to list format
        result = list(physical_properties.values())
        
        logger.info(f"Retrieved {len(result)} physical properties for project {project_id}")
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "physical_properties": result,
            "count": len(result)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get physical properties for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get physical properties: {str(e)}"
        )
