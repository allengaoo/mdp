"""
Mapping API endpoints for MDP Platform V3.1
Multimodal data mapping and vector indexing.
"""
import uuid
import random
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session
from sqlalchemy import create_engine, text

from app.core.db import get_session
from app.core.config import settings
from app.core.logger import logger
from app.engine.v3 import mapping_crud
from app.models.context import (
    ObjectMappingDef,
    ObjectMappingDefCreate,
    ObjectMappingDefUpdate,
    ObjectMappingDefRead,
    MappingPreviewRequest,
    MappingPreviewResponse,
    ObjectInstanceLineage,
    ObjectInstanceLineageRead,
    LineageLookupResponse,
)

router = APIRouter(prefix="/mappings", tags=["Mappings"])


# ==========================================
# CRUD Endpoints
# ==========================================

@router.post("", response_model=ObjectMappingDefRead)
def create_mapping(
    data: ObjectMappingDefCreate,
    session: Session = Depends(get_session)
):
    """Create a new mapping definition."""
    mapping = mapping_crud.create_mapping(session, data)
    return mapping


@router.get("", response_model=List[ObjectMappingDefRead])
def list_mappings(
    object_def_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List mapping definitions with optional filters."""
    return mapping_crud.list_mappings(session, object_def_id, status, skip, limit)


@router.get("/{mapping_id}", response_model=ObjectMappingDefRead)
def get_mapping(
    mapping_id: str,
    session: Session = Depends(get_session)
):
    """Get a mapping by ID."""
    mapping = mapping_crud.get_mapping(session, mapping_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return mapping


@router.put("/{mapping_id}", response_model=ObjectMappingDefRead)
def update_mapping(
    mapping_id: str,
    data: ObjectMappingDefUpdate,
    session: Session = Depends(get_session)
):
    """Update a mapping definition."""
    mapping = mapping_crud.update_mapping(session, mapping_id, data)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return mapping


@router.delete("/{mapping_id}")
def delete_mapping(
    mapping_id: str,
    session: Session = Depends(get_session)
):
    """Delete a mapping definition."""
    success = mapping_crud.delete_mapping(session, mapping_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return {"message": "Mapping deleted successfully"}


# ==========================================
# Preview & Publish Endpoints
# ==========================================

@router.post("/preview", response_model=MappingPreviewResponse)
def preview_mapping(
    request: MappingPreviewRequest,
    session: Session = Depends(get_session)
):
    """
    Live preview of mapping transformation.
    Fetches sample rows from source and simulates transforms.
    """
    logger.info(f"[Mapping] Preview request for table: {request.source_table_name}")
    
    try:
        # Connect to raw store database
        raw_engine = create_engine(settings.raw_store_database_url)
        
        # Fetch sample rows
        with raw_engine.connect() as conn:
            query = text(f"SELECT * FROM {request.source_table_name} LIMIT :limit")
            result = conn.execute(query, {"limit": request.limit})
            columns = list(result.keys())
            rows = [dict(row._mapping) for row in result.fetchall()]
        
        raw_engine.dispose()
        
        if not rows:
            return MappingPreviewResponse(
                columns=[],
                data=[],
                row_count=0,
                warnings=["Source table is empty"]
            )
        
        # Apply transforms based on mapping_spec
        transformed_data = []
        warnings = []
        
        for row in rows:
            transformed_row = _apply_transforms(row, request.mapping_spec, warnings)
            transformed_data.append(transformed_row)
        
        # Get output columns from target nodes
        output_columns = _get_output_columns(request.mapping_spec)
        
        return MappingPreviewResponse(
            columns=output_columns,
            data=transformed_data,
            row_count=len(transformed_data),
            warnings=warnings if warnings else None
        )
        
    except Exception as e:
        logger.error(f"[Mapping] Preview failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")


@router.post("/{mapping_id}/publish", response_model=ObjectMappingDefRead)
def publish_mapping(
    mapping_id: str,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """
    Publish a mapping and trigger indexing job.
    """
    mapping = mapping_crud.publish_mapping(session, mapping_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    # Trigger background indexing
    from app.engine.indexing_worker import run_indexing_job
    background_tasks.add_task(run_indexing_job, mapping_id)
    
    logger.info(f"[Mapping] Published and triggered indexing for: {mapping_id}")
    return mapping


# ==========================================
# Transform Helpers
# ==========================================

def _apply_transforms(
    row: Dict[str, Any],
    mapping_spec: Dict[str, Any],
    warnings: List[str]
) -> Dict[str, Any]:
    """
    Apply transformation logic from mapping_spec to a single row.
    """
    nodes = mapping_spec.get("nodes", [])
    edges = mapping_spec.get("edges", [])
    
    # Build node lookup and edge graph
    node_map = {n["id"]: n for n in nodes}
    edge_map = {}  # target_id -> source_id
    for edge in edges:
        edge_map[edge["target"]] = edge["source"]
    
    result = {}
    
    # Process each target node
    for node in nodes:
        if node.get("type") != "target":
            continue
        
        target_prop = node.get("data", {}).get("property", node.get("property", ""))
        if not target_prop:
            continue
        
        # Trace back through edges to find source
        value = _resolve_node_value(node["id"], node_map, edge_map, row, warnings)
        result[target_prop] = value
    
    return result


def _resolve_node_value(
    node_id: str,
    node_map: Dict[str, Any],
    edge_map: Dict[str, str],
    row: Dict[str, Any],
    warnings: List[str]
) -> Any:
    """
    Recursively resolve the value for a node by tracing edges.
    """
    node = node_map.get(node_id)
    if not node:
        return None
    
    node_type = node.get("type")
    node_data = node.get("data", {})
    
    if node_type == "source":
        # Source node: get value from row
        column = node_data.get("column", node.get("column", ""))
        return row.get(column)
    
    elif node_type == "transform":
        # Transform node: apply function to input
        func_name = node_data.get("function", node.get("function", ""))
        
        # Get input value from connected source
        source_node_id = edge_map.get(node_id)
        if not source_node_id:
            return None
        
        input_value = _resolve_node_value(source_node_id, node_map, edge_map, row, warnings)
        
        return _apply_transform_function(func_name, input_value, warnings)
    
    elif node_type == "target":
        # Target node: get value from connected node
        source_node_id = edge_map.get(node_id)
        if not source_node_id:
            return None
        
        return _resolve_node_value(source_node_id, node_map, edge_map, row, warnings)
    
    return None


def _apply_transform_function(
    func_name: str,
    input_value: Any,
    warnings: List[str]
) -> Any:
    """
    Apply a transformation function to an input value.
    """
    if func_name == "image_embedding_clip":
        # Mock: Generate random 768-dim vector
        return [round(random.uniform(-1, 1), 6) for _ in range(768)]
    
    elif func_name == "concat":
        # String concatenation (pass through for single value)
        return str(input_value) if input_value else ""
    
    elif func_name == "to_uppercase":
        return str(input_value).upper() if input_value else ""
    
    elif func_name == "to_lowercase":
        return str(input_value).lower() if input_value else ""
    
    elif func_name == "format_date":
        # Pass through for demo
        return input_value
    
    else:
        warnings.append(f"Unknown transform function: {func_name}")
        return input_value


def _get_output_columns(mapping_spec: Dict[str, Any]) -> List[str]:
    """
    Extract output column names from target nodes.
    """
    nodes = mapping_spec.get("nodes", [])
    columns = []
    
    for node in nodes:
        if node.get("type") == "target":
            prop = node.get("data", {}).get("property", node.get("property", ""))
            if prop:
                columns.append(prop)
    
    return columns


# ==========================================
# Lineage Query Endpoints
# ==========================================

@router.get("/lineage/instance/{instance_id}", response_model=LineageLookupResponse)
def get_lineage_by_instance(
    instance_id: str,
    session: Session = Depends(get_session)
):
    """
    Get lineage info for an object instance.
    
    Use this to trace a vector back to its source file.
    """
    from sqlmodel import select
    
    stmt = select(ObjectInstanceLineage).where(
        ObjectInstanceLineage.instance_id == instance_id
    )
    lineage = session.exec(stmt).first()
    
    if not lineage:
        raise HTTPException(status_code=404, detail="Lineage record not found")
    
    return LineageLookupResponse(
        instance_id=lineage.instance_id,
        object_def_id=lineage.object_def_id,
        source_table=lineage.source_table,
        source_row_id=lineage.source_row_id,
        source_file_path=lineage.source_file_path,
        vector_collection=lineage.vector_collection
    )


@router.get("/lineage/mapping/{mapping_id}", response_model=List[ObjectInstanceLineageRead])
def list_lineage_by_mapping(
    mapping_id: str,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    List all lineage records for a mapping.
    """
    from sqlmodel import select
    
    stmt = select(ObjectInstanceLineage).where(
        ObjectInstanceLineage.mapping_id == mapping_id
    ).offset(skip).limit(limit)
    
    records = session.exec(stmt).all()
    return records


@router.get("/lineage/file", response_model=List[ObjectInstanceLineageRead])
def search_lineage_by_file(
    file_path: str,
    session: Session = Depends(get_session)
):
    """
    Search lineage records by source file path.
    
    Useful for finding all vectors derived from a specific file.
    """
    from sqlmodel import select
    
    stmt = select(ObjectInstanceLineage).where(
        ObjectInstanceLineage.source_file_path.contains(file_path)
    ).limit(100)
    
    records = session.exec(stmt).all()
    return records
