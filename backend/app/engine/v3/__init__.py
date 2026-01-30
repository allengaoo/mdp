"""
MDP Platform V3.1 - Engine Module
CRUD operations for V3.1 metadata-driven architecture
"""

from app.engine.v3.project_crud import (
    create_project,
    get_project,
    list_projects,
    update_project,
    delete_project,
)

from app.engine.v3.ontology_crud import (
    # Shared Property
    create_shared_property,
    get_shared_property,
    list_shared_properties,
    update_shared_property,
    delete_shared_property,
    # Object Type Definition
    create_object_type_def,
    get_object_type_def,
    list_object_type_defs,
    # Object Type Version
    create_object_type_ver,
    get_object_type_ver,
    update_object_type_ver,
    # Object Full (Def + Current Ver)
    get_object_type_full,
    list_object_types_full,
    # Property Binding
    bind_property_to_object_ver,
    get_object_ver_properties,
    # Link Type
    create_link_type_def,
    get_link_type_def,
    list_link_type_defs,
    create_link_type_ver,
    get_link_type_full,
    list_link_types_full,
)

from app.engine.v3.context_crud import (
    create_project_object_binding,
    get_project_object_bindings,
    update_project_object_binding,
    delete_project_object_binding,
)

__all__ = [
    # Project
    "create_project", "get_project", "list_projects", "update_project", "delete_project",
    # Shared Property
    "create_shared_property", "get_shared_property", "list_shared_properties",
    "update_shared_property", "delete_shared_property",
    # Object Type
    "create_object_type_def", "get_object_type_def", "list_object_type_defs",
    "create_object_type_ver", "get_object_type_ver", "update_object_type_ver",
    "get_object_type_full", "list_object_types_full",
    "bind_property_to_object_ver", "get_object_ver_properties",
    # Link Type
    "create_link_type_def", "get_link_type_def", "list_link_type_defs",
    "create_link_type_ver", "get_link_type_full", "list_link_types_full",
    # Context
    "create_project_object_binding", "get_project_object_bindings",
    "update_project_object_binding", "delete_project_object_binding",
]
