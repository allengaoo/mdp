"""
Object 360 View API - Low-Code Metadata-Driven Object Profile
MDP Platform V3.1

Endpoints:
- GET /object-views/config/{object_type} - Get view configuration
- GET /objects/{id}/360-data - Get aggregated 360 data
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select, text
from pydantic import BaseModel

from app.core.db import get_session
from app.core.config import settings
from app.models.workshop import (
    AppDefinition,
    AppModule,
    AppWidget,
)

router = APIRouter(prefix="/object-views", tags=["Object 360 View"])


# =============================================================================
# DTOs
# =============================================================================

class WidgetConfigDTO(BaseModel):
    """Widget configuration DTO."""
    id: str
    widget_type: str
    data_binding: Dict[str, Any]
    view_config: Optional[Dict[str, Any]] = None
    position_config: Optional[Dict[str, Any]] = None


class ModuleConfigDTO(BaseModel):
    """Module configuration with widgets."""
    id: str
    name: Optional[str]
    layout_config: Optional[Dict[str, Any]] = None
    display_order: int
    widgets: List[WidgetConfigDTO] = []


class ViewConfigDTO(BaseModel):
    """Complete view configuration."""
    id: str
    name: str
    app_type: str
    global_config: Optional[Dict[str, Any]] = None
    modules: List[ModuleConfigDTO] = []


class TimelineEventDTO(BaseModel):
    """Timeline event DTO."""
    id: str
    event_type: str
    title: str
    description: Optional[str] = None
    timestamp: datetime
    icon: Optional[str] = None
    color: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RelationDTO(BaseModel):
    """Relation DTO."""
    id: str
    link_type: str
    target_id: str
    target_type: str
    target_label: str
    direction: str  # "outgoing" or "incoming"
    properties: Optional[Dict[str, Any]] = None


class SimilarObjectDTO(BaseModel):
    """Similar object from vector search."""
    id: str
    object_type: str
    label: str
    similarity_score: float
    properties: Optional[Dict[str, Any]] = None


class Object360DataDTO(BaseModel):
    """Complete 360 data for an object."""
    object_id: str
    object_type: str
    properties: Dict[str, Any] = {}
    relations: Dict[str, List[RelationDTO]] = {}
    timeline_events: List[TimelineEventDTO] = []
    similar_objects: List[SimilarObjectDTO] = []
    media_urls: List[str] = []
    stats: Dict[str, Any] = {}


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/config/{object_type}", response_model=ViewConfigDTO)
async def get_view_config(
    object_type: str,
    session: Session = Depends(get_session)
):
    """
    Get the view configuration for a specific object type.
    
    This returns the complete layout configuration including:
    - App definition (global settings)
    - Modules (layout sections)
    - Widgets (components)
    
    The frontend uses this to dynamically render the Object 360 page.
    """
    # Query app_definition where global_config->>'$.object_type' == object_type
    # Using raw SQL for JSON extraction
    query = text("""
        SELECT id, project_id, name, app_type, global_config, created_by, created_at, updated_at
        FROM app_definition
        WHERE JSON_UNQUOTE(JSON_EXTRACT(global_config, '$.object_type')) = :object_type
        AND app_type = 'EXPLORER'
        LIMIT 1
    """)
    
    result = session.execute(query, {"object_type": object_type}).fetchone()
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No view configuration found for object type: {object_type}"
        )
    
    app_id = result[0]
    
    # Parse global_config
    import json
    global_config = result[4]
    if isinstance(global_config, str):
        global_config = json.loads(global_config)
    
    # Fetch modules
    modules_query = text("""
        SELECT id, app_id, name, layout_config, display_order
        FROM app_module
        WHERE app_id = :app_id
        ORDER BY display_order
    """)
    modules_result = session.execute(modules_query, {"app_id": app_id}).fetchall()
    
    modules = []
    for mod_row in modules_result:
        mod_id = mod_row[0]
        layout_config = mod_row[3]
        if isinstance(layout_config, str):
            layout_config = json.loads(layout_config)
        
        # Fetch widgets for this module
        widgets_query = text("""
            SELECT id, module_id, widget_type, data_binding, view_config, position_config
            FROM app_widget
            WHERE module_id = :module_id
            ORDER BY JSON_EXTRACT(position_config, '$.order')
        """)
        widgets_result = session.execute(widgets_query, {"module_id": mod_id}).fetchall()
        
        widgets = []
        for wgt_row in widgets_result:
            data_binding = wgt_row[3]
            view_config = wgt_row[4]
            position_config = wgt_row[5]
            
            if isinstance(data_binding, str):
                data_binding = json.loads(data_binding)
            if isinstance(view_config, str):
                view_config = json.loads(view_config)
            if isinstance(position_config, str):
                position_config = json.loads(position_config)
            
            widgets.append(WidgetConfigDTO(
                id=wgt_row[0],
                widget_type=wgt_row[2],
                data_binding=data_binding or {},
                view_config=view_config,
                position_config=position_config,
            ))
        
        modules.append(ModuleConfigDTO(
            id=mod_id,
            name=mod_row[2],
            layout_config=layout_config,
            display_order=mod_row[4],
            widgets=widgets,
        ))
    
    return ViewConfigDTO(
        id=app_id,
        name=result[2],
        app_type=result[3],
        global_config=global_config,
        modules=modules,
    )


@router.get("/types")
async def get_available_object_types(
    session: Session = Depends(get_session)
):
    """
    Get list of object types that have 360 view configurations.
    """
    query = text("""
        SELECT 
            JSON_UNQUOTE(JSON_EXTRACT(global_config, '$.object_type')) as object_type,
            name,
            id
        FROM app_definition
        WHERE app_type = 'EXPLORER'
        AND JSON_EXTRACT(global_config, '$.object_type') IS NOT NULL
    """)
    
    result = session.execute(query).fetchall()
    
    return [
        {
            "object_type": row[0],
            "view_name": row[1],
            "app_id": row[2],
        }
        for row in result
    ]


# =============================================================================
# 360 Data Aggregation Endpoint
# =============================================================================

# Create a separate router for object data endpoints
objects_router = APIRouter(prefix="/objects", tags=["Object 360 Data"])


@objects_router.get("/{object_id}/360-data", response_model=Object360DataDTO)
async def get_object_360_data(
    object_id: str,
    object_type: str = Query(..., description="The type of the object"),
    session: Session = Depends(get_session)
):
    """
    Get aggregated 360-degree data for a specific object.
    
    This performs a "Scatter-Gather" operation to collect data from:
    1. Identity - Object properties from MySQL/ES
    2. Relations - Linked objects from sys_link_instance
    3. Timeline - Action logs and events
    4. AI Insights - Similar objects from ChromaDB
    5. Media - Associated media files
    """
    # Run data fetching in parallel where possible
    properties_task = _fetch_object_properties(session, object_id, object_type)
    relations_task = _fetch_object_relations(session, object_id)
    timeline_task = _fetch_timeline_events(session, object_id)
    similar_task = _fetch_similar_objects(object_id, object_type)
    media_task = _fetch_media_urls(session, object_id)
    stats_task = _fetch_object_stats(session, object_id)
    
    # Gather results
    properties = await properties_task
    relations = await relations_task
    timeline_events = await timeline_task
    similar_objects = await similar_task
    media_urls = await media_task
    stats = await stats_task
    
    return Object360DataDTO(
        object_id=object_id,
        object_type=object_type,
        properties=properties,
        relations=relations,
        timeline_events=timeline_events,
        similar_objects=similar_objects,
        media_urls=media_urls,
        stats=stats,
    )


# =============================================================================
# Data Fetching Functions (Scatter-Gather)
# =============================================================================

async def _fetch_object_properties(
    session: Session,
    object_id: str,
    object_type: str
) -> Dict[str, Any]:
    """
    Fetch object scalar properties from MySQL.
    In production, this would also query ElasticSearch for richer data.
    """
    # First try to get from sys_object_instance
    query = text("""
        SELECT properties
        FROM sys_object_instance
        WHERE id = :object_id
        LIMIT 1
    """)
    
    try:
        result = session.execute(query, {"object_id": object_id}).fetchone()
        if result and result[0]:
            import json
            props = result[0]
            # Handle bytes
            if isinstance(props, bytes):
                props = props.decode('utf-8')
            
            # Handle string (parse JSON)
            if isinstance(props, str):
                try:
                    props = json.loads(props)
                except json.JSONDecodeError:
                    pass
            
            # Handle double-encoded JSON string if necessary
            if isinstance(props, str):
                try:
                    props = json.loads(props)
                except json.JSONDecodeError:
                    pass
            
            return props if isinstance(props, dict) else {}
    except Exception as e:
        print(f"Error fetching properties: {e}")
    
    # Fallback: return mock data for demo
    return {
        "id": object_id,
        "object_type": object_type,
        "name": f"Object {object_id}",
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
    }


async def _fetch_object_relations(
    session: Session,
    object_id: str
) -> Dict[str, List[RelationDTO]]:
    """
    Fetch relations from sys_link_instance table.
    Groups relations by link_type.
    """
    relations: Dict[str, List[RelationDTO]] = {}
    
    # Query outgoing relations
    outgoing_query = text("""
        SELECT 
            l.id,
            COALESCE(lt.name, l.source_object_type || '->' || l.target_object_type) as link_type,
            l.target_instance_id,
            l.target_object_type,
            l.properties
        FROM sys_link_instance l
        LEFT JOIN meta_link_type lt ON l.link_type_id = lt.id
        WHERE l.source_instance_id = :object_id
    """)
    
    try:
        outgoing_result = session.execute(outgoing_query, {"object_id": object_id}).fetchall()
        
        import json
        for row in outgoing_result:
            link_type = row[1] or "unknown"
            props = row[4]
            if isinstance(props, str):
                props = json.loads(props)
            
            rel = RelationDTO(
                id=row[0],
                link_type=link_type,
                target_id=row[2],
                target_type=row[3] or "unknown",
                target_label=f"{row[3] or 'Object'}: {row[2][:8]}",
                direction="outgoing",
                properties=props,
            )
            
            if link_type not in relations:
                relations[link_type] = []
            relations[link_type].append(rel)
    except Exception as e:
        print(f"Error fetching outgoing relations: {e}")
    
    # Query incoming relations
    incoming_query = text("""
        SELECT 
            l.id,
            COALESCE(lt.name, l.source_object_type || '->' || l.target_object_type) as link_type,
            l.source_instance_id,
            l.source_object_type,
            l.properties
        FROM sys_link_instance l
        LEFT JOIN meta_link_type lt ON l.link_type_id = lt.id
        WHERE l.target_instance_id = :object_id
    """)
    
    try:
        incoming_result = session.execute(incoming_query, {"object_id": object_id}).fetchall()
        
        import json
        for row in incoming_result:
            link_type = row[1] or "unknown"
            props = row[4]
            if isinstance(props, str):
                props = json.loads(props)
            
            rel = RelationDTO(
                id=row[0],
                link_type=link_type,
                target_id=row[2],
                target_type=row[3] or "unknown",
                target_label=f"{row[3] or 'Object'}: {row[2][:8]}",
                direction="incoming",
                properties=props,
            )
            
            if link_type not in relations:
                relations[link_type] = []
            relations[link_type].append(rel)
    except Exception as e:
        print(f"Error fetching incoming relations: {e}")
    
    return relations


async def _fetch_timeline_events(
    session: Session,
    object_id: str
) -> List[TimelineEventDTO]:
    """
    Fetch timeline events from sys_action_log and linked events.
    """
    events: List[TimelineEventDTO] = []
    
    # Fetch from sys_action_log
    action_log_query = text("""
        SELECT 
            al.id,
            al.action_def_id,
            ad.name as action_name,
            al.execution_status,
            al.created_at,
            al.input_params,
            al.error_message
        FROM sys_action_log al
        LEFT JOIN meta_action_def ad ON al.action_def_id = ad.id
        WHERE JSON_EXTRACT(al.input_params, '$.object_id') = :object_id
           OR JSON_EXTRACT(al.input_params, '$.target_id') = :object_id
        ORDER BY al.created_at DESC
        LIMIT 50
    """)
    
    try:
        result = session.execute(action_log_query, {"object_id": object_id}).fetchall()
        
        import json
        for row in result:
            status = row[3] or "unknown"
            color = "#52c41a" if status == "SUCCESS" else "#ff4d4f" if status == "FAILED" else "#1890ff"
            icon = "check-circle" if status == "SUCCESS" else "close-circle" if status == "FAILED" else "clock-circle"
            
            input_params = row[5]
            if isinstance(input_params, str):
                input_params = json.loads(input_params)
            
            events.append(TimelineEventDTO(
                id=row[0],
                event_type="action_execution",
                title=row[2] or f"Action {row[1]}",
                description=row[6] if status == "FAILED" else f"Status: {status}",
                timestamp=row[4],
                icon=icon,
                color=color,
                metadata={"input_params": input_params, "status": status},
            ))
    except Exception as e:
        print(f"Error fetching action logs: {e}")
    
    # Sort by timestamp
    events.sort(key=lambda e: e.timestamp, reverse=True)
    
    return events


async def _fetch_similar_objects(
    object_id: str,
    object_type: str
) -> List[SimilarObjectDTO]:
    """
    Fetch similar objects from ChromaDB vector search.
    This is a placeholder - in production, would query ChromaDB.
    """
    # TODO: Implement actual ChromaDB vector search
    # For now, return mock data
    return [
        SimilarObjectDTO(
            id=f"sim-{i}",
            object_type=object_type,
            label=f"Similar {object_type} #{i}",
            similarity_score=0.95 - (i * 0.05),
            properties={"note": "Mock similar object"},
        )
        for i in range(1, 4)
    ]


async def _fetch_media_urls(
    session: Session,
    object_id: str
) -> List[str]:
    """
    Fetch media URLs linked to the object.
    """
    query = text("""
        SELECT l.target_instance_id
        FROM sys_link_instance l
        WHERE l.source_instance_id = :object_id
        AND l.target_object_type IN ('recon_image', 'media', 'document')
    """)
    
    try:
        result = session.execute(query, {"object_id": object_id}).fetchall()
        # In production, would resolve actual URLs from media service
        return [f"/api/v3/media/{row[0]}" for row in result]
    except Exception as e:
        print(f"Error fetching media: {e}")
        return []


async def _fetch_object_stats(
    session: Session,
    object_id: str
) -> Dict[str, Any]:
    """
    Calculate object statistics.
    """
    stats = {}
    
    # Count relations
    try:
        rel_count_query = text("""
            SELECT COUNT(*) FROM sys_link_instance
            WHERE source_instance_id = :object_id OR target_instance_id = :object_id
        """)
        result = session.execute(rel_count_query, {"object_id": object_id}).fetchone()
        stats["total_relations"] = result[0] if result else 0
    except Exception as e:
        stats["total_relations"] = 0
    
    # Count action logs
    try:
        log_count_query = text("""
            SELECT COUNT(*) FROM sys_action_log
            WHERE JSON_EXTRACT(input_params, '$.object_id') = :object_id
        """)
        result = session.execute(log_count_query, {"object_id": object_id}).fetchone()
        stats["total_actions"] = result[0] if result else 0
    except Exception as e:
        stats["total_actions"] = 0
    
    return stats


# Export both routers
__all__ = ["router", "objects_router"]
