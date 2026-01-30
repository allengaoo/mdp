"""
Vector Store Module - ChromaDB Integration
MDP Platform V3.1 - Multimodal Data Governance

Provides serverless vector storage for unstructured data embeddings.
Migrated from Milvus to ChromaDB for better Windows compatibility.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.logger import logger
from app.core.config import settings

# Initialize ChromaDB client as None (lazy loading)
chroma_client: Optional[chromadb.PersistentClient] = None


def get_chroma_client() -> chromadb.PersistentClient:
    """Get or create ChromaDB client singleton."""
    global chroma_client
    if chroma_client is None:
        # Ensure data directory exists
        db_path = Path(settings.chroma_db_path)
        db_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[VectorStore] Initializing ChromaDB at {db_path}")
        chroma_client = chromadb.PersistentClient(
            path=str(db_path),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
    return chroma_client


def ensure_object_collection(
    object_type_id: str, 
    dimension: int = 768
) -> str:
    """
    Ensure a vector collection exists for an object type.
    
    Args:
        object_type_id: The ontology object type ID (used as collection name prefix)
        dimension: Vector dimension (default 768 for CLIP/BERT embeddings)
    
    Returns:
        Collection name
    """
    client = get_chroma_client()
    
    # Sanitize collection name (ChromaDB requires alphanumeric + underscore)
    collection_name = f"obj_{object_type_id.replace('-', '_')}"
    
    # Get or create collection with cosine similarity
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine", "dimension": dimension}
    )
    
    logger.debug(f"[VectorStore] Collection '{collection_name}' ready")
    return collection_name


def upsert_vectors(
    collection_name: str, 
    data: List[Dict[str, Any]]
) -> int:
    """
    Insert or update vectors in a collection.
    
    Args:
        collection_name: Target collection
        data: List of dicts with 'id' and 'vector' keys
              e.g., [{"id": "uuid-1", "vector": [0.1, 0.2, ...]}]
    
    Returns:
        Number of vectors upserted
    """
    if not data:
        return 0
    
    client = get_chroma_client()
    collection = client.get_or_create_collection(name=collection_name)
    
    # Prepare data for ChromaDB
    ids = []
    embeddings = []
    metadatas = []
    
    for item in data:
        if "id" not in item or "vector" not in item:
            raise ValueError("Each item must have 'id' and 'vector' keys")
        ids.append(item["id"])
        embeddings.append(item["vector"])
        # Include any additional metadata
        metadata = {k: v for k, v in item.items() if k not in ("id", "vector")}
        metadatas.append(metadata if metadata else {})
    
    # Upsert to ChromaDB
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    logger.info(f"[VectorStore] Upserted {len(ids)} vectors to '{collection_name}'")
    return len(ids)


def search_vectors(
    collection_name: str,
    query_vector: List[float],
    top_k: int = 10,
    filter_expr: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search for similar vectors.
    
    Args:
        collection_name: Collection to search
        query_vector: Query embedding
        top_k: Number of results to return
        filter_expr: Optional filter dict for ChromaDB where clause
    
    Returns:
        List of results with id, distance, and metadata
    """
    client = get_chroma_client()
    
    try:
        collection = client.get_collection(name=collection_name)
    except ValueError:
        logger.warning(f"[VectorStore] Collection '{collection_name}' not found")
        return []
    
    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        where=filter_expr,
        include=["embeddings", "metadatas", "distances"]
    )
    
    # Format results
    formatted = []
    if results and results.get("ids") and len(results["ids"]) > 0:
        ids = results["ids"][0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        
        for i, doc_id in enumerate(ids):
            result = {
                "id": doc_id,
                "distance": distances[i] if i < len(distances) else 0,
            }
            if i < len(metadatas) and metadatas[i]:
                result.update(metadatas[i])
            formatted.append(result)
    
    return formatted


def delete_vectors(collection_name: str, ids: List[str]) -> int:
    """
    Delete vectors by IDs.
    
    Args:
        collection_name: Collection name
        ids: List of vector IDs to delete
    
    Returns:
        Number of vectors deleted
    """
    if not ids:
        return 0
    
    client = get_chroma_client()
    
    try:
        collection = client.get_collection(name=collection_name)
        collection.delete(ids=ids)
        logger.info(f"[VectorStore] Deleted {len(ids)} vectors from '{collection_name}'")
        return len(ids)
    except ValueError:
        logger.warning(f"[VectorStore] Collection '{collection_name}' not found")
        return 0


def drop_collection(collection_name: str) -> bool:
    """
    Drop a collection entirely.
    
    Args:
        collection_name: Collection to drop
    
    Returns:
        True if dropped, False if didn't exist
    """
    client = get_chroma_client()
    
    try:
        client.delete_collection(name=collection_name)
        logger.info(f"[VectorStore] Dropped collection '{collection_name}'")
        return True
    except ValueError:
        return False


def get_collection_stats(collection_name: str) -> Optional[Dict[str, Any]]:
    """
    Get statistics for a collection.
    
    Returns:
        Dict with count, etc. or None if collection doesn't exist
    """
    client = get_chroma_client()
    
    try:
        collection = client.get_collection(name=collection_name)
        return {
            "row_count": collection.count(),
            "name": collection_name,
            "metadata": collection.metadata
        }
    except ValueError:
        return None


def list_collections() -> List[str]:
    """
    List all collection names.
    
    Returns:
        List of collection names
    """
    client = get_chroma_client()
    collections = client.list_collections()
    return [c.name for c in collections]


# Backward compatibility aliases
def get_milvus_client():
    """Deprecated: Use get_chroma_client() instead."""
    logger.warning("[VectorStore] get_milvus_client() is deprecated, use get_chroma_client()")
    return get_chroma_client()
