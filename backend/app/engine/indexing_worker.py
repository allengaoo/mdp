"""
Indexing Worker - Background ETL for Triple Write Indexing
MDP Platform V3.1 - Multimodal Data Governance

Handles batch processing of mapping definitions:
1. Read source data from mdp_raw_store
2. Apply transformations
3. Triple write:
   - Scalar props -> MySQL (obj_instance_store)
   - Vector props -> ChromaDB (vector search)
   - Search props -> Elasticsearch (full-text search)
4. Write lineage records for traceability (vector -> source file)
5. Record job runs and metrics for observability
"""
import uuid
import random
import traceback
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

import pandas as pd
from sqlalchemy import create_engine, text

from app.core.config import settings
from app.core.logger import logger
from app.core.db import get_session_context
from app.core.vector_store import ensure_object_collection, upsert_vectors
from app.engine.v3 import mapping_crud
from app.engine.es_indexer import bulk_index_object_instances, build_es_document


# ==========================================
# Observability Classes
# ==========================================

@dataclass
class MetricsCollector:
    """Collects metrics during indexing job execution."""
    pk_collisions: int = 0
    ai_latency_total_ms: float = 0
    ai_inference_count: int = 0
    ai_low_confidence_count: int = 0
    vector_dim_mismatch: int = 0
    corrupt_media_files: int = 0
    transform_errors: int = 0
    
    def record_ai_latency(self, latency_ms: float):
        """Record AI inference latency."""
        self.ai_latency_total_ms += latency_ms
        self.ai_inference_count += 1
    
    def record_pk_collision(self):
        """Record a primary key collision."""
        self.pk_collisions += 1
    
    def record_corrupt_media(self):
        """Record a corrupt media file."""
        self.corrupt_media_files += 1
    
    def record_transform_error(self):
        """Record a transformation error."""
        self.transform_errors += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to JSON-serializable dict."""
        avg_latency = 0
        if self.ai_inference_count > 0:
            avg_latency = round(self.ai_latency_total_ms / self.ai_inference_count, 2)
        
        return {
            "pk_collisions": self.pk_collisions,
            "ai_latency_avg_ms": avg_latency,
            "ai_inference_count": self.ai_inference_count,
            "ai_low_confidence_count": self.ai_low_confidence_count,
            "vector_dim_mismatch": self.vector_dim_mismatch,
            "corrupt_media_files": self.corrupt_media_files,
            "transform_errors": self.transform_errors,
        }


@dataclass
class ErrorSampler:
    """Samples errors for debugging (Dead Letter Queue)."""
    max_samples: int = 100
    samples: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_error(
        self,
        raw_row_id: str,
        category: str,
        message: str,
        stack_trace: Optional[str] = None
    ):
        """Add an error sample if under limit."""
        if len(self.samples) >= self.max_samples:
            return
        
        self.samples.append({
            "id": str(uuid.uuid4()),
            "raw_row_id": raw_row_id,
            "error_category": category,
            "error_message": message[:2000],  # Truncate long messages
            "stack_trace": stack_trace[:5000] if stack_trace else None,
        })
    
    def get_samples(self) -> List[Dict[str, Any]]:
        """Get collected error samples."""
        return self.samples


# ==========================================
# Main Indexing Job
# ==========================================

def run_indexing_job(mapping_id: str):
    """
    Execute indexing job for a published mapping.
    
    This function runs as a background task after mapping publish.
    Records job run and metrics for observability.
    """
    logger.info(f"[IndexingWorker] Starting job for mapping: {mapping_id}")
    
    job_run_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    metrics = MetricsCollector()
    error_sampler = ErrorSampler(max_samples=100)
    
    object_def_id = None
    rows_processed = 0
    rows_indexed = 0
    status = "SUCCESS"
    
    try:
        with get_session_context() as session:
            # Load mapping definition
            mapping = mapping_crud.get_mapping(session, mapping_id)
            if not mapping:
                logger.error(f"[IndexingWorker] Mapping not found: {mapping_id}")
                status = "FAILED"
                return
            
            object_def_id = mapping.object_def_id
            
            if mapping.status != "PUBLISHED":
                logger.warning(f"[IndexingWorker] Mapping not published: {mapping_id}")
                status = "FAILED"
                return
            
            # Execute indexing
            result = _process_mapping(mapping, metrics, error_sampler)
            
            rows_processed = result.get("total_rows", 0)
            rows_indexed = result.get("rows_indexed", 0)
            
            # Determine final status
            if result.get("status") == "FAILED":
                status = "FAILED"
            elif rows_indexed < rows_processed:
                status = "PARTIAL_SUCCESS"
            else:
                status = "SUCCESS"
            
            logger.info(f"[IndexingWorker] Job completed for {mapping_id}: {result}")
            
    except Exception as e:
        logger.error(f"[IndexingWorker] Job failed for {mapping_id}: {e}")
        logger.error(traceback.format_exc())
        status = "FAILED"
        error_sampler.add_error(
            raw_row_id="N/A",
            category="SYSTEM",
            message=str(e),
            stack_trace=traceback.format_exc()
        )
    
    finally:
        end_time = datetime.utcnow()
        
        # Record job run
        _record_job_run(
            job_run_id=job_run_id,
            mapping_id=mapping_id,
            object_def_id=object_def_id or "unknown",
            start_time=start_time,
            end_time=end_time,
            status=status,
            rows_processed=rows_processed,
            rows_indexed=rows_indexed,
            metrics=metrics.to_dict()
        )
        
        # Record error samples
        if error_sampler.samples:
            _record_error_samples(job_run_id, error_sampler.get_samples())


def _process_mapping(
    mapping,
    metrics: MetricsCollector,
    error_sampler: ErrorSampler
) -> Dict[str, Any]:
    """
    Process a single mapping definition with Triple Write support.
    
    Returns: Statistics dict with row counts
    """
    mapping_id = mapping.id
    source_table = mapping.source_table_name
    mapping_spec = mapping.mapping_spec
    object_def_id = mapping.object_def_id
    
    logger.info(f"[IndexingWorker] Processing table: {source_table} -> {object_def_id}")
    
    # Identify file path columns for lineage (columns that contain file paths)
    file_path_columns = _identify_file_path_columns(mapping_spec)
    
    # Get object type info and property configs for ES indexing
    object_type_api_name = None
    object_type_display_name = None
    property_configs = []
    
    try:
        object_type_info = _get_object_type_info(object_def_id)
        if object_type_info:
            object_type_api_name = object_type_info.get("api_name")
            object_type_display_name = object_type_info.get("display_name")
            property_configs = object_type_info.get("property_configs", [])
            logger.info(f"[IndexingWorker] Object type: {object_type_api_name}, {len(property_configs)} properties with search flags")
    except Exception as e:
        logger.warning(f"[IndexingWorker] Failed to get object type info for ES indexing: {e}")
    
    # Connect to raw store
    raw_engine = create_engine(settings.raw_store_database_url)
    
    # Read source data in batches
    batch_size = 1000
    total_rows = 0
    total_indexed = 0
    total_vectors = 0
    total_lineage = 0
    
    query = f"SELECT * FROM {source_table}"
    
    try:
        for chunk_df in pd.read_sql(query, raw_engine, chunksize=batch_size):
            rows_processed, rows_indexed, vectors_indexed, lineage_written = _process_batch(
                df=chunk_df, 
                mapping_spec=mapping_spec, 
                object_def_id=object_def_id,
                mapping_id=mapping_id,
                source_table=source_table,
                file_path_columns=file_path_columns,
                metrics=metrics,
                error_sampler=error_sampler,
                # ES indexing parameters
                object_type_api_name=object_type_api_name,
                object_type_display_name=object_type_display_name,
                property_configs=property_configs
            )
            total_rows += rows_processed
            total_indexed += rows_indexed
            total_vectors += vectors_indexed
            total_lineage += lineage_written
            
            logger.info(f"[IndexingWorker] Processed batch: {rows_processed} rows, {rows_indexed} indexed, {vectors_indexed} vectors")
    
    except Exception as e:
        logger.error(f"[IndexingWorker] Processing failed: {e}")
        error_sampler.add_error(
            raw_row_id="N/A",
            category="SYSTEM",
            message=f"Batch processing failed: {str(e)}",
            stack_trace=traceback.format_exc()
        )
        return {
            "total_rows": total_rows,
            "rows_indexed": total_indexed,
            "total_vectors": total_vectors,
            "total_lineage": total_lineage,
            "status": "FAILED"
        }
    finally:
        raw_engine.dispose()
    
    return {
        "total_rows": total_rows,
        "rows_indexed": total_indexed,
        "total_vectors": total_vectors,
        "total_lineage": total_lineage,
        "status": "SUCCESS"
    }


def _identify_file_path_columns(mapping_spec: Dict[str, Any]) -> List[str]:
    """
    Identify source columns that contain file paths (for lineage tracking).
    
    Looks for columns connected to image/file embedding transforms.
    """
    nodes = mapping_spec.get("nodes", [])
    edges = mapping_spec.get("edges", [])
    
    node_map = {n["id"]: n for n in nodes}
    # Build reverse edge map: source -> targets
    source_to_targets = {}
    for edge in edges:
        src = edge["source"]
        if src not in source_to_targets:
            source_to_targets[src] = []
        source_to_targets[src].append(edge["target"])
    
    file_columns = []
    
    for node in nodes:
        if node.get("type") != "source":
            continue
        
        column = node.get("data", {}).get("column", node.get("column", ""))
        if not column:
            continue
        
        # Check if this source connects to a file-related transform
        target_ids = source_to_targets.get(node["id"], [])
        for tid in target_ids:
            target_node = node_map.get(tid)
            if target_node and target_node.get("type") == "transform":
                func = target_node.get("data", {}).get("function", "")
                if func in ("image_embedding_clip", "file_embedding"):
                    file_columns.append(column)
                    break
    
    return file_columns


def _process_batch(
    df: pd.DataFrame,
    mapping_spec: Dict[str, Any],
    object_def_id: str,
    mapping_id: str,
    source_table: str,
    file_path_columns: List[str],
    metrics: MetricsCollector,
    error_sampler: ErrorSampler,
    object_type_api_name: str = None,
    object_type_display_name: str = None,
    property_configs: List[Dict[str, Any]] = None
) -> tuple:
    """
    Process a batch of rows with Triple Write support.
    
    Returns: (rows_processed, rows_indexed, vectors_indexed, lineage_written)
    """
    nodes = mapping_spec.get("nodes", [])
    edges = mapping_spec.get("edges", [])
    
    # Build node lookup and edge graph
    node_map = {n["id"]: n for n in nodes}
    edge_map = {}
    for edge in edges:
        edge_map[edge["target"]] = edge["source"]
    
    # Identify vector properties
    vector_props = _identify_vector_properties(nodes, edge_map, node_map)
    
    scalar_records = []
    vector_records = []
    lineage_records = []
    rows_with_errors = 0
    
    # Determine the primary key column for source rows
    pk_column = None
    for col in ["id", "ID", "pk", "primary_key", "_id"]:
        if col in df.columns:
            pk_column = col
            break
    if pk_column is None and len(df.columns) > 0:
        pk_column = df.columns[0]
    
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        source_row_id = str(row_dict.get(pk_column, idx)) if pk_column else str(idx)
        
        try:
            # Generate unique ID for this object instance
            instance_id = str(uuid.uuid4())
            
            # Get file path for lineage (if any)
            source_file_path = None
            for col in file_path_columns:
                if col in row_dict and row_dict[col]:
                    source_file_path = str(row_dict[col])
                    break
            
            # Transform row (with timing for AI operations)
            transformed = _transform_row(row_dict, nodes, edge_map, node_map, metrics, error_sampler, source_row_id)
            
            # Separate scalar and vector properties
            scalar_data = {"id": instance_id, "object_def_id": object_def_id}
            vector_data = {"id": instance_id}
            has_vector = False
            
            for prop, value in transformed.items():
                if prop in vector_props:
                    if value is not None:
                        vector_data["vector"] = value
                        has_vector = True
                else:
                    scalar_data[prop] = value
            
            scalar_records.append(scalar_data)
            
            if has_vector:
                vector_records.append(vector_data)
            
            # Create lineage record for traceability
            lineage_records.append({
                "id": str(uuid.uuid4()),
                "object_def_id": object_def_id,
                "instance_id": instance_id,
                "mapping_id": mapping_id,
                "source_table": source_table,
                "source_row_id": source_row_id,
                "source_file_path": source_file_path,
                "vector_collection": f"obj_type_{object_def_id.replace('-', '_')}" if has_vector else None
            })
            
        except Exception as e:
            rows_with_errors += 1
            metrics.record_transform_error()
            error_sampler.add_error(
                raw_row_id=source_row_id,
                category="SEMANTIC",
                message=f"Row transformation failed: {str(e)}",
                stack_trace=traceback.format_exc()
            )
    
    # Write scalar data to MySQL (obj_instance_store)
    _write_scalar_data(scalar_records, object_def_id)
    
    # Write vector data to ChromaDB
    vectors_indexed = 0
    vector_collection = None
    if vector_records:
        vectors_indexed, vector_collection = _write_vector_data(vector_records, object_def_id)
        
        # Update lineage records with actual collection name
        if vector_collection:
            for rec in lineage_records:
                if rec["vector_collection"]:
                    rec["vector_collection"] = vector_collection
    
    # Write lineage records
    lineage_written = _write_lineage_data(lineage_records)
    
    # Write to Elasticsearch (Triple Write - Step 3)
    es_indexed = 0
    if property_configs and object_type_api_name:
        try:
            # Build ES documents from scalar records
            es_objects = []
            for rec in scalar_records:
                es_objects.append({
                    "id": rec["id"],
                    **{k: v for k, v in rec.items() if k not in ("id", "object_def_id")}
                })
            
            es_indexed = bulk_index_object_instances(
                objects=es_objects,
                object_type_api_name=object_type_api_name,
                object_type_display_name=object_type_display_name or object_type_api_name,
                property_configs=property_configs,
                title_property=None,  # Will be detected from is_title flag
                project_id=None
            )
            logger.info(f"[IndexingWorker] Indexed {es_indexed} objects to Elasticsearch")
        except Exception as e:
            logger.error(f"[IndexingWorker] ES indexing failed: {e}")
    
    rows_indexed = len(scalar_records) - rows_with_errors
    return len(df), rows_indexed, vectors_indexed, lineage_written


def _identify_vector_properties(
    nodes: List[Dict],
    edge_map: Dict[str, str],
    node_map: Dict[str, Dict]
) -> set:
    """
    Identify which target properties will contain vectors.
    """
    vector_props = set()
    
    for node in nodes:
        if node.get("type") != "target":
            continue
        
        prop = node.get("data", {}).get("property", node.get("property", ""))
        if not prop:
            continue
        
        # Check if this target is connected to a vector transform
        source_id = edge_map.get(node["id"])
        if source_id:
            source_node = node_map.get(source_id)
            if source_node and source_node.get("type") == "transform":
                func = source_node.get("data", {}).get("function", "")
                if func in ("image_embedding_clip", "text_embedding"):
                    vector_props.add(prop)
    
    return vector_props


def _transform_row(
    row: Dict[str, Any],
    nodes: List[Dict],
    edge_map: Dict[str, str],
    node_map: Dict[str, Dict],
    metrics: MetricsCollector,
    error_sampler: ErrorSampler,
    source_row_id: str
) -> Dict[str, Any]:
    """
    Apply transformations to a single row.
    """
    result = {}
    
    for node in nodes:
        if node.get("type") != "target":
            continue
        
        prop = node.get("data", {}).get("property", node.get("property", ""))
        if not prop:
            continue
        
        value = _resolve_value(node["id"], edge_map, node_map, row, metrics, error_sampler, source_row_id)
        result[prop] = value
    
    return result


def _resolve_value(
    node_id: str,
    edge_map: Dict[str, str],
    node_map: Dict[str, Dict],
    row: Dict[str, Any],
    metrics: MetricsCollector,
    error_sampler: ErrorSampler,
    source_row_id: str
) -> Any:
    """
    Recursively resolve value for a node.
    """
    node = node_map.get(node_id)
    if not node:
        return None
    
    node_type = node.get("type")
    node_data = node.get("data", {})
    
    if node_type == "source":
        column = node_data.get("column", node.get("column", ""))
        return row.get(column)
    
    elif node_type == "transform":
        func_name = node_data.get("function", node.get("function", ""))
        source_id = edge_map.get(node_id)
        
        if not source_id:
            return None
        
        input_value = _resolve_value(source_id, edge_map, node_map, row, metrics, error_sampler, source_row_id)
        return _apply_transform(func_name, input_value, metrics, error_sampler, source_row_id)
    
    elif node_type == "target":
        source_id = edge_map.get(node_id)
        if not source_id:
            return None
        return _resolve_value(source_id, edge_map, node_map, row, metrics, error_sampler, source_row_id)
    
    return None


def _apply_transform(
    func_name: str,
    input_value: Any,
    metrics: MetricsCollector,
    error_sampler: ErrorSampler,
    source_row_id: str
) -> Any:
    """
    Apply transformation function with timing and error handling.
    """
    if func_name == "image_embedding_clip":
        # Simulate AI inference with timing
        start_time = time.time()
        
        try:
            # Simulate corrupt media detection (random for demo)
            if random.random() < 0.01:  # 1% chance of corrupt file
                metrics.record_corrupt_media()
                error_sampler.add_error(
                    raw_row_id=source_row_id,
                    category="MEDIA_IO",
                    message=f"Corrupt or unreadable media file: {input_value}"
                )
                return None
            
            # Mock: Generate random 768-dim vector
            # In production, use actual CLIP model
            result = [round(random.uniform(-1, 1), 6) for _ in range(768)]
            
            # Record latency
            latency_ms = (time.time() - start_time) * 1000
            # Add simulated AI latency (50-300ms)
            latency_ms += random.uniform(50, 300)
            metrics.record_ai_latency(latency_ms)
            
            return result
            
        except Exception as e:
            metrics.record_transform_error()
            error_sampler.add_error(
                raw_row_id=source_row_id,
                category="AI_INFERENCE",
                message=f"Image embedding failed: {str(e)}",
                stack_trace=traceback.format_exc()
            )
            return None
    
    elif func_name == "text_embedding":
        start_time = time.time()
        
        try:
            # Mock: Generate random 768-dim vector
            result = [round(random.uniform(-1, 1), 6) for _ in range(768)]
            
            latency_ms = (time.time() - start_time) * 1000
            latency_ms += random.uniform(20, 100)  # Text is faster than image
            metrics.record_ai_latency(latency_ms)
            
            return result
            
        except Exception as e:
            metrics.record_transform_error()
            error_sampler.add_error(
                raw_row_id=source_row_id,
                category="AI_INFERENCE",
                message=f"Text embedding failed: {str(e)}"
            )
            return None
    
    elif func_name == "concat":
        return str(input_value) if input_value else ""
    
    elif func_name == "to_uppercase":
        return str(input_value).upper() if input_value else ""
    
    elif func_name == "to_lowercase":
        return str(input_value).lower() if input_value else ""
    
    elif func_name == "format_date":
        return input_value
    
    return input_value


def _write_scalar_data(records: List[Dict], object_def_id: str):
    """
    Write scalar properties to MySQL instance store.
    """
    if not records:
        return
    
    table_name = f"obj_instance_{object_def_id.replace('-', '_')}"
    
    df = pd.DataFrame(records)
    
    engine = create_engine(settings.raw_store_database_url)
    df.to_sql(table_name, engine, if_exists="append", index=False)
    engine.dispose()
    
    logger.info(f"[IndexingWorker] Wrote {len(records)} scalar records to {table_name}")


def _write_vector_data(records: List[Dict], object_def_id: str) -> tuple:
    """
    Write vector properties to ChromaDB.
    
    Returns: (count, collection_name)
    """
    if not records:
        return 0, None
    
    try:
        collection_name = ensure_object_collection(object_def_id, dimension=768)
        count = upsert_vectors(collection_name, records)
        
        logger.info(f"[IndexingWorker] Indexed {count} vectors to {collection_name}")
        return count, collection_name
        
    except Exception as e:
        logger.error(f"[IndexingWorker] Vector write failed: {e}")
        return 0, None


def _write_lineage_data(records: List[Dict]) -> int:
    """
    Write lineage records to MySQL for traceability.
    """
    if not records:
        return 0
    
    try:
        df = pd.DataFrame(records)
        
        engine = create_engine(settings.database_url)
        df.to_sql("ctx_object_instance_lineage", engine, if_exists="append", index=False)
        engine.dispose()
        
        logger.info(f"[IndexingWorker] Wrote {len(records)} lineage records")
        return len(records)
        
    except Exception as e:
        logger.error(f"[IndexingWorker] Lineage write failed: {e}")
        logger.error(traceback.format_exc())
        return 0


# ==========================================
# Object Type Info for ES Indexing
# ==========================================

def _get_object_type_info(object_def_id: str) -> Optional[Dict[str, Any]]:
    """
    Get object type info and property configurations for ES indexing.
    
    Returns dict with:
        - api_name: Object type API name
        - display_name: Object type display name
        - property_configs: List of property configs with search flags
    """
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # Get object type info
            obj_result = conn.execute(text("""
                SELECT 
                    otd.api_name,
                    otv.display_name
                FROM meta_object_type_def otd
                LEFT JOIN meta_object_type_ver otv ON otd.current_version_id = otv.id
                WHERE otd.id = :def_id
            """), {"def_id": object_def_id})
            
            obj_row = obj_result.fetchone()
            if not obj_row:
                return None
            
            api_name, display_name = obj_row
            
            # Get property configs with search flags
            props_result = conn.execute(text("""
                SELECT 
                    spd.api_name AS property_api_name,
                    spd.display_name AS property_display_name,
                    spd.data_type,
                    ovp.is_searchable,
                    ovp.is_filterable,
                    ovp.is_sortable,
                    ovp.is_title
                FROM rel_object_ver_property ovp
                JOIN meta_shared_property_def spd ON ovp.property_def_id = spd.id
                JOIN meta_object_type_ver otv ON ovp.object_ver_id = otv.id
                JOIN meta_object_type_def otd ON otv.def_id = otd.id
                WHERE otd.id = :def_id
                AND (ovp.is_searchable = 1 OR ovp.is_filterable = 1 OR ovp.is_sortable = 1 OR ovp.is_title = 1)
            """), {"def_id": object_def_id})
            
            property_configs = []
            for row in props_result:
                property_configs.append({
                    "api_name": row[0],
                    "display_name": row[1],
                    "data_type": row[2],
                    "is_searchable": bool(row[3]),
                    "is_filterable": bool(row[4]),
                    "is_sortable": bool(row[5]),
                    "is_title": bool(row[6]),
                })
        
        engine.dispose()
        
        return {
            "api_name": api_name,
            "display_name": display_name or api_name,
            "property_configs": property_configs
        }
        
    except Exception as e:
        logger.error(f"[IndexingWorker] Failed to get object type info: {e}")
        return None


# ==========================================
# Observability Recording
# ==========================================

def _record_job_run(
    job_run_id: str,
    mapping_id: str,
    object_def_id: str,
    start_time: datetime,
    end_time: datetime,
    status: str,
    rows_processed: int,
    rows_indexed: int,
    metrics: Dict[str, Any]
):
    """
    Record job run to sys_index_job_run table.
    """
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO sys_index_job_run 
                (id, mapping_id, object_def_id, start_time, end_time, status, 
                 rows_processed, rows_indexed, metrics_json, created_at)
                VALUES 
                (:id, :mapping_id, :object_def_id, :start_time, :end_time, :status,
                 :rows_processed, :rows_indexed, :metrics_json, :created_at)
            """), {
                "id": job_run_id,
                "mapping_id": mapping_id,
                "object_def_id": object_def_id,
                "start_time": start_time,
                "end_time": end_time,
                "status": status,
                "rows_processed": rows_processed,
                "rows_indexed": rows_indexed,
                "metrics_json": str(metrics).replace("'", '"'),  # Convert to JSON string
                "created_at": datetime.utcnow()
            })
            conn.commit()
        
        engine.dispose()
        logger.info(f"[IndexingWorker] Recorded job run: {job_run_id}, status={status}")
        
    except Exception as e:
        logger.error(f"[IndexingWorker] Failed to record job run: {e}")
        logger.error(traceback.format_exc())


def _record_error_samples(job_run_id: str, samples: List[Dict[str, Any]]):
    """
    Record error samples to sys_index_error_sample table.
    """
    if not samples:
        return
    
    try:
        # Add job_run_id and created_at to each sample
        for sample in samples:
            sample["job_run_id"] = job_run_id
            sample["created_at"] = datetime.utcnow()
        
        df = pd.DataFrame(samples)
        
        engine = create_engine(settings.database_url)
        df.to_sql("sys_index_error_sample", engine, if_exists="append", index=False)
        engine.dispose()
        
        logger.info(f"[IndexingWorker] Recorded {len(samples)} error samples")
        
    except Exception as e:
        logger.error(f"[IndexingWorker] Failed to record error samples: {e}")
        logger.error(traceback.format_exc())
