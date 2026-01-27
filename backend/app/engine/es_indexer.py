"""
Elasticsearch Object Indexer Module
MDP Platform V3.1 - Global Search Module

Builds ES documents from object instances based on property search configuration.
Implements the "Smart Indexer" pattern with Triple Write support.
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from app.core.elastic_store import (
    ensure_objects_index,
    index_object,
    bulk_index_objects,
    delete_object,
)


def build_es_document(
    instance_id: str,
    object_type_api_name: str,
    object_type_display_name: str,
    row_data: Dict[str, Any],
    property_configs: List[Dict[str, Any]],
    title_property: Optional[str] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build an ES document from object instance data based on property configurations.
    
    Args:
        instance_id: Object instance ID
        object_type_api_name: Object type api_name (used as keyword)
        object_type_display_name: Object type display name
        row_data: Raw data row with property values
        property_configs: List of property configurations with fields:
            - api_name: Property API name
            - data_type: Property data type
            - is_searchable: Enable full-text search
            - is_filterable: Enable facets/filters
            - is_sortable: Enable sorting
            - is_title: Use as display name
        title_property: Name of property to use as display_name (optional)
        project_id: Project ID for filtering
        
    Returns:
        ES document dict ready for indexing
    """
    # Build properties object with suffixed field names
    properties = {}
    display_name = ""
    
    for prop_config in property_configs:
        api_name = prop_config.get("api_name") or prop_config.get("property_api_name")
        if not api_name:
            continue
            
        value = row_data.get(api_name)
        if value is None:
            continue
        
        # Convert value to string for text fields
        str_value = str(value) if value is not None else ""
        
        # Determine display name
        if prop_config.get("is_title") or api_name == title_property:
            display_name = str_value
        
        # Add field with appropriate suffix based on configuration
        if prop_config.get("is_searchable"):
            properties[f"{api_name}_txt"] = str_value
        
        if prop_config.get("is_filterable"):
            # For keyword fields, limit length
            kwd_value = str_value[:256] if len(str_value) > 256 else str_value
            properties[f"{api_name}_kwd"] = kwd_value
        
        if prop_config.get("is_sortable"):
            properties[f"{api_name}_val"] = str_value
    
    # Fallback display name
    if not display_name:
        display_name = row_data.get("name") or row_data.get("title") or f"{object_type_api_name}_{instance_id[:8]}"
    
    # Build final document
    doc = {
        "id": instance_id,
        "object_type": object_type_api_name,
        "object_type_display": object_type_display_name,
        "display_name": display_name,
        "properties": properties,
        "project_id": project_id,
    }
    
    return doc


def index_object_instance(
    instance_id: str,
    object_type_api_name: str,
    object_type_display_name: str,
    row_data: Dict[str, Any],
    property_configs: List[Dict[str, Any]],
    title_property: Optional[str] = None,
    project_id: Optional[str] = None
) -> bool:
    """
    Index a single object instance to ES.
    
    Returns:
        True if indexing succeeded
    """
    # Ensure index exists
    if not ensure_objects_index():
        logger.warning("Failed to ensure objects index, skipping ES indexing")
        return False
    
    doc = build_es_document(
        instance_id=instance_id,
        object_type_api_name=object_type_api_name,
        object_type_display_name=object_type_display_name,
        row_data=row_data,
        property_configs=property_configs,
        title_property=title_property,
        project_id=project_id,
    )
    
    return index_object(
        instance_id=doc["id"],
        object_type=doc["object_type"],
        display_name=doc["display_name"],
        properties=doc["properties"],
        object_type_display=doc["object_type_display"],
        project_id=doc["project_id"],
    )


def bulk_index_object_instances(
    objects: List[Dict[str, Any]],
    object_type_api_name: str,
    object_type_display_name: str,
    property_configs: List[Dict[str, Any]],
    title_property: Optional[str] = None,
    project_id: Optional[str] = None
) -> int:
    """
    Bulk index multiple object instances to ES.
    
    Args:
        objects: List of dicts with 'id' and row data
        object_type_api_name: Object type api_name
        object_type_display_name: Object type display name
        property_configs: Property configurations
        title_property: Property to use as display name
        project_id: Project ID
        
    Returns:
        Number of objects indexed
    """
    # Ensure index exists
    if not ensure_objects_index():
        logger.warning("Failed to ensure objects index, skipping ES bulk indexing")
        return 0
    
    if not objects:
        return 0
    
    # Build documents
    docs = []
    for obj in objects:
        doc = build_es_document(
            instance_id=obj["id"],
            object_type_api_name=object_type_api_name,
            object_type_display_name=object_type_display_name,
            row_data=obj,
            property_configs=property_configs,
            title_property=title_property,
            project_id=project_id,
        )
        docs.append(doc)
    
    return bulk_index_objects(docs)


def delete_object_instance(instance_id: str) -> bool:
    """
    Delete an object instance from ES index.
    
    Returns:
        True if deletion succeeded
    """
    return delete_object(instance_id)


def get_searchable_property_configs(
    property_bindings: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Filter property bindings to only those with search flags enabled.
    
    Args:
        property_bindings: List of property binding dicts from database
        
    Returns:
        Filtered list with search-enabled properties
    """
    return [
        pb for pb in property_bindings
        if pb.get("is_searchable") or pb.get("is_filterable") or pb.get("is_sortable")
    ]


def get_filterable_field_names(
    property_configs: List[Dict[str, Any]]
) -> List[str]:
    """
    Get list of filterable field names for facet aggregations.
    
    Args:
        property_configs: Property configurations
        
    Returns:
        List of field names with _kwd suffix
    """
    fields = ["object_type"]  # Always include object_type
    
    for config in property_configs:
        if config.get("is_filterable"):
            api_name = config.get("api_name") or config.get("property_api_name")
            if api_name:
                fields.append(f"properties.{api_name}_kwd")
    
    return fields
