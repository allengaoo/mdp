import pytest
from httpx import AsyncClient
import uuid

def gen_name(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

@pytest.mark.anyio
async def test_v3_object_mapping_crud(client: AsyncClient):
    # Setup: Create Object Type
    obj_name = gen_name("test_map_obj")
    obj_resp = await client.post("/api/v3/ontology/object-types", json={"api_name": obj_name})
    obj_id = obj_resp.json()["id"]

    # 1. Create Mapping
    payload = {
        "object_def_id": obj_id,
        "source_connection_id": "conn-123", # Mock ID
        "source_table_name": "raw_users",
        "mapping_spec": {
            "nodes": [{"id": "1", "type": "source"}, {"id": "2", "type": "target"}],
            "edges": [{"source": "1", "target": "2"}]
        }
    }
    response = await client.post("/api/v3/mappings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["object_def_id"] == obj_id
    mapping_id = data["id"]

    # 2. Get Mapping
    response = await client.get(f"/api/v3/mappings/{mapping_id}")
    assert response.status_code == 200
    assert response.json()["id"] == mapping_id

    # 3. Update Mapping
    update_payload = {"source_table_name": "raw_users_v2"}
    response = await client.put(f"/api/v3/mappings/{mapping_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["source_table_name"] == "raw_users_v2"

    # 4. List Mappings
    response = await client.get("/api/v3/mappings")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # 5. Delete Mapping
    response = await client.delete(f"/api/v3/mappings/{mapping_id}")
    assert response.status_code == 200

    # Cleanup
    await client.delete(f"/api/v1/meta/object-types/{obj_id}")


@pytest.mark.anyio
async def test_v3_link_mapping_crud(client: AsyncClient):
    # Setup: Create Link Type
    obj1_name = gen_name("test_src_map")
    obj1 = await client.post("/api/v3/ontology/object-types", json={"api_name": obj1_name})
    obj2_name = gen_name("test_tgt_map")
    obj2 = await client.post("/api/v3/ontology/object-types", json={"api_name": obj2_name})
    
    link_name = gen_name("test_link_map")
    link_resp = await client.post("/api/v3/ontology/link-types", json={"api_name": link_name}, params={
        "source_object_def_id": obj1.json()["id"],
        "target_object_def_id": obj2.json()["id"],
        "cardinality": "MANY_TO_MANY"
    })
    link_id = link_resp.json()["id"]

    # 1. Create Link Mapping
    payload = {
        "link_def_id": link_id,
        "source_connection_id": "conn-456",
        "join_table_name": "raw_join_table",
        "source_key_column": "src_id",
        "target_key_column": "tgt_id",
        "property_mappings": {"role": "role_col"}
    }
    response = await client.post("/api/v3/mappings/link-mappings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["link_def_id"] == link_id
    mapping_id = data["id"]

    # 2. Get Link Mapping
    response = await client.get(f"/api/v3/mappings/link-mappings/by-def/{link_id}")
    assert response.status_code == 200
    assert response.json()["id"] == mapping_id

    # 3. Update Link Mapping
    update_payload = {"join_table_name": "raw_join_table_v2"}
    response = await client.put(f"/api/v3/mappings/link-mappings/{mapping_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["join_table_name"] == "raw_join_table_v2"

    # Cleanup
    await client.delete(f"/api/v1/meta/link-types/{link_id}")
    await client.delete(f"/api/v1/meta/object-types/{obj1.json()['id']}")
    await client.delete(f"/api/v1/meta/object-types/{obj2.json()['id']}")
