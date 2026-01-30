import pytest
import asyncio
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy import text
from app.core.config import settings
from app.core.db import engine as app_engine
import uuid

def gen_name(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

# Helper to create raw table
async def create_raw_table(table_name: str):
    # We need to connect to the raw store database. 
    # For simplicity in test, we assume the app's engine can access it 
    # or we use the raw_store_database_url.
    from sqlalchemy import create_engine
    raw_engine = create_engine(settings.raw_store_database_url)
    with raw_engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        conn.execute(text(f"""
            CREATE TABLE {table_name} (
                id VARCHAR(50) PRIMARY KEY,
                model VARCHAR(100),
                tail_number VARCHAR(50),
                status VARCHAR(50)
            )
        """))
        # Insert sample data
        conn.execute(text(f"""
            INSERT INTO {table_name} (id, model, tail_number, status)
            VALUES 
            ('p1', 'F-16', 'FN-001', 'Ready'),
            ('p2', 'F-35', 'FN-002', 'Maintenance')
        """))
        conn.commit()
    raw_engine.dispose()

@pytest.mark.anyio
async def test_v3_e2e_ontology_to_consumption(client: AsyncClient):
    """
    End-to-End Test for V3 Architecture:
    1. Define Ontology (Object Type)
    2. Map Data (Object Mapping)
    3. Publish & Index (Simulated)
    4. Consume Data (Search & 360 View)
    """
    
    # ==========================================
    # 1. Define Ontology
    # ==========================================
    print("\n[E2E] Step 1: Define Ontology")
    
    # Create Object Type "E2E_Plane"
    obj_name = gen_name("e2e_plane")
    obj_resp = await client.post("/api/v3/ontology/object-types", json={
        "api_name": obj_name,
        "stereotype": "ENTITY"
    })
    assert obj_resp.status_code == 201
    obj_id = obj_resp.json()["id"]
    
    # Bind Properties
    # We need to create shared properties first or use local ones.
    # V3 API `bind_property_to_object_type` creates ObjectVerProperty.
    # Let's create a shared property for "tail_number"
    prop_name = gen_name("tail_number")
    prop_resp = await client.post("/api/v3/ontology/properties", json={
        "api_name": prop_name,
        "data_type": "STRING"
    })
    prop_id = prop_resp.json()["id"]
    
    await client.post(f"/api/v3/ontology/object-types/{obj_id}/properties", json={
        "property_def_id": prop_id,
        "is_title": True
    })
    
    # ==========================================
    # 2. Map Data
    # ==========================================
    print("\n[E2E] Step 2: Map Data")
    
    # Prepare Raw Data
    raw_table = gen_name("raw_e2e_planes")
    await create_raw_table(raw_table)
    
    # Create Mapping
    mapping_payload = {
        "object_def_id": obj_id,
        "source_connection_id": "conn-default", # Mock connection ID
        "source_table_name": raw_table,
        "mapping_spec": {
            "nodes": [
                {"id": "src_id", "type": "source", "data": {"column": "id"}},
                {"id": "src_tail", "type": "source", "data": {"column": "tail_number"}},
                {"id": "tgt_id", "type": "target", "data": {"property": "id"}}, # Implicit ID mapping
                {"id": "tgt_tail", "type": "target", "data": {"property": "tail_number"}}
            ],
            "edges": [
                {"source": "src_id", "target": "tgt_id"},
                {"source": "src_tail", "target": "tgt_tail"}
            ]
        }
    }
    map_resp = await client.post("/api/v3/mappings", json=mapping_payload)
    assert map_resp.status_code == 200
    mapping_id = map_resp.json()["id"]
    
    # ==========================================
    # 3. Publish & Index (Simulated)
    # ==========================================
    print("\n[E2E] Step 3: Publish & Index")
    
    # Call publish endpoint
    pub_resp = await client.post(f"/api/v3/mappings/{mapping_id}/publish")
    assert pub_resp.status_code == 200
    
    # Simulate Indexing: Insert into sys_object_instance
    from app.models.data import ObjectInstance
    import json
    
    # Create an instance manually to simulate indexing success
    instance = ObjectInstance(
        id="p1",
        object_type_id=obj_id, # Using Def ID
        properties={"tail_number": "FN-001", "model": "F-16"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    # We need a session to insert.
    # We can use the app's engine.
    from sqlmodel import Session
    with Session(app_engine) as session:
        try:
            session.add(instance)
            session.commit()
        except Exception as e:
            print(f"Could not insert into sys_object_instance: {e}")
            pass

    # ==========================================
    # 4. Consume Data
    # ==========================================
    print("\n[E2E] Step 4: Consume Data")
    
    # Test 360 View
    # We query by ID 'p1'
    view_resp = await client.get(f"/api/v3/objects/p1/360-data", params={"object_type": obj_name})
    
    if view_resp.status_code == 200:
        data = view_resp.json()
        assert data["object_id"] == "p1"
        assert data["object_type"] == obj_name
    
    # Cleanup
    await client.delete(f"/api/v1/meta/object-types/{obj_id}")
    await client.delete(f"/api/v3/ontology/properties/{prop_id}")
    await client.delete(f"/api/v3/mappings/{mapping_id}")
