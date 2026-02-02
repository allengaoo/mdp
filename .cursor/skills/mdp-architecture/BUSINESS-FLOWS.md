# MDP Business Flows & Call Graphs

## 1. Object Type Management

### 1.1 Create Object Type (V3 Flow)

**Scenario**: User creates a new "Aircraft" object type in Studio.

```mermaid
sequenceDiagram
    participant UI as ObjectTypeWizard (Frontend)
    participant API as v1/ontology.py (Backend API)
    participant Engine as meta_crud.py (Hybrid Engine)
    participant V3CRUD as v3/ontology_crud.py
    participant DB as Database

    UI->>API: POST /api/v1/meta/object-types
    API->>Engine: create_object_type()
    Engine->>V3CRUD: create_object_type_def()
    V3CRUD->>DB: INSERT meta_object_type_def
    Engine->>V3CRUD: create_object_type_ver()
    V3CRUD->>DB: INSERT meta_object_type_ver
    
    loop For each property
        Engine->>V3CRUD: bind_property_to_object_ver()
        V3CRUD->>DB: INSERT rel_object_ver_property
    end
    
    Engine->>DB: INSERT ctx_project_object_binding
```

### 1.2 Edit Object Type (V3 Flow)

**Scenario**: User adds a property to "Aircraft".

```mermaid
sequenceDiagram
    participant UI as ObjectTypeEditor (Frontend)
    participant API as v1/ontology.py
    participant Engine as meta_crud.py
    participant V3CRUD as v3/ontology_crud.py
    participant DB as Database

    UI->>API: PUT /api/v1/meta/object-types/{id}
    API->>Engine: update_object_type()
    Engine->>V3CRUD: get_object_type_def()
    Engine->>V3CRUD: update_object_type_ver()
    
    rect rgb(240, 240, 240)
        note right of Engine: Property Synchronization
        Engine->>V3CRUD: get_object_ver_properties()
        Engine->>V3CRUD: bind_property_to_object_ver() (for new)
        Engine->>V3CRUD: unbind_property_from_object_ver() (for deleted)
    end
```

## 2. Link Type Management

### 2.1 Edit Link Type & Mapping (M:N)

**Scenario**: User configures a Many-to-Many link "Aircraft <-> Pilot" using a join table.

```mermaid
sequenceDiagram
    participant UI as LinkTypeEditor (Frontend)
    participant API_Ontology as v3/ontology.ts (Frontend API)
    participant API_Mapping as v3/mapping.py (Backend API)
    participant CRUD as v3/mapping_crud.py (Backend Engine)
    participant DB as Database

    Note over UI: User selects "MANY_TO_MANY" & Join Table
    
    UI->>API_Ontology: updateLinkMapping()
    API_Ontology->>API_Mapping: PUT /mappings/link-mappings/{id}
    API_Mapping->>CRUD: update_link_mapping()
    CRUD->>DB: UPDATE ctx_link_mapping_def
    
    Note over DB: Stores join_table_name, source_key, target_key
```

## 3. Data Ingestion & Indexing

### 3.1 Publish Mapping (Triple Write)

**Scenario**: User publishes a mapping to sync data.

```mermaid
sequenceDiagram
    participant UI as MappingEditor
    participant API as v3/mapping.py
    participant Worker as indexing_worker.py
    participant Raw as mdp_raw_store
    participant ES as Elasticsearch
    participant Chroma as ChromaDB
    participant SQL as ontology_raw_data

    UI->>API: POST /mappings/{id}/publish
    API->>Worker: Background Task: run_indexing_job()
    
    Worker->>Raw: SELECT * FROM source_table
    
    par Triple Write
        Worker->>SQL: INSERT INTO object_instances
        Worker->>ES: Index Document (Full Text)
        Worker->>Chroma: Upsert Vector (Embeddings)
    end
```

## 4. Search & Retrieval

### 4.1 Hybrid Search

**Scenario**: User searches for "Boeing engine failure".

```mermaid
sequenceDiagram
    participant UI as GlobalSearchPage
    participant API as v3/search.py
    participant Store as elastic_store.py
    participant ES as Elasticsearch
    participant Chroma as ChromaDB

    UI->>API: POST /search/objects
    API->>Store: search_objects(query)
    
    rect rgb(240, 248, 255)
        note right of Store: Hybrid Logic
        Store->>Chroma: Vector Search (Get Top K IDs)
        Store->>ES: Multi-match Query (Text) + ID Filter (Vector Results)
    end
    
    Store-->>API: Combined Results
    API-->>UI: JSON Response
```

## 5. Code Execution

### 5.1 Code Test Flow (Auto Selection)

**Scenario**: User tests function code in FunctionEditor.

```mermaid
sequenceDiagram
    participant UI as FunctionEditor (Frontend)
    participant API as v3/execute.py (Backend API)
    participant Executor as code_executor.py (Engine)
    participant Builtin as function_runner.py
    participant Subprocess as subprocess_runner.py

    UI->>API: POST /api/v3/execute/code/test
    Note right of UI: {code_content, context, executor_type: "auto"}
    
    API->>Executor: execute_code(request)
    
    rect rgb(255, 245, 238)
        note right of Executor: Auto Selection Logic
        Executor->>Executor: detect_imports(code)
        Executor->>Executor: detect_database_api_usage(code)
        Executor->>Executor: choose_executor()
    end
    
    alt Uses numpy/pandas
        Executor->>Subprocess: execute_in_subprocess()
        Subprocess-->>Executor: SubprocessResult
    else Simple code / DB access
        Executor->>Builtin: execute_code_direct()
        Builtin-->>Executor: ExecutionResult
    end
    
    Executor-->>API: CodeExecutionResponse
    API-->>UI: JSON Response
```

### 5.2 Remote Sandbox Execution

**Scenario**: User explicitly requests remote execution for security isolation.

```mermaid
sequenceDiagram
    participant UI as FunctionEditor (Frontend)
    participant API as v3/execute.py (Backend API)
    participant Executor as code_executor.py (Engine)
    participant Sandbox as mdp-sandbox (K8s Pod:8001)

    UI->>API: POST /api/v3/execute/code/test
    Note right of UI: {code_content, context, executor_type: "remote"}
    
    API->>Executor: execute_code(request)
    Executor->>Executor: executor_type == REMOTE
    
    rect rgb(240, 255, 240)
        note right of Executor: Remote Execution
        Executor->>Sandbox: HTTP POST /execute
        Note right of Sandbox: {code_content, context, timeout_seconds}
        Sandbox->>Sandbox: subprocess.run(python -c wrapper_code)
        Sandbox-->>Executor: JSON Response
    end
    
    Executor-->>API: CodeExecutionResponse
    API-->>UI: JSON Response
```

### 5.3 Sandbox Service Internal Flow

**Scenario**: Inside the Sandbox Pod, how code is executed.

```mermaid
sequenceDiagram
    participant Client as Backend (httpx)
    participant API as sandbox/main.py
    participant Wrapper as wrapper_code
    participant UserCode as User's main()

    Client->>API: POST /execute
    API->>API: indent_code(user_code)
    API->>API: Generate wrapper_code
    
    rect rgb(255, 250, 240)
        note right of API: Subprocess Execution
        API->>Wrapper: subprocess.run([python, -c, wrapper_code])
        Wrapper->>Wrapper: Read context from stdin
        Wrapper->>UserCode: Call main(context)
        UserCode-->>Wrapper: Return result
        Wrapper->>Wrapper: JSON output to stdout
        Wrapper-->>API: Capture stdout/stderr
    end
    
    API-->>Client: CodeExecuteResponse
```
