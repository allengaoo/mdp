"""
Runtime operations API endpoints: Action execution and data querying.

增强版本支持：
- 代码试运行（不保存状态）
- 函数试运行
- 执行日志查询
"""
from typing import List, Optional, Dict, Any, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from pydantic import BaseModel

from app.core.db import get_session
from app.engine import meta_crud, instance_crud, function_runner
from app.engine.code_executor import (
    execute_code, try_function_code, execute_function_by_id,
    CodeExecutionRequest, CodeExecutionResponse, ExecutorType
)
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


class CodeTestRequest(BaseModel):
    """Request model for testing code execution."""
    code_content: str
    context: Optional[Dict[str, Any]] = None
    executor_type: Literal["auto", "builtin", "subprocess"] = "auto"
    timeout_seconds: int = 30


class CodeTestResponse(BaseModel):
    """Response model for code test execution."""
    success: bool
    result: Any
    stdout: str
    stderr: str
    execution_time_ms: int
    executor_used: str
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    traceback: Optional[str] = None


class FunctionTestRequest(BaseModel):
    """Request model for testing function execution."""
    context: Optional[Dict[str, Any]] = None
    executor_type: Literal["auto", "builtin", "subprocess"] = "auto"
    timeout_seconds: int = 30


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
    6. Log execution result
    7. Return result
    """
    import time
    start_time = time.time()
    action_def = None
    source_id = None
    error_message = None
    execution_status = "SUCCESS"
    
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
        
        # Step 6: Log execution (success)
        duration_ms = int((time.time() - start_time) * 1000)
        try:
            # Get project_id from action_def or use a default
            project_id = getattr(action_def, 'project_id', None) or "default"
            # Combine source_id and params into input_params
            input_params = {"source_id": source_id, **(request.params or {})}
            instance_crud.create_execution_log(
                session=session,
                project_id=project_id,
                action_def_id=action_def.id,
                execution_status="SUCCESS",
                duration_ms=duration_ms,
                input_params=input_params
            )
        except Exception as log_error:
            logger.warning(f"Failed to log execution: {log_error}")
        
        # Step 7: Return result
        return ActionRunResponse(
            success=True,
            result=result,
            action_api_name=request.action_api_name,
            source_id=request.effective_source_id or "",
            message="Action executed successfully"
        )
        
    except HTTPException as http_exc:
        # Log execution (failed)
        execution_status = "FAILED"
        error_message = http_exc.detail
        duration_ms = int((time.time() - start_time) * 1000)
        if action_def:
            try:
                project_id = getattr(action_def, 'project_id', None) or "default"
                input_params = {"source_id": source_id, **(request.params or {})}
                instance_crud.create_execution_log(
                    session=session,
                    project_id=project_id,
                    action_def_id=action_def.id,
                    execution_status="FAILED",
                    duration_ms=duration_ms,
                    error_message=str(error_message),
                    input_params=input_params
                )
            except Exception as log_error:
                logger.warning(f"Failed to log execution: {log_error}")
        raise
    except ValueError as e:
        # Handle ValueError from function_runner (e.g., function not found)
        execution_status = "FAILED"
        error_message = str(e)
        duration_ms = int((time.time() - start_time) * 1000)
        if action_def:
            try:
                project_id = getattr(action_def, 'project_id', None) or "default"
                input_params = {"source_id": source_id, **(request.params or {})}
                instance_crud.create_execution_log(
                    session=session,
                    project_id=project_id,
                    action_def_id=action_def.id,
                    execution_status="FAILED",
                    duration_ms=duration_ms,
                    error_message=error_message,
                    input_params=input_params
                )
            except Exception as log_error:
                logger.warning(f"Failed to log execution: {log_error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SyntaxError as e:
        # Handle syntax errors in function code
        execution_status = "FAILED"
        error_message = f"Syntax error in function code: {str(e)}"
        duration_ms = int((time.time() - start_time) * 1000)
        if action_def:
            try:
                project_id = getattr(action_def, 'project_id', None) or "default"
                input_params = {"source_id": source_id, **(request.params or {})}
                instance_crud.create_execution_log(
                    session=session,
                    project_id=project_id,
                    action_def_id=action_def.id,
                    execution_status="FAILED",
                    duration_ms=duration_ms,
                    error_message=error_message,
                    input_params=input_params
                )
            except Exception as log_error:
                logger.warning(f"Failed to log execution: {log_error}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_message
        )
    except Exception as e:
        # Handle other runtime errors
        execution_status = "FAILED"
        error_message = f"Action execution failed: {str(e)}"
        duration_ms = int((time.time() - start_time) * 1000)
        if action_def:
            try:
                project_id = getattr(action_def, 'project_id', None) or "default"
                input_params = {"source_id": source_id, **(request.params or {})}
                instance_crud.create_execution_log(
                    session=session,
                    project_id=project_id,
                    action_def_id=action_def.id,
                    execution_status="FAILED",
                    duration_ms=duration_ms,
                    error_message=error_message,
                    input_params=input_params
                )
            except Exception as log_error:
                logger.warning(f"Failed to log execution: {log_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )


# ==========================================
# Execution Log Endpoints
# ==========================================

@router.get("/logs", response_model=List[Dict[str, Any]])
def list_execution_logs(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    action_id: Optional[str] = Query(None, description="Filter by action definition ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (SUCCESS/FAILED)"),
    exec_status: Optional[str] = Query(None, description="Alternative filter by status (SUCCESS/FAILED)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """
    Query execution logs with optional filters.
    
    Query Parameters:
    - project_id: Optional filter by project ID
    - action_id: Optional filter by action definition ID
    - status: Optional filter by execution status (SUCCESS/FAILED)
    - exec_status: Alternative filter by execution status (SUCCESS/FAILED)
    - skip: Pagination offset (default: 0)
    - limit: Pagination limit (default: 100, max: 1000)
    
    Returns:
    - List of execution log records with action_name resolved from ActionDefinition
    """
    try:
        # Support both status and exec_status parameters
        effective_status = status_filter or exec_status
        
        logs = instance_crud.list_execution_logs(
            session=session,
            project_id=project_id,
            action_def_id=action_id,
            status=effective_status,
            skip=skip,
            limit=limit
        )
        
        # Convert to response format with action_name
        result = []
        for log in logs:
            # Get action name from ActionDefinition
            action_name = None
            try:
                action_def = meta_crud.get_action_definition(session, log.action_def_id)
                if action_def:
                    action_name = action_def.display_name
            except Exception:
                pass
            
            log_dict = {
                "id": log.id,
                "project_id": log.project_id,
                "action_id": log.action_def_id,
                "action_name": action_name or log.action_def_id,
                "trigger_user_id": log.trigger_user_id,
                "status": log.execution_status,
                "duration_ms": log.duration_ms,
                "error_message": log.error_message,
                "input_params": log.input_params,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            result.append(log_dict)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query execution logs: {str(e)}"
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


# ==========================================
# Code Execution Test Endpoints
# ==========================================

@router.post("/code/test", response_model=CodeTestResponse, status_code=status.HTTP_200_OK)
def test_code_execution(
    request: CodeTestRequest,
    session: Session = Depends(get_session)
):
    """
    测试运行代码（不保存状态）
    
    用于前端代码编辑器的试运行功能。
    
    Request Body:
    - code_content: Python 代码字符串（必须定义 main(context) 函数）
    - context: 传递给 main 函数的上下文数据（可选）
    - executor_type: 执行器类型 - "auto"（自动选择）、"builtin"（内置）、"subprocess"（子进程）
    - timeout_seconds: 执行超时时间（秒，默认30）
    
    Example Request:
    ```json
    {
        "code_content": "def main(ctx):\\n    return ctx.get('x', 0) * 2",
        "context": {"x": 5},
        "executor_type": "auto",
        "timeout_seconds": 30
    }
    ```
    
    Example Response:
    ```json
    {
        "success": true,
        "result": 10,
        "stdout": "",
        "stderr": "",
        "execution_time_ms": 15,
        "executor_used": "builtin",
        "error_message": null,
        "error_type": null,
        "traceback": null
    }
    ```
    """
    logger.info(f"Testing code execution, executor_type={request.executor_type}")
    
    try:
        # 映射执行器类型
        executor_map = {
            "auto": ExecutorType.AUTO,
            "builtin": ExecutorType.BUILTIN,
            "subprocess": ExecutorType.SUBPROCESS
        }
        executor_type = executor_map.get(request.executor_type, ExecutorType.AUTO)
        
        # 执行代码
        result = try_function_code(
            code_content=request.code_content,
            context=request.context,
            session=session,
            executor_type=executor_type,
            timeout_seconds=request.timeout_seconds
        )
        
        return CodeTestResponse(
            success=result.success,
            result=result.result,
            stdout=result.stdout,
            stderr=result.stderr,
            execution_time_ms=result.execution_time_ms,
            executor_used=result.executor_used,
            error_message=result.error_message,
            error_type=result.error_type,
            traceback=result.traceback
        )
        
    except Exception as e:
        logger.error(f"Code test execution failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code test execution failed: {str(e)}"
        )


@router.post("/function/{function_id}/test", response_model=CodeTestResponse, status_code=status.HTTP_200_OK)
def test_function_execution(
    function_id: str,
    request: FunctionTestRequest,
    session: Session = Depends(get_session)
):
    """
    测试运行已保存的函数（不保存状态）
    
    根据函数 ID 获取代码并执行。
    
    Path Parameters:
    - function_id: FunctionDefinition 的 ID
    
    Request Body:
    - context: 传递给 main 函数的上下文数据（可选）
    - executor_type: 执行器类型
    - timeout_seconds: 执行超时时间
    
    Example:
    POST /execute/function/30000000-0000-0000-0000-000000000001/test
    ```json
    {
        "context": {
            "source": {"id": "xxx", "properties": {"fuel": 80}}
        }
    }
    ```
    """
    logger.info(f"Testing function execution: {function_id}")
    
    try:
        # 映射执行器类型
        executor_map = {
            "auto": ExecutorType.AUTO,
            "builtin": ExecutorType.BUILTIN,
            "subprocess": ExecutorType.SUBPROCESS
        }
        executor_type = executor_map.get(request.executor_type, ExecutorType.AUTO)
        
        # 执行函数
        result = execute_function_by_id(
            session=session,
            function_id=function_id,
            context=request.context or {},
            executor_type=executor_type,
            timeout_seconds=request.timeout_seconds
        )
        
        return CodeTestResponse(
            success=result.success,
            result=result.result,
            stdout=result.stdout,
            stderr=result.stderr,
            execution_time_ms=result.execution_time_ms,
            executor_used=result.executor_used,
            error_message=result.error_message,
            error_type=result.error_type,
            traceback=result.traceback
        )
        
    except Exception as e:
        logger.error(f"Function test execution failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function test execution failed: {str(e)}"
        )


@router.post("/code/validate", status_code=status.HTTP_200_OK)
def validate_code_syntax(
    request: CodeTestRequest
):
    """
    验证代码语法（不执行）
    
    快速检查代码是否有语法错误。
    
    Request Body:
    - code_content: Python 代码字符串
    
    Returns:
    - valid: 是否有效
    - error_message: 错误信息（如果无效）
    - error_line: 错误行号（如果有）
    """
    from app.engine.function_runner import validate_syntax
    
    is_valid, error_message = validate_syntax(request.code_content)
    
    return {
        "valid": is_valid,
        "error_message": error_message
    }
