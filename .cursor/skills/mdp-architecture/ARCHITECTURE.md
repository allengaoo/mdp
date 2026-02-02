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
    
    subgraph "Code Execution"
        Executor[code_executor.py]
        Builtin[builtin executor]
        Subprocess[subprocess executor]
        Remote[remote sandbox]
        Sandbox[K8s Sandbox Pod]
    end
    
    Executor --> Builtin
    Executor --> Subprocess
    Executor --> Remote
    Remote --> Sandbox
```

## 2. Code Implementation Map

### 2.1 Presentation Layer (Frontend)

Located in `frontend/src/`.

| Component | Path | Responsibility | V3 API Client |
| :--- | :--- | :--- | :--- |
| **Studio** | `platform/Studio/` | Ontology modeling (Objects, Links, Functions). | `api/v3/ontology.ts` |
| **OMA** | `platform/OMA/` | Object management center. | `api/v3/objects.ts` |
| **DataLink** | `platform/DataLink/` | Connectors & Mappings. | `api/v3/connectors.ts`, `api/v3/mapping.ts` |
| **Explorer** | `platform/Explorer/` | Search & Graph analysis. | `api/v3/search.ts`, `api/v3/graph.ts` |

**Key Files:**
*   `frontend/src/api/v3/ontology.ts`: **Core Client**. Handles ObjectTypes, LinkTypes, SharedProperties.
*   `frontend/src/api/v3/mapping.ts`: Handles ObjectMapping and LinkMapping.
*   `frontend/src/api/v3/client.ts`: V3 Axios instance with `baseURL: /api/v3`.
*   `frontend/src/api/axios.ts`: V1 Axios instance with `baseURL: /api/v1`.

### 2.2 Interface Layer (Backend API)

Located in `backend/app/api/v3/`. **This is the standard entry point.**

| Module | File | Endpoints |
| :--- | :--- | :--- |
| **Ontology** | `ontology.py` | `/object-types`, `/link-types`, `/properties` |
| **Mapping** | `mapping.py` | `/mappings` (Object & Link mappings) |
| **Connectors** | `connectors.py` | `/connectors`, `/sync-jobs` |
| **Search** | `search.py` | `/search/objects` |
| **Graph** | `graph.py` | `/graph/expand` |
| **Execute** | `execute.py` | `/execute/code/test`, `/execute/function/{id}/test` |
| **Health** | `health.py` | `/health/summary`, `/health/objects/{id}/history` |
| **Chat** | `chat.py` | `/chat/message` |

### 2.3 Business Logic Layer (Engine)

Located in `backend/app/engine/`. **All complex logic resides here.**

| Module | File | Key Functions |
| :--- | :--- | :--- |
| **Ontology CRUD** | `v3/ontology_crud.py` | `create_object_type_def`, `create_object_type_ver`, `bind_property_to_object_ver` |
| **Mapping CRUD** | `v3/mapping_crud.py` | `create_mapping` (Object), `create_link_mapping` (Link) |
| **Sync Engine** | `sync_worker.py` | `run_sync_job` (Pandas ETL) |
| **Index Engine** | `indexing_worker.py` | `run_indexing_job` (Triple Write: SQL+ES+Chroma) |
| **Code Executor** | `code_executor.py` | `execute_code`, `execute_in_sandbox`, `choose_executor` |

**Legacy/Hybrid:**
*   `backend/app/engine/meta_crud.py`: **[Legacy]** Handles V1 requests. May call V3 functions internally. **Avoid modifying for new features.**

### 2.4 Data Access Layer (Models)

Located in `backend/app/models/`.

| Layer | File | Models | Description |
| :--- | :--- | :--- | :--- |
| **Ontology** | `ontology.py` | `ObjectTypeDef`, `ObjectTypeVer`, `ObjectVerProperty`, `LinkTypeDef`, `LinkTypeVer` | Core definitions. |
| **Context** | `context.py` | `ProjectObjectBinding`, `ObjectMappingDef`, `LinkMappingDef` | Contextual bindings & mappings. |
| **System** | `system.py` | `Connection`, `SyncJobDef` | Infrastructure configurations. |

### 2.5 Sandbox Service (Isolated Execution)

Located in `backend/sandbox/`. **Deployed as a separate K8s Pod.**

| File | Responsibility |
| :--- | :--- |
| `main.py` | FastAPI service for isolated code execution |
| `Dockerfile` | Docker image configuration |
| `requirements.txt` | Dependencies |

**K8s Deployment:** `k8s/sandbox-deployment.yaml`

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

### 3.3 Code Execution Request/Response

```python
# Request
CodeExecutionRequest(
    code_content="def main(ctx): return ctx['x'] * 2",
    context={"x": 21},
    executor_type=ExecutorType.AUTO,  # auto, builtin, subprocess, remote
    timeout_seconds=30
)

# Response
CodeExecutionResponse(
    success=True,
    result=42,
    stdout="",
    stderr="",
    execution_time_ms=15,
    executor_used="builtin",  # or "subprocess", "remote"
    error_message=None
)
```

## 4. Code Execution Architecture

### 4.1 Executor Types

| Type | Module | Use Case | Pros | Cons |
| :--- | :--- | :--- | :--- | :--- |
| **builtin** | `function_runner.py` | Simple code, DB access | Fast, DB access | No isolation |
| **subprocess** | `subprocess_runner.py` | Complex compute, numpy/pandas | Isolation, timeout | Slower startup |
| **remote** | `code_executor.py` → Sandbox | Production, security | Full isolation, K8s resources | Network latency |

### 4.2 Auto Selection Logic

```python
def choose_executor(code_content, has_session):
    imports = detect_imports(code_content)
    uses_db_api = detect_database_api_usage(code_content)
    
    # If uses numpy/pandas → subprocess
    if imports & SUBPROCESS_REQUIRED_IMPORTS:
        return ExecutorType.SUBPROCESS
    
    # If uses DB API and has session → builtin
    if uses_db_api and has_session:
        return ExecutorType.BUILTIN
    
    # Default → builtin (faster)
    return ExecutorType.BUILTIN
```

### 4.3 Remote Sandbox Flow

```
Frontend                    Backend                     K8s Sandbox Pod
   │                          │                              │
   ├── POST /execute/code/test─┤                              │
   │   {executor_type:"remote"}│                              │
   │                          │                              │
   │                          ├── HTTP POST /execute ────────►│
   │                          │   {code_content, context}     │
   │                          │                              │
   │                          │◄── JSON Response ────────────┤
   │                          │   {success, result, stdout}   │
   │                          │                              │
   │◄── Response ─────────────┤                              │
```

## 5. Configuration

### 5.1 Sandbox Configuration (config.py)

```python
class Settings(BaseSettings):
    # Sandbox Configuration
    sandbox_url: str = "http://mdp-sandbox:8001"  # K8s service URL
    sandbox_enabled: bool = True
    sandbox_timeout: int = 30
    default_executor: str = "auto"  # auto, builtin, subprocess, remote
```

### 5.2 K8s Service Discovery

- **In-cluster**: `http://mdp-sandbox:8001` (K8s Service DNS)
- **Local dev**: `http://localhost:8001` (port-forward)

## 6. API Versioning Strategy

| API | Prefix | Status | Use Case |
| :--- | :--- | :--- | :--- |
| **V1** | `/api/v1/meta` | Legacy/Compat | CRUD operations (internally calls V3) |
| **V3** | `/api/v3` | Active | All new features, versioning, search, graph |

## 7. File Quick Reference

### Backend Key Files

| File | Responsibility |
| :--- | :--- |
| `app/main.py` | FastAPI app entry, router registration |
| `app/api/v3/__init__.py` | V3 router aggregation |
| `app/engine/code_executor.py` | Code execution dispatcher |
| `app/core/config.py` | Settings (DB, ES, Sandbox, Ollama) |
| `app/models/ontology.py` | Core ontology models |

### Frontend Key Files

| File | Responsibility |
| :--- | :--- |
| `src/App.tsx` | Route definitions |
| `src/api/v3/client.ts` | V3 Axios instance |
| `src/platform/Studio/FunctionEditor.tsx` | Function code editing & testing |
| `src/platform/Studio/FunctionWizard.tsx` | Function creation wizard |
