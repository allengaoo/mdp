"""
Ontology API endpoints for Meta Layer entities.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.core.db import get_session
from app.engine import meta_crud
from app.models.meta import (
    ObjectTypeCreate, ObjectTypeUpdate, ObjectTypeRead,
    LinkTypeCreate, LinkTypeUpdate, LinkTypeRead,
    FunctionDefinitionCreate, FunctionDefinitionUpdate, FunctionDefinitionRead,
    ActionDefinitionCreate, ActionDefinitionUpdate, ActionDefinitionRead,
    SharedPropertyCreate, SharedPropertyUpdate, SharedPropertyRead,
    ProjectCreate, ProjectRead
)
from app.schemas.api_payloads import ObjectTypeRequest, LinkTypeRequest, ProjectResponse
from app.models.data import (
    DataSourceTableCreate, DataSourceTableRead
)
from app.engine import instance_crud

router = APIRouter(tags=["meta"])


# ==========================================
# ObjectType Endpoints
# ==========================================

@router.post("/object-types", response_model=ObjectTypeRead, status_code=status.HTTP_201_CREATED)
def create_object_type(
    request: ObjectTypeRequest,
    session: Session = Depends(get_session)
):
    """Create a new ObjectType."""
    try:
        # Convert property_schema from List[PropertyDef] to Dict[str, Any]
        property_schema_dict = {}
        for prop in request.property_schema:
            property_schema_dict[prop.key] = {
                "label": prop.label,
                "type": prop.type,
                "required": prop.required,
            }
            if prop.shared_property_id:
                property_schema_dict[prop.key]["shared_property_id"] = prop.shared_property_id
        
        # Create ObjectTypeCreate from request
        obj_in = ObjectTypeCreate(
            api_name=request.api_name,
            display_name=request.display_name,
            description=request.description,
            project_id=request.project_id,
            property_schema=property_schema_dict if property_schema_dict else None
        )
        
        return meta_crud.create_object_type(session, obj_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create ObjectType: {str(e)}"
        )


@router.get("/object-types", response_model=List[ObjectTypeRead])
def list_object_types(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
):
    """List all ObjectTypes."""
    return meta_crud.list_object_types(session, skip=skip, limit=limit)


@router.get("/object-types/{obj_id}", response_model=ObjectTypeRead)
def get_object_type(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Get ObjectType by ID."""
    db_obj = meta_crud.get_object_type(session, obj_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ObjectType not found: {obj_id}"
        )
    return db_obj


@router.put("/object-types/{obj_id}", response_model=ObjectTypeRead)
def update_object_type(
    obj_id: str,
    obj_in: ObjectTypeUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing ObjectType."""
    try:
        db_obj = meta_crud.update_object_type(session, obj_id, obj_in)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ObjectType not found: {obj_id}"
            )
        return db_obj
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update ObjectType: {str(e)}"
        )


@router.delete("/object-types/{obj_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_object_type(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Delete ObjectType by ID."""
    success = meta_crud.delete_object_type(session, obj_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ObjectType not found: {obj_id}"
        )
    return None


# ==========================================
# LinkType Endpoints
# ==========================================

@router.post("/link-types", response_model=LinkTypeRead, status_code=status.HTTP_201_CREATED)
def create_link_type(
    request: LinkTypeRequest,
    session: Session = Depends(get_session)
):
    """Create a new LinkType."""
    try:
        # Create LinkTypeCreate from request
        # Note: mapping_config is stored separately or can be added to LinkType model later
        obj_in = LinkTypeCreate(
            api_name=request.api_name,
            display_name=request.display_name or request.api_name,
            source_type_id=request.source_type_id,
            target_type_id=request.target_type_id,
            cardinality=request.cardinality
        )
        
        # TODO: Store mapping_config if LinkType model is extended with a JSON field
        # For now, mapping_config is accepted but not persisted
        
        return meta_crud.create_link_type(session, obj_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create LinkType: {str(e)}"
        )


@router.get("/link-types", response_model=List[LinkTypeRead])
def list_link_types(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
):
    """List all LinkTypes."""
    return meta_crud.list_link_types(session, skip=skip, limit=limit)


@router.get("/link-types/{obj_id}", response_model=LinkTypeRead)
def get_link_type(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Get LinkType by ID."""
    db_obj = meta_crud.get_link_type(session, obj_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LinkType not found: {obj_id}"
        )
    return db_obj


@router.put("/link-types/{obj_id}", response_model=LinkTypeRead)
def update_link_type(
    obj_id: str,
    obj_in: LinkTypeUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing LinkType."""
    try:
        db_obj = meta_crud.update_link_type(session, obj_id, obj_in)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LinkType not found: {obj_id}"
            )
        return db_obj
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update LinkType: {str(e)}"
        )


@router.delete("/link-types/{obj_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link_type(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Delete LinkType by ID."""
    success = meta_crud.delete_link_type(session, obj_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LinkType not found: {obj_id}"
        )
    return None


# ==========================================
# FunctionDefinition Endpoints
# ==========================================

@router.post("/functions", response_model=FunctionDefinitionRead, status_code=status.HTTP_201_CREATED)
def create_function_definition(
    obj_in: FunctionDefinitionCreate,
    session: Session = Depends(get_session)
):
    """Create a new FunctionDefinition."""
    try:
        return meta_crud.create_function_definition(session, obj_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create FunctionDefinition: {str(e)}"
        )


@router.get("/functions", response_model=List[FunctionDefinitionRead])
def list_function_definitions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
):
    """List all FunctionDefinitions."""
    return meta_crud.list_function_definitions(session, skip=skip, limit=limit)


@router.get("/functions/{obj_id}", response_model=FunctionDefinitionRead)
def get_function_definition(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Get FunctionDefinition by ID."""
    db_obj = meta_crud.get_function_definition(session, obj_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FunctionDefinition not found: {obj_id}"
        )
    return db_obj


@router.put("/functions/{obj_id}", response_model=FunctionDefinitionRead)
def update_function_definition(
    obj_id: str,
    obj_in: FunctionDefinitionUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing FunctionDefinition."""
    db_obj = meta_crud.update_function_definition(session, obj_id, obj_in)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FunctionDefinition not found: {obj_id}"
        )
    return db_obj


@router.delete("/functions/{obj_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_function_definition(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Delete FunctionDefinition by ID."""
    success = meta_crud.delete_function_definition(session, obj_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FunctionDefinition not found: {obj_id}"
        )
    return None


# ==========================================
# ActionDefinition Endpoints
# ==========================================

@router.post("/actions", response_model=ActionDefinitionRead, status_code=status.HTTP_201_CREATED)
def create_action_definition(
    obj_in: ActionDefinitionCreate,
    session: Session = Depends(get_session)
):
    """Create a new ActionDefinition."""
    try:
        return meta_crud.create_action_definition(session, obj_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create ActionDefinition: {str(e)}"
        )


@router.get("/actions", response_model=List[ActionDefinitionRead])
def list_action_definitions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
):
    """List all ActionDefinitions."""
    return meta_crud.list_action_definitions(session, skip=skip, limit=limit)


@router.get("/actions/{obj_id}", response_model=ActionDefinitionRead)
def get_action_definition(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Get ActionDefinition by ID."""
    db_obj = meta_crud.get_action_definition(session, obj_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ActionDefinition not found: {obj_id}"
        )
    return db_obj


@router.put("/actions/{obj_id}", response_model=ActionDefinitionRead)
def update_action_definition(
    obj_id: str,
    obj_in: ActionDefinitionUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing ActionDefinition."""
    db_obj = meta_crud.update_action_definition(session, obj_id, obj_in)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ActionDefinition not found: {obj_id}"
        )
    return db_obj


@router.delete("/actions/{obj_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action_definition(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Delete ActionDefinition by ID."""
    success = meta_crud.delete_action_definition(session, obj_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ActionDefinition not found: {obj_id}"
        )
    return None


# ActionDefinition 别名路由（兼容前端使用的 /action-definitions）
@router.post("/action-definitions", response_model=ActionDefinitionRead, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_action_definition_alias(
    obj_in: ActionDefinitionCreate,
    session: Session = Depends(get_session)
):
    """Alias for create_action_definition."""
    return create_action_definition(obj_in, session)


@router.get("/action-definitions", response_model=List[ActionDefinitionRead], include_in_schema=False)
def list_action_definitions_alias(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
):
    """Alias for list_action_definitions."""
    return list_action_definitions(skip, limit, session)


@router.get("/action-definitions/{obj_id}", response_model=ActionDefinitionRead, include_in_schema=False)
def get_action_definition_alias(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Alias for get_action_definition."""
    return get_action_definition(obj_id, session)


@router.put("/action-definitions/{obj_id}", response_model=ActionDefinitionRead, include_in_schema=False)
def update_action_definition_alias(
    obj_id: str,
    obj_in: ActionDefinitionUpdate,
    session: Session = Depends(get_session)
):
    """Alias for update_action_definition."""
    return update_action_definition(obj_id, obj_in, session)


@router.delete("/action-definitions/{obj_id}", status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
def delete_action_definition_alias(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Alias for delete_action_definition."""
    return delete_action_definition(obj_id, session)


# ==========================================
# SharedProperty Endpoints
# ==========================================

@router.post("/shared-properties", response_model=SharedPropertyRead, status_code=status.HTTP_201_CREATED)
def create_shared_property(
    obj_in: SharedPropertyCreate,
    session: Session = Depends(get_session)
):
    """Create a new SharedProperty."""
    try:
        return meta_crud.create_shared_property(session, obj_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create SharedProperty: {str(e)}"
        )


@router.get("/shared-properties", response_model=List[SharedPropertyRead])
def list_shared_properties(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
):
    """List all SharedProperties."""
    return meta_crud.list_shared_properties(session, skip=skip, limit=limit)


@router.get("/shared-properties/{obj_id}", response_model=SharedPropertyRead)
def get_shared_property(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Get SharedProperty by ID."""
    obj = meta_crud.get_shared_property(session, obj_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SharedProperty not found: {obj_id}"
        )
    return obj


@router.put("/shared-properties/{obj_id}", response_model=SharedPropertyRead)
def update_shared_property(
    obj_id: str,
    obj_in: SharedPropertyUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing SharedProperty."""
    try:
        db_obj = meta_crud.update_shared_property(session, obj_id, obj_in)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SharedProperty not found: {obj_id}"
            )
        return db_obj
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update SharedProperty: {str(e)}"
        )


@router.delete("/shared-properties/{obj_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shared_property(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Delete SharedProperty by ID."""
    success = meta_crud.delete_shared_property(session, obj_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SharedProperty not found: {obj_id}"
        )
    return None


# ==========================================
# DataSourceTable Endpoints
# ==========================================

@router.post("/datasource-tables", response_model=DataSourceTableRead, status_code=status.HTTP_201_CREATED)
def create_datasource_table(
    obj_in: DataSourceTableCreate,
    session: Session = Depends(get_session)
):
    """Create a new DataSourceTable."""
    try:
        return instance_crud.create_datasource_table(session, obj_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create DataSourceTable: {str(e)}"
        )


@router.get("/datasource-tables", response_model=List[DataSourceTableRead])
def list_datasource_tables(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
):
    """List all DataSourceTables."""
    return instance_crud.list_datasource_tables(session, skip=skip, limit=limit)


@router.get("/datasources", response_model=List[DataSourceTableRead])
def list_datasources(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
):
    """List all DataSourceTables (alias for /datasource-tables)."""
    return instance_crud.list_datasource_tables(session, skip=skip, limit=limit)


@router.get("/datasource-tables/{obj_id}", response_model=DataSourceTableRead)
def get_datasource_table(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Get DataSourceTable by ID."""
    obj = instance_crud.get_datasource_table(session, obj_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DataSourceTable not found: {obj_id}"
        )
    return obj


@router.get("/datasource-tables/name/{table_name}", response_model=DataSourceTableRead)
def get_datasource_table_by_name(
    table_name: str,
    session: Session = Depends(get_session)
):
    """Get DataSourceTable by table name."""
    obj = instance_crud.get_datasource_table_by_name(session, table_name)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DataSourceTable not found: {table_name}"
        )
    return obj


@router.delete("/datasource-tables/{obj_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_datasource_table(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Delete DataSourceTable by ID."""
    success = instance_crud.delete_datasource_table(session, obj_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DataSourceTable not found: {obj_id}"
        )
    return None


# ==========================================
# Project Endpoints
# ==========================================

@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
):
    """List all Projects with aggregated statistics (objectCount, linkCount)."""
    projects_data = meta_crud.list_projects_with_stats(session, skip=skip, limit=limit)
    return [ProjectResponse(**project) for project in projects_data]


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    obj_in: ProjectCreate,
    session: Session = Depends(get_session)
):
    """Create a new Project."""
    try:
        db_obj = meta_crud.create_project(session, obj_in)
        return db_obj
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create Project: {str(e)}"
        )


@router.get("/projects/{obj_id}", response_model=ProjectRead)
def get_project(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Get Project by ID."""
    db_obj = meta_crud.get_project(session, obj_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {obj_id}"
        )
    return db_obj


@router.put("/projects/{obj_id}", response_model=ProjectRead)
def update_project(
    obj_id: str,
    obj_in: ProjectCreate,
    session: Session = Depends(get_session)
):
    """Update an existing Project."""
    try:
        db_obj = meta_crud.update_project(session, obj_id, obj_in)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {obj_id}"
            )
        return db_obj
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update Project: {str(e)}"
        )


@router.delete("/projects/{obj_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    obj_id: str,
    session: Session = Depends(get_session)
):
    """Delete Project by ID."""
    try:
        success = meta_crud.delete_project(session, obj_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {obj_id}"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
