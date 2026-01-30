"""
V3 Graph API - Graph Analysis Endpoints
MDP Platform V3.1 - Graph Analysis Module

Provides endpoints for:
- Node expansion (hard links + semantic links)
- Shortest path finding
- Graph statistics
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from loguru import logger

from app.services.graph_service import get_graph_service
from app.models.graph import (
    ExpandRequest, ExpandOptions,
    GraphDTO, GraphNode, GraphEdge,
    ShortestPathRequest, ShortestPathResponse
)

router = APIRouter(prefix="/graph", tags=["Graph Analysis"])


# ==========================================
# Request/Response DTOs
# ==========================================

class ExpandRequestBody(BaseModel):
    """Request body for expand endpoint."""
    seed_ids: List[str]
    options: Optional[ExpandOptions] = None


class GraphStatsResponse(BaseModel):
    """Response for graph statistics."""
    total_links: int
    unique_nodes: int
    link_types: List[dict]


# ==========================================
# Endpoints
# ==========================================

@router.post("/expand", response_model=GraphDTO)
async def expand_graph(request: ExpandRequestBody):
    """
    Expand graph from seed nodes.
    
    Supports two modes:
    - Hard Links: Database-stored relationships
    - Semantic Links: Vector similarity (when options.semantic=true)
    
    Request body:
    ```json
    {
      "seed_ids": ["tgt-001"],
      "options": {
        "semantic": false,
        "limit": 50,
        "depth": 1
      }
    }
    ```
    
    Returns React Flow compatible nodes and edges.
    """
    logger.info(f"Graph expand request: seeds={request.seed_ids}")
    
    if not request.seed_ids:
        raise HTTPException(status_code=400, detail="seed_ids cannot be empty")
    
    if len(request.seed_ids) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 seed nodes allowed")
    
    service = get_graph_service()
    result = service.expand_node(request.seed_ids, request.options)
    
    return result


@router.post("/shortest-path", response_model=ShortestPathResponse)
async def find_shortest_path(request: ShortestPathRequest):
    """
    Find shortest path between two nodes.
    
    Uses BFS to find the shortest path through the graph.
    
    Request body:
    ```json
    {
      "source": "tgt-001",
      "target": "mission-001",
      "max_depth": 10
    }
    ```
    """
    logger.info(f"Shortest path request: {request.source} -> {request.target}")
    
    if request.source == request.target:
        return ShortestPathResponse(found=True, path=[request.source], distance=0)
    
    service = get_graph_service()
    result = service.find_shortest_path(
        request.source,
        request.target,
        request.max_depth
    )
    
    return result


@router.get("/stats", response_model=GraphStatsResponse)
async def get_graph_stats():
    """
    Get graph statistics.
    
    Returns total links, unique nodes, and link type distribution.
    """
    service = get_graph_service()
    stats = service.get_graph_stats()
    
    return GraphStatsResponse(**stats)


@router.get("/node/{node_id}")
async def get_node_neighbors(
    node_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    include_semantic: bool = Query(default=False)
):
    """
    Get neighbors of a specific node.
    
    Convenience endpoint for single-node expansion.
    """
    service = get_graph_service()
    options = ExpandOptions(semantic=include_semantic, limit=limit)
    result = service.expand_node([node_id], options)
    
    return result


@router.get("/types")
async def get_node_types():
    """
    Get available node types and their visual configuration.
    """
    from app.services.graph_service import NODE_TYPE_CONFIG
    
    return {
        "types": [
            {
                "type": key,
                "icon": config["icon"],
                "color": config["color"],
                "label": config["label"]
            }
            for key, config in NODE_TYPE_CONFIG.items()
        ]
    }
