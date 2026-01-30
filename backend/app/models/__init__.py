"""
MDP Platform V3.1 - Models Package
Metadata-Driven Architecture
"""

# ==========================================
# V3.1 Models - System Layer
# ==========================================
from app.models.system import (
    # ORM Models
    Project,
    Connection,
    Dataset,
    # DTOs
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    ProjectWithStats,
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionRead,
    DatasetCreate,
    DatasetUpdate,
    DatasetRead,
    DatasetWithConnection,
)

# ==========================================
# V3.1 Models - Ontology Layer
# ==========================================
from app.models.ontology import (
    # ORM Models
    SharedPropertyDef,
    ObjectTypeDef,
    ObjectTypeVer,
    ObjectVerProperty,
    LinkTypeDef,
    LinkTypeVer,
    LinkVerProperty,
    # DTOs - Shared Property
    SharedPropertyDefCreate,
    SharedPropertyDefUpdate,
    SharedPropertyDefRead,
    # DTOs - Object Type
    ObjectTypeDefCreate,
    ObjectTypeDefRead,
    ObjectTypeVerCreate,
    ObjectTypeVerUpdate,
    ObjectTypeVerRead,
    ObjectTypeFullRead,
    ObjectVerPropertyCreate,
    ObjectVerPropertyRead,
    # DTOs - Link Type
    LinkTypeDefCreate,
    LinkTypeDefRead,
    LinkTypeVerCreate,
    LinkTypeVerUpdate,
    LinkTypeVerRead,
    LinkTypeFullRead,
)

# ==========================================
# V3.1 Models - Pipeline Layer
# ==========================================
from app.models.pipeline import (
    # ORM Models
    PipelineDef,
    SyncTask,
    # DTOs
    PipelineDefCreate,
    PipelineDefUpdate,
    PipelineDefRead,
    PipelineDefWithDetails,
    SyncTaskCreate,
    SyncTaskUpdate,
    SyncTaskRead,
    SyncTaskWithPipeline,
)

# ==========================================
# V3.1 Models - Workshop Layer
# ==========================================
from app.models.workshop import (
    # ORM Models
    AppDefinition,
    AppModule,
    AppWidget,
    # DTOs
    AppDefinitionCreate,
    AppDefinitionUpdate,
    AppDefinitionRead,
    AppDefinitionWithModules,
    AppModuleCreate,
    AppModuleUpdate,
    AppModuleRead,
    AppModuleWithWidgets,
    AppWidgetCreate,
    AppWidgetUpdate,
    AppWidgetRead,
)

# ==========================================
# V3.1 Models - Context Layer
# ==========================================
from app.models.context import (
    # ORM Models
    ProjectObjectBinding,
    # DTOs
    ProjectObjectBindingCreate,
    ProjectObjectBindingUpdate,
    ProjectObjectBindingRead,
    ProjectObjectBindingWithDetails,
)

# ==========================================
# Legacy Models (V2) - Kept for backward compatibility
# Will be removed after migration complete
# ==========================================
# from app.models.meta import (
#     Project as LegacyProject,
#     ObjectType as LegacyObjectType,
#     LinkType as LegacyLinkType,
#     FunctionDefinition,
#     ActionDefinition,
#     SharedProperty as LegacySharedProperty,
# )
# from app.models.data import (
#     ObjectInstance,
#     LinkInstance,
#     DataSourceTable,
#     ExecutionLog,
# )


__all__ = [
    # System
    "Project", "Connection", "Dataset",
    "ProjectCreate", "ProjectUpdate", "ProjectRead", "ProjectWithStats",
    "ConnectionCreate", "ConnectionUpdate", "ConnectionRead",
    "DatasetCreate", "DatasetUpdate", "DatasetRead", "DatasetWithConnection",
    # Ontology
    "SharedPropertyDef", "ObjectTypeDef", "ObjectTypeVer", "ObjectVerProperty",
    "LinkTypeDef", "LinkTypeVer", "LinkVerProperty",
    "SharedPropertyDefCreate", "SharedPropertyDefUpdate", "SharedPropertyDefRead",
    "ObjectTypeDefCreate", "ObjectTypeDefRead",
    "ObjectTypeVerCreate", "ObjectTypeVerUpdate", "ObjectTypeVerRead", "ObjectTypeFullRead",
    "ObjectVerPropertyCreate", "ObjectVerPropertyRead",
    "LinkTypeDefCreate", "LinkTypeDefRead",
    "LinkTypeVerCreate", "LinkTypeVerUpdate", "LinkTypeVerRead", "LinkTypeFullRead",
    # Pipeline
    "PipelineDef", "SyncTask",
    "PipelineDefCreate", "PipelineDefUpdate", "PipelineDefRead", "PipelineDefWithDetails",
    "SyncTaskCreate", "SyncTaskUpdate", "SyncTaskRead", "SyncTaskWithPipeline",
    # Workshop
    "AppDefinition", "AppModule", "AppWidget",
    "AppDefinitionCreate", "AppDefinitionUpdate", "AppDefinitionRead", "AppDefinitionWithModules",
    "AppModuleCreate", "AppModuleUpdate", "AppModuleRead", "AppModuleWithWidgets",
    "AppWidgetCreate", "AppWidgetUpdate", "AppWidgetRead",
    # Context
    "ProjectObjectBinding",
    "ProjectObjectBindingCreate", "ProjectObjectBindingUpdate", 
    "ProjectObjectBindingRead", "ProjectObjectBindingWithDetails",
]
