"""
Hybrid Search Service
MDP Platform V3.1 - Global Search Module

Implements hybrid search combining:
1. Vector semantic search (ChromaDB)
2. Full-text keyword search (Elasticsearch)
3. Dynamic faceted filtering

Architecture:
- Stage 1 (Optional): Vector query -> ChromaDB -> Top-K candidate IDs
- Stage 2: Text/Filter query -> ES with vector boost -> Final results + Facets
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from loguru import logger

from app.core.elastic_store import (
    search_objects,
    get_object_facets,
    ensure_objects_index,
)

# Lazy import for vector_store to avoid startup errors if chromadb is not installed
_search_vectors = None

def _get_search_vectors():
    """Lazy load search_vectors function."""
    global _search_vectors
    if _search_vectors is None:
        try:
            from app.core.vector_store import search_vectors
            _search_vectors = search_vectors
        except ImportError as e:
            logger.warning(f"[SearchService] Vector search unavailable: {e}")
            _search_vectors = lambda *args, **kwargs: []
    return _search_vectors


@dataclass
class SearchFilters:
    """Search filter configuration."""
    object_types: List[str] = field(default_factory=list)
    properties: Dict[str, List[str]] = field(default_factory=dict)
    project_id: Optional[str] = None


@dataclass
class SearchRequest:
    """Search request parameters."""
    query_text: Optional[str] = None
    query_vector: Optional[List[float]] = None
    filters: Optional[SearchFilters] = None
    page: int = 1
    page_size: int = 20
    sort_field: Optional[str] = None
    sort_order: str = "desc"


@dataclass
class SearchHit:
    """Single search result."""
    id: str
    object_type: str
    object_type_display: str
    display_name: str
    score: float
    properties: Dict[str, Any]
    highlights: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class FacetBucket:
    """Single facet bucket."""
    key: str
    count: int


@dataclass
class Facet:
    """Facet with buckets."""
    field: str
    display_name: str
    buckets: List[FacetBucket]


@dataclass
class SearchResponse:
    """Complete search response."""
    hits: List[SearchHit]
    total: int
    page: int
    page_size: int
    facets: List[Facet]
    query_text: Optional[str] = None


def execute_search(request: SearchRequest) -> SearchResponse:
    """
    Execute hybrid search with vector boost.
    
    Strategy:
    1. If query_vector provided: Query ChromaDB for semantic matches
    2. Query ES with text search + filters + vector boost
    3. Process facets from ES aggregations
    
    Args:
        request: SearchRequest with query and filters
        
    Returns:
        SearchResponse with hits, total, and facets
    """
    logger.info(f"[SearchService] Executing search: text='{request.query_text}', has_vector={request.query_vector is not None}")
    
    # Ensure index exists
    ensure_objects_index()
    
    # Stage 1: Vector Search (if vector provided)
    vector_ids = []
    if request.query_vector:
        vector_ids = _execute_vector_search(request.query_vector)
        logger.info(f"[SearchService] Vector search returned {len(vector_ids)} candidates")
    
    # Stage 2: ES Search with filters and vector boost
    es_filters = _build_es_filters(request.filters)
    
    es_result = search_objects(
        query_text=request.query_text,
        filters=es_filters,
        vector_ids=vector_ids if vector_ids else None,
        size=request.page_size,
        page=request.page,
        sort_field=request.sort_field,
        sort_order=request.sort_order
    )
    
    # Process hits
    hits = []
    for hit in es_result.get("hits", []):
        search_hit = SearchHit(
            id=hit["id"],
            object_type=hit.get("object_type", ""),
            object_type_display=hit.get("object_type_display", hit.get("object_type", "")),
            display_name=hit.get("display_name", ""),
            score=hit.get("score", 0),
            properties=hit.get("properties", {}),
            highlights=hit.get("highlights", {})
        )
        hits.append(search_hit)
    
    # Process facets
    facets = _process_facets(es_result.get("aggregations", {}))
    
    return SearchResponse(
        hits=hits,
        total=es_result.get("total", 0),
        page=request.page,
        page_size=request.page_size,
        facets=facets,
        query_text=request.query_text
    )


def _execute_vector_search(
    query_vector: List[float],
    top_k: int = 100
) -> List[str]:
    """
    Execute vector search across all object collections.
    
    Returns list of matching object IDs.
    """
    # For now, search in a generic collection
    # In production, would search across multiple type-specific collections
    try:
        # Get search function lazily
        search_vectors_fn = _get_search_vectors()
        
        # Search in default objects collection
        results = search_vectors_fn(
            collection_name="obj_default",
            query_vector=query_vector,
            top_k=top_k
        )
        
        return [r["id"] for r in results]
        
    except Exception as e:
        logger.warning(f"[SearchService] Vector search failed: {e}")
        return []


def _build_es_filters(filters: Optional[SearchFilters]) -> Dict[str, Any]:
    """
    Convert SearchFilters to ES filter dict.
    """
    if not filters:
        return {}
    
    es_filters = {}
    
    # Object type filter
    if filters.object_types:
        es_filters["object_type"] = filters.object_types
    
    # Project filter
    if filters.project_id:
        es_filters["project_id"] = filters.project_id
    
    # Property filters (keyword fields with _kwd suffix)
    for prop_name, values in filters.properties.items():
        if values:
            # Ensure proper field path
            if not prop_name.startswith("properties."):
                field_name = f"properties.{prop_name}_kwd"
            else:
                field_name = prop_name
            es_filters[field_name] = values
    
    return es_filters


def _process_facets(aggregations: Dict[str, Any]) -> List[Facet]:
    """
    Process ES aggregations into Facet objects.
    """
    facets = []
    
    # Object types facet (always present)
    if "object_types" in aggregations:
        buckets = [
            FacetBucket(key=b["key"], count=b["count"])
            for b in aggregations["object_types"]
        ]
        facets.append(Facet(
            field="object_type",
            display_name="对象类型",
            buckets=buckets
        ))
    
    # Dynamic property facets
    for field_name, field_data in aggregations.items():
        if field_name == "object_types":
            continue
        
        if isinstance(field_data, list):
            buckets = [
                FacetBucket(key=b["key"], count=b["count"])
                for b in field_data
            ]
            
            # Extract property name from field path
            display_name = field_name
            if field_name.startswith("properties.") and field_name.endswith("_kwd"):
                display_name = field_name[11:-4]  # Remove 'properties.' and '_kwd'
            
            facets.append(Facet(
                field=field_name,
                display_name=display_name,
                buckets=buckets
            ))
    
    return facets


def get_available_facets(
    object_types: Optional[List[str]] = None
) -> List[Facet]:
    """
    Get available facets based on registered filterable properties.
    
    Args:
        object_types: Optional list of object types to filter by
        
    Returns:
        List of Facet with current bucket counts
    """
    # Get standard facets
    field_names = ["object_type"]
    
    # TODO: Get dynamic facet fields from database based on is_filterable flag
    # For now, use some common fields
    common_facets = [
        "properties.status_kwd",
        "properties.type_kwd",
        "properties.classification_kwd",
    ]
    field_names.extend(common_facets)
    
    # Query ES for facet values
    facet_data = get_object_facets(field_names)
    
    facets = []
    for field, buckets in facet_data.items():
        display_name = field
        if field.startswith("properties.") and field.endswith("_kwd"):
            display_name = field[11:-4]
        elif field == "object_type":
            display_name = "对象类型"
        
        facets.append(Facet(
            field=field,
            display_name=display_name,
            buckets=[FacetBucket(key=b["key"], count=b["count"]) for b in buckets]
        ))
    
    return facets


def search_by_text(
    query: str,
    object_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> SearchResponse:
    """
    Simple text-only search (convenience method).
    """
    filters = None
    if object_type:
        filters = SearchFilters(object_types=[object_type])
    
    request = SearchRequest(
        query_text=query,
        filters=filters,
        page=page,
        page_size=page_size
    )
    
    return execute_search(request)


def search_by_vector(
    vector: List[float],
    object_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> SearchResponse:
    """
    Vector-only search (convenience method).
    """
    filters = None
    if object_type:
        filters = SearchFilters(object_types=[object_type])
    
    request = SearchRequest(
        query_vector=vector,
        filters=filters,
        page=page,
        page_size=page_size
    )
    
    return execute_search(request)
