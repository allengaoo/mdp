"""
Elasticsearch Client Module for MDP Platform.

Provides full-text search capabilities for unstructured content.
Supports hybrid search with dynamic field mapping for Object Explorer.
"""

from typing import Optional, List, Dict, Any
from loguru import logger

from app.core.config import settings


def get_objects_index_name() -> str:
    """Get the objects index name from config."""
    return settings.elasticsearch_objects_index


# Lazy import to avoid startup errors if ES is not installed
_es_client = None


def get_es_client():
    """
    Get or create Elasticsearch client singleton.
    
    Returns:
        Elasticsearch client instance
    """
    global _es_client
    
    if _es_client is not None:
        return _es_client
    
    try:
        from elasticsearch import Elasticsearch
        
        _es_client = Elasticsearch(
            hosts=[settings.elasticsearch_host],
            verify_certs=settings.elasticsearch_verify_certs,
            request_timeout=settings.elasticsearch_request_timeout,
        )
        
        # Verify connection
        info = _es_client.info()
        logger.info(f"Connected to Elasticsearch: {info['cluster_name']} v{info['version']['number']}")
        
        return _es_client
        
    except ImportError:
        logger.warning("elasticsearch package not installed. Text search will be unavailable.")
        return None
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        return None


def ensure_text_index(index_name: Optional[str] = None) -> bool:
    """
    Ensure the text search index exists with proper mappings.
    """
    client = get_es_client()
    if client is None:
        return False
    
    if index_name is None:
        index_name = settings.elasticsearch_index_name
    
    try:
        if client.indices.exists(index=index_name):
            logger.debug(f"Index '{index_name}' already exists")
            return True
        
        mappings = {
            "settings": {
                "number_of_shards": settings.elasticsearch_number_of_shards,
                "number_of_replicas": settings.elasticsearch_number_of_replicas,
                "analysis": {
                    "analyzer": {
                        "text_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "object_type_id": {"type": "keyword"},
                    "object_instance_id": {"type": "keyword"},
                    "property_name": {"type": "keyword"},
                    "content": {
                        "type": "text",
                        "analyzer": "text_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword", "ignore_above": 256}
                        }
                    },
                    "source_file": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "metadata": {"type": "object", "enabled": False}
                }
            }
        }
        
        client.indices.create(index=index_name, body=mappings)
        logger.info(f"Created index '{index_name}'")
        return True
        
    except Exception as e:
        logger.error(f"Failed to ensure index '{index_name}': {e}")
        return False


def index_document(
    doc_id: str,
    content: str,
    object_type_id: str,
    object_instance_id: str,
    property_name: str = "content",
    source_file: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    index_name: Optional[str] = None
) -> bool:
    """Index a document for full-text search."""
    client = get_es_client()
    if client is None:
        return False
    
    if index_name is None:
        index_name = settings.elasticsearch_index_name
    
    try:
        from datetime import datetime
        
        doc = {
            "object_type_id": object_type_id,
            "object_instance_id": object_instance_id,
            "property_name": property_name,
            "content": content,
            "source_file": source_file,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        client.index(index=index_name, id=doc_id, document=doc)
        logger.debug(f"Indexed document '{doc_id}' in '{index_name}'")
        return True
        
    except Exception as e:
        logger.error(f"Failed to index document '{doc_id}': {e}")
        return False


def search_text(
    query: str,
    object_type_id: Optional[str] = None,
    size: int = 20,
    index_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search for documents matching the query."""
    client = get_es_client()
    if client is None:
        return []
    
    if index_name is None:
        index_name = settings.elasticsearch_index_name
    
    try:
        must_clauses = [
            {
                "match": {
                    "content": {
                        "query": query,
                        "fuzziness": "AUTO"
                    }
                }
            }
        ]
        
        filter_clauses = []
        if object_type_id:
            filter_clauses.append({
                "term": {"object_type_id": object_type_id}
            })
        
        search_body = {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses
                }
            },
            "size": size,
            "highlight": {
                "fields": {
                    "content": {
                        "pre_tags": ["<mark>"],
                        "post_tags": ["</mark>"],
                        "fragment_size": 150,
                        "number_of_fragments": 3
                    }
                }
            }
        }
        
        response = client.search(index=index_name, body=search_body)
        
        results = []
        for hit in response["hits"]["hits"]:
            result = {
                "id": hit["_id"],
                "score": hit["_score"],
                **hit["_source"]
            }
            if "highlight" in hit:
                result["highlights"] = hit["highlight"].get("content", [])
            results.append(result)
        
        logger.debug(f"Search for '{query}' returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Search failed for query '{query}': {e}")
        return []


def delete_document(doc_id: str, index_name: Optional[str] = None) -> bool:
    """Delete a document from the index."""
    client = get_es_client()
    if client is None:
        return False
    
    if index_name is None:
        index_name = settings.elasticsearch_index_name
    
    try:
        client.delete(index=index_name, id=doc_id)
        logger.debug(f"Deleted document '{doc_id}' from '{index_name}'")
        return True
    except Exception as e:
        logger.error(f"Failed to delete document '{doc_id}': {e}")
        return False


def bulk_index_documents(
    documents: List[Dict[str, Any]],
    index_name: Optional[str] = None
) -> int:
    """Bulk index multiple documents."""
    client = get_es_client()
    if client is None:
        return 0
    
    if not documents:
        return 0
    
    if index_name is None:
        index_name = settings.elasticsearch_index_name
    
    try:
        from datetime import datetime
        from elasticsearch.helpers import bulk
        
        now = datetime.utcnow().isoformat()
        
        actions = []
        for doc in documents:
            action = {
                "_index": index_name,
                "_id": doc["id"],
                "_source": {
                    "object_type_id": doc["object_type_id"],
                    "object_instance_id": doc["object_instance_id"],
                    "property_name": doc.get("property_name", "content"),
                    "content": doc["content"],
                    "source_file": doc.get("source_file"),
                    "created_at": now,
                    "updated_at": now,
                    "metadata": doc.get("metadata", {})
                }
            }
            actions.append(action)
        
        success, failed = bulk(client, actions, stats_only=True)
        logger.info(f"Bulk indexed {success} documents, {failed} failed")
        return success
        
    except Exception as e:
        logger.error(f"Bulk indexing failed: {e}")
        return 0


# ==========================================
# Object Explorer Index Functions
# ==========================================

def ensure_objects_index() -> bool:
    """Ensure the objects index exists with dynamic template mappings."""
    client = get_es_client()
    if client is None:
        return False
    
    try:
        index_name = get_objects_index_name()
        if client.indices.exists(index=index_name):
            logger.debug(f"Index '{index_name}' already exists")
            return True
        
        index_config = {
            "settings": {
                "number_of_shards": settings.elasticsearch_number_of_shards,
                "number_of_replicas": settings.elasticsearch_number_of_replicas,
                "analysis": {
                    "analyzer": {
                        "text_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "asciifolding"]
                        }
                    }
                }
            },
            "mappings": {
                "dynamic_templates": [
                    {
                        "text_fields": {
                            "match_pattern": "regex",
                            "match": ".*_txt$",
                            "mapping": {"type": "text", "analyzer": "text_analyzer"}
                        }
                    },
                    {
                        "keyword_fields": {
                            "match_pattern": "regex",
                            "match": ".*_kwd$",
                            "mapping": {"type": "keyword"}
                        }
                    },
                    {
                        "sortable_fields": {
                            "match_pattern": "regex",
                            "match": ".*_val$",
                            "mapping": {"type": "keyword"}
                        }
                    }
                ],
                "properties": {
                    "id": {"type": "keyword"},
                    "object_type": {"type": "keyword"},
                    "object_type_display": {"type": "keyword"},
                    "display_name": {
                        "type": "text",
                        "analyzer": "text_analyzer",
                        "fields": {"keyword": {"type": "keyword"}, "sort": {"type": "keyword"}}
                    },
                    "properties": {"type": "object", "dynamic": True},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "project_id": {"type": "keyword"}
                }
            }
        }
        
        client.indices.create(index=index_name, body=index_config)
        logger.info(f"Created objects index '{index_name}' with dynamic templates")
        return True
        
    except Exception as e:
        logger.error(f"Failed to ensure objects index: {e}")
        return False


def index_object(
    instance_id: str,
    object_type: str,
    display_name: str,
    properties: Dict[str, Any],
    object_type_display: Optional[str] = None,
    project_id: Optional[str] = None
) -> bool:
    """Index an object instance for search."""
    client = get_es_client()
    if client is None:
        return False
    
    try:
        from datetime import datetime
        
        doc = {
            "id": instance_id,
            "object_type": object_type,
            "object_type_display": object_type_display or object_type,
            "display_name": display_name,
            "properties": properties,
            "project_id": project_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        client.index(index=get_objects_index_name(), id=instance_id, document=doc)
        logger.debug(f"Indexed object '{instance_id}' of type '{object_type}'")
        return True
        
    except Exception as e:
        logger.error(f"Failed to index object '{instance_id}': {e}")
        return False


def bulk_index_objects(objects: List[Dict[str, Any]]) -> int:
    """Bulk index multiple objects."""
    client = get_es_client()
    if client is None:
        return 0
    
    if not objects:
        return 0
    
    try:
        from datetime import datetime
        from elasticsearch.helpers import bulk
        
        now = datetime.utcnow().isoformat()
        index_name = get_objects_index_name()
        
        actions = []
        for obj in objects:
            action = {
                "_index": index_name,
                "_id": obj["id"],
                "_source": {
                    "id": obj["id"],
                    "object_type": obj["object_type"],
                    "object_type_display": obj.get("object_type_display", obj["object_type"]),
                    "display_name": obj.get("display_name", ""),
                    "properties": obj.get("properties", {}),
                    "project_id": obj.get("project_id"),
                    "created_at": obj.get("created_at", now),
                    "updated_at": now,
                }
            }
            actions.append(action)
        
        success, failed = bulk(client, actions, stats_only=True)
        logger.info(f"Bulk indexed {success} objects, {failed} failed")
        return success
        
    except Exception as e:
        logger.error(f"Bulk object indexing failed: {e}")
        return 0


def search_objects(
    query_text: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    vector_ids: Optional[List[str]] = None,
    size: int = 20,
    page: int = 1,
    sort_field: Optional[str] = None,
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """Execute hybrid search on objects index."""
    client = get_es_client()
    if client is None:
        return {"hits": [], "total": 0, "aggregations": {}}
    
    try:
        from_offset = (page - 1) * size
        
        must_clauses = []
        filter_clauses = []
        should_clauses = []
        
        if query_text:
            must_clauses.append({
                "multi_match": {
                    "query": query_text,
                    "fields": ["display_name^3", "properties.*_txt"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })
        
        if filters:
            for field, value in filters.items():
                if isinstance(value, list):
                    filter_clauses.append({"terms": {field: value}})
                else:
                    filter_clauses.append({"term": {field: value}})
        
        if vector_ids:
            should_clauses.append({"terms": {"_id": vector_ids, "boost": 2.0}})
        
        bool_query = {}
        if must_clauses:
            bool_query["must"] = must_clauses
        if filter_clauses:
            bool_query["filter"] = filter_clauses
        if should_clauses:
            bool_query["should"] = should_clauses
            bool_query["minimum_should_match"] = 0
        
        query = {"match_all": {}} if not bool_query else {"bool": bool_query}
        
        search_body = {
            "query": query,
            "from": from_offset,
            "size": size,
            "highlight": {
                "fields": {"display_name": {}, "properties.*_txt": {}},
                "pre_tags": ["<em>"],
                "post_tags": ["</em>"]
            },
            "aggs": {"object_types": {"terms": {"field": "object_type", "size": 20}}}
        }
        
        if sort_field:
            search_body["sort"] = [{sort_field: {"order": sort_order}}]
        else:
            search_body["sort"] = [{"_score": {"order": "desc"}}]
        
        response = client.search(index=get_objects_index_name(), body=search_body)
        
        hits = []
        for hit in response["hits"]["hits"]:
            result = {"id": hit["_id"], "score": hit["_score"], **hit["_source"]}
            if "highlight" in hit:
                result["highlights"] = hit["highlight"]
            hits.append(result)
        
        aggs = {}
        if "aggregations" in response:
            for agg_name, agg_data in response["aggregations"].items():
                if "buckets" in agg_data:
                    aggs[agg_name] = [{"key": b["key"], "count": b["doc_count"]} for b in agg_data["buckets"]]
        
        return {"hits": hits, "total": response["hits"]["total"]["value"], "aggregations": aggs}
        
    except Exception as e:
        logger.error(f"Object search failed: {e}")
        return {"hits": [], "total": 0, "aggregations": {}}


def delete_object(instance_id: str) -> bool:
    """Delete an object from the index."""
    client = get_es_client()
    if client is None:
        return False
    
    try:
        client.delete(index=get_objects_index_name(), id=instance_id)
        logger.debug(f"Deleted object '{instance_id}' from index")
        return True
    except Exception as e:
        logger.error(f"Failed to delete object '{instance_id}': {e}")
        return False


def get_object_facets(field_names: List[str]) -> Dict[str, List[Dict]]:
    """Get aggregations for specified fields (for dynamic facets)."""
    client = get_es_client()
    if client is None:
        return {}
    
    try:
        aggs = {field: {"terms": {"field": field, "size": 50}} for field in field_names}
        search_body = {"size": 0, "aggs": aggs}
        
        response = client.search(index=get_objects_index_name(), body=search_body)
        
        result = {}
        if "aggregations" in response:
            for agg_name, agg_data in response["aggregations"].items():
                if "buckets" in agg_data:
                    result[agg_name] = [{"key": b["key"], "count": b["doc_count"]} for b in agg_data["buckets"]]
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get facets: {e}")
        return {}
