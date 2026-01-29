# MDP Code Architecture & Implementation Map

## 1. Architecture Overview

MDP (Metadata-Driven Platform) adopts a **V3 Architecture** that separates logical definitions from physical storage, implementing a "Metadata + Context" layered design.

```mermaid
graph TD
    UI[Frontend (React)] --> API[Backend API (FastAPI)]
    API --> Engine[Business Logic Engine]
    Engine --> Models[Data Models]
    Models --> DB[(Database)]
    
    subgraph "V3 Architecture Layers"
        Meta[Ontology Layer]
        Context[Context Layer]
        System[System Layer]
    end
```

## 2. Code Implementation Map

### 2.1 Presentation Layer (Frontend)

Located in `frontend/src/`.

| Component | Path | Responsibility | V3 API Client |
| :--- | :--- | :--- | :--- |
| **Studio** | `platform/Studio/` | Ontology modeling (Objects, Links). | `api/v3/ontology.ts` |
| **OMA** | `platform/OMA/` | Object management center. | `api/v3/objects.ts` |
| **DataLink** | `platform/DataLink/` | Connectors & Mappings. | `api/v3/connectors.ts`, `api/v3/mapping.ts` |
| **Explorer** | `platform/Explorer/` | Search & Graph analysis. | `api/v3/search.ts`, `api/v3/graph.ts` |

**Key Files:**
*   `frontend/src/api/v3/ontology.ts`: **Core Client**. Handles ObjectTypes, LinkTypes, SharedProperties.
*   `frontend/src/api/v3/mapping.ts`: Handles ObjectMapping and LinkMapping.

### 2.2 Interface Layer (Backend API)

Located in `backend/app/api/v3/`. **This is the standard entry point.**

| Module | File | Endpoints |
| :--- | :--- | :--- |
| **Ontology** | `ontology.py` | `/object-types`, `/link-types`, `/properties` |
| **Mapping** | `mapping.py` | `/mappings` (Object & Link mappings) |
| **Connectors** | `connectors.py` | `/connectors`, `/sync-jobs` |
| **Search** | `search.py` | `/search/objects` |
| **Graph** | `graph.py` | `/graph/expand` |

### 2.3 Business Logic Layer (Engine)

Located in `backend/app/engine/v3/`. **All complex logic resides here.**

| Module | File | Key Functions |
| :--- | :--- | :--- |
| **Ontology CRUD** | `ontology_crud.py` | `create_object_type_def`, `create_object_type_ver`, `bind_property_to_object_ver` |
| **Mapping CRUD** | `mapping_crud.py` | `create_mapping` (Object), `create_link_mapping` (Link) |
| **Sync Engine** | `sync_worker.py` | `run_sync_job` (Pandas ETL) |
| **Index Engine** | `indexing_worker.py` | `run_indexing_job` (Triple Write: SQL+ES+Chroma) |

**Legacy/Hybrid:**
*   `backend/app/engine/meta_crud.py`: **[Legacy]** Handles V1 requests. May call V3 functions internally. **Avoid modifying for new features.**

### 2.4 Data Access Layer (Models)

Located in `backend/app/models/`.

| Layer | File | Models | Description |
| :--- | :--- | :--- | :--- |
| **Ontology** | `ontology.py` | `ObjectTypeDef`, `ObjectTypeVer`, `ObjectVerProperty`, `LinkTypeDef`, `LinkTypeVer` | Core definitions. |
| **Context** | `context.py` | `ProjectObjectBinding`, `ObjectMappingDef`, `LinkMappingDef` | Contextual bindings & mappings. |
| **System** | `system.py` | `Connection`, `SyncJobDef` | Infrastructure configurations. |

## 3. Key Data Structures

### 3.1 Object Type Structure (V3)

```python
# 1. Definition (Immutable Identity)
ObjectTypeDef(id="obj-123", api_name="aircraft")

# 2. Version (Configuration)
ObjectTypeVer(id="ver-1", def_id="obj-123", version="1.0", status="PUBLISHED")

# 3. Property Binding (Composition)
ObjectVerProperty(
    ver_id="ver-1",
    property_def_id="prop-share-1", # Reference to Shared Property
    local_api_name="tail_number"    # Local override
)
```

### 3.2 Mapping Structure (V3)

```python
# 1. Object Mapping (Source Table -> Object)
ObjectMappingDef(
    object_def_id="obj-123",
    source_table_name="raw_aircraft_data",
    mapping_spec={...} # React Flow JSON
)

# 2. Link Mapping (Join Table -> Link)
LinkMappingDef(
    link_def_id="link-456",
    join_table_name="raw_flight_crew",
    source_key_column="aircraft_id",
    target_key_column="pilot_id"
)
```
