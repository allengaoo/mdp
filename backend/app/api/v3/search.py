"""
V3 Search API - Full Text Search & Object Explorer Endpoints

Provides:
1. Basic text search capabilities
2. Hybrid object search (text + vector + facets)
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from loguru import logger

from app.core.elastic_store import (
    search_text,
    index_document,
    delete_document,
    bulk_index_documents,
    ensure_text_index,
    ensure_objects_index,
    get_es_client,
)
from app.services.search_service import (
    execute_search,
    get_available_facets,
    SearchRequest,
    SearchFilters,
)

router = APIRouter(prefix="/search", tags=["Search"])


# ==========================================
# DTOs
# ==========================================

class SearchResult(BaseModel):
    """Single search result."""
    id: str
    score: float
    content: str
    object_type_id: str
    object_instance_id: str
    property_name: str
    source_file: Optional[str] = None
    highlights: Optional[List[str]] = None
    created_at: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response with results and metadata."""
    query: str
    total: int
    results: List[SearchResult]


class IndexDocumentRequest(BaseModel):
    """Request to index a document."""
    id: str
    content: str
    object_type_id: str
    object_instance_id: str
    property_name: str = "content"
    source_file: Optional[str] = None
    metadata: Optional[dict] = None


class BulkIndexRequest(BaseModel):
    """Request to bulk index documents."""
    documents: List[IndexDocumentRequest]


class HealthResponse(BaseModel):
    """Elasticsearch health status."""
    status: str
    cluster_name: Optional[str] = None
    version: Optional[str] = None
    message: Optional[str] = None


# ==========================================
# Endpoints
# ==========================================

@router.get("/health", response_model=HealthResponse)
async def check_health():
    """
    Check Elasticsearch connection health.
    """
    client = get_es_client()
    if client is None:
        return HealthResponse(
            status="unavailable",
            message="Elasticsearch client not available"
        )
    
    try:
        info = client.info()
        return HealthResponse(
            status="healthy",
            cluster_name=info["cluster_name"],
            version=info["version"]["number"]
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            message=str(e)
        )


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    object_type_id: Optional[str] = Query(None, description="Filter by object type"),
    size: int = Query(20, ge=1, le=100, description="Maximum results to return")
):
    """
    Search for documents matching the query.
    
    Supports full-text search with highlighting and optional filtering by object type.
    """
    logger.info(f"Search request: q='{q}', object_type_id={object_type_id}, size={size}")
    
    results = search_text(
        query=q,
        object_type_id=object_type_id,
        size=size
    )
    
    # Convert to response model
    search_results = []
    for r in results:
        search_results.append(SearchResult(
            id=r["id"],
            score=r["score"],
            content=r["content"],
            object_type_id=r["object_type_id"],
            object_instance_id=r["object_instance_id"],
            property_name=r["property_name"],
            source_file=r.get("source_file"),
            highlights=r.get("highlights"),
            created_at=r.get("created_at")
        ))
    
    return SearchResponse(
        query=q,
        total=len(search_results),
        results=search_results
    )


@router.post("/index")
async def index_single_document(request: IndexDocumentRequest):
    """
    Index a single document for search.
    """
    success = index_document(
        doc_id=request.id,
        content=request.content,
        object_type_id=request.object_type_id,
        object_instance_id=request.object_instance_id,
        property_name=request.property_name,
        source_file=request.source_file,
        metadata=request.metadata
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to index document")
    
    return {"success": True, "id": request.id}


@router.post("/bulk-index")
async def bulk_index(request: BulkIndexRequest):
    """
    Bulk index multiple documents.
    """
    if not request.documents:
        raise HTTPException(status_code=400, detail="No documents provided")
    
    docs = [doc.model_dump() for doc in request.documents]
    count = bulk_index_documents(docs)
    
    return {
        "success": True,
        "indexed": count,
        "total": len(docs)
    }


@router.delete("/{doc_id}")
async def delete_indexed_document(doc_id: str):
    """
    Delete a document from the search index.
    """
    success = delete_document(doc_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete document")
    
    return {"success": True, "id": doc_id}


@router.post("/ensure-index")
async def ensure_index():
    """
    Ensure the search index exists with proper mappings.
    """
    success = ensure_text_index()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create index")
    
    return {"success": True, "message": "Index ready"}


# ==========================================
# Object Explorer DTOs
# ==========================================

class ObjectSearchFilters(BaseModel):
    """Filters for object search."""
    object_types: Optional[List[str]] = None
    properties: Optional[Dict[str, List[str]]] = None
    project_id: Optional[str] = None


class ObjectSearchRequest(BaseModel):
    """Request for object search."""
    q: Optional[str] = None
    vector_embedding: Optional[List[float]] = None
    filters: Optional[ObjectSearchFilters] = None
    page: int = 1
    page_size: int = 20
    sort_field: Optional[str] = None
    sort_order: str = "desc"


class ObjectHit(BaseModel):
    """Single object search hit."""
    id: str
    object_type: str
    object_type_display: str
    display_name: str
    score: float
    properties: Dict[str, Any]
    highlights: Optional[Dict[str, List[str]]] = None


class FacetBucket(BaseModel):
    """Single facet bucket."""
    key: str
    count: int


class FacetResponse(BaseModel):
    """Single facet with buckets."""
    field: str
    display_name: str
    buckets: List[FacetBucket]


class ObjectSearchResponse(BaseModel):
    """Response for object search."""
    hits: List[ObjectHit]
    total: int
    page: int
    page_size: int
    facets: List[FacetResponse]
    query: Optional[str] = None


# ==========================================
# Object Explorer Endpoints
# ==========================================

@router.post("/objects", response_model=ObjectSearchResponse)
async def search_objects_api(request: ObjectSearchRequest):
    """
    Search objects using hybrid search (text + vector).
    
    Supports:
    - Full-text search on display_name and searchable properties
    - Vector embedding for semantic search
    - Dynamic faceted filtering
    - Pagination and sorting
    
    Request body:
    ```json
    {
      "q": "radar",
      "vector_embedding": [...],  // Optional, 768-dim vector
      "filters": {
        "object_types": ["target", "vessel"],
        "properties": {
          "status": ["ACTIVE", "PENDING"]
        }
      },
      "page": 1,
      "page_size": 20
    }
    ```
    """
    logger.info(f"Object search: q='{request.q}', has_vector={request.vector_embedding is not None}")
    
    # Build search request
    filters = None
    if request.filters:
        filters = SearchFilters(
            object_types=request.filters.object_types or [],
            properties=request.filters.properties or {},
            project_id=request.filters.project_id
        )
    
    search_req = SearchRequest(
        query_text=request.q,
        query_vector=request.vector_embedding,
        filters=filters,
        page=request.page,
        page_size=request.page_size,
        sort_field=request.sort_field,
        sort_order=request.sort_order
    )
    
    # Execute search
    result = execute_search(search_req)
    
    # Convert to API response
    hits = [
        ObjectHit(
            id=h.id,
            object_type=h.object_type,
            object_type_display=h.object_type_display,
            display_name=h.display_name,
            score=h.score,
            properties=h.properties,
            highlights=h.highlights if h.highlights else None
        )
        for h in result.hits
    ]
    
    facets = [
        FacetResponse(
            field=f.field,
            display_name=f.display_name,
            buckets=[FacetBucket(key=b.key, count=b.count) for b in f.buckets]
        )
        for f in result.facets
    ]
    
    return ObjectSearchResponse(
        hits=hits,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        facets=facets,
        query=request.q
    )


@router.get("/objects/facets")
async def get_facets(
    object_types: Optional[str] = Query(None, description="Comma-separated object types to filter")
):
    """
    Get available facets for object search.
    
    Returns all filterable properties with their current value counts.
    """
    types = None
    if object_types:
        types = [t.strip() for t in object_types.split(",")]
    
    facets = get_available_facets(types)
    
    return {
        "facets": [
            {
                "field": f.field,
                "display_name": f.display_name,
                "buckets": [{"key": b.key, "count": b.count} for b in f.buckets]
            }
            for f in facets
        ]
    }


@router.post("/objects/ensure-index")
async def ensure_objects_index_api():
    """
    Ensure the objects search index exists with proper mappings.
    """
    success = ensure_objects_index()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create objects index")
    
    return {"success": True, "message": "Objects index ready"}
