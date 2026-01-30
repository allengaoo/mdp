import pytest
from httpx import AsyncClient
import uuid

def gen_name(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

@pytest.mark.anyio
async def test_v3_shared_property_crud(client: AsyncClient):
    # 1. Create Shared Property
    api_name = gen_name("test_v3_prop")
    payload = {
        "api_name": api_name,
        "display_name": "Test V3 Property",
        "data_type": "STRING",
        "description": "A test property"
    }
    response = await client.post("/api/v3/ontology/properties", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["api_name"] == payload["api_name"]
    prop_id = data["id"]

    # 2. Get Shared Property
    response = await client.get(f"/api/v3/ontology/properties/{prop_id}")
    assert response.status_code == 200
    assert response.json()["id"] == prop_id

    # 3. Update Shared Property
    update_payload = {"display_name": "Updated V3 Property"}
    response = await client.patch(f"/api/v3/ontology/properties/{prop_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["display_name"] == "Updated V3 Property"

    # 4. List Shared Properties
    response = await client.get("/api/v3/ontology/properties")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # 5. Delete Shared Property
    response = await client.delete(f"/api/v3/ontology/properties/{prop_id}")
    assert response.status_code == 204

    # Verify deletion
    response = await client.get(f"/api/v3/ontology/properties/{prop_id}")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_v3_object_type_crud(client: AsyncClient):
    # 1. Create Object Type
    api_name = gen_name("test_v3_object")
    payload = {
        "api_name": api_name,
        "stereotype": "ENTITY"
    }
    response = await client.post("/api/v3/ontology/object-types", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["api_name"] == payload["api_name"]
    obj_id = data["id"]
    
    # Check initial version
    assert data["version_number"] == "1.0"
    ver_id = data["version_id"]

    # 2. Get Object Type
    response = await client.get(f"/api/v3/ontology/object-types/{obj_id}")
    assert response.status_code == 200
    assert response.json()["id"] == obj_id

    # 3. Create New Version
    ver_payload = {
        "def_id": obj_id,
        "version_number": "1.1",
        "display_name": "V3 Object v1.1",
        "status": "DRAFT"
    }
    response = await client.post(f"/api/v3/ontology/object-types/{obj_id}/versions", json=ver_payload)
    assert response.status_code == 201
    new_ver_id = response.json()["id"]

    # 4. Bind Property to Version
    # First create a shared property
    prop_name = gen_name("test_v3_obj_prop")
    prop_resp = await client.post("/api/v3/ontology/properties", json={
        "api_name": prop_name,
        "data_type": "INTEGER"
    })
    prop_id = prop_resp.json()["id"]

    bind_payload = {
        "property_def_id": prop_id,
        "is_required": True
    }
    
    response = await client.post(f"/api/v3/ontology/object-types/{obj_id}/properties", json=bind_payload)
    assert response.status_code == 201

    # 5. Get Properties
    response = await client.get(f"/api/v3/ontology/object-types/{obj_id}/properties")
    assert response.status_code == 200
    props = response.json()
    assert len(props) == 1
    assert props[0]["property_def_id"] == prop_id

    # Cleanup
    response = await client.delete(f"/api/v1/meta/object-types/{obj_id}")
    assert response.status_code == 204
    
    await client.delete(f"/api/v3/ontology/properties/{prop_id}")


@pytest.mark.anyio
async def test_v3_link_type_crud(client: AsyncClient):
    # Setup: Create two object types
    obj1_name = gen_name("test_src_obj")
    obj1 = await client.post("/api/v3/ontology/object-types", json={"api_name": obj1_name})
    obj1_id = obj1.json()["id"]
    
    obj2_name = gen_name("test_tgt_obj")
    obj2 = await client.post("/api/v3/ontology/object-types", json={"api_name": obj2_name})
    obj2_id = obj2.json()["id"]

    # 1. Create Link Type
    link_name = gen_name("test_link_rel")
    payload = {
        "api_name": link_name
    }
    params = {
        "source_object_def_id": obj1_id,
        "target_object_def_id": obj2_id,
        "cardinality": "MANY_TO_MANY",
        "display_name": "Test Link"
    }
    response = await client.post("/api/v3/ontology/link-types", json=payload, params=params)
    assert response.status_code == 201
    data = response.json()
    assert data["api_name"] == payload["api_name"]
    assert data["source_object_def_id"] == obj1_id
    link_id = data["id"]

    # 2. Get Link Type
    response = await client.get(f"/api/v3/ontology/link-types/{link_id}")
    assert response.status_code == 200
    assert response.json()["id"] == link_id

    # 3. List Link Types
    response = await client.get("/api/v3/ontology/link-types")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # Cleanup
    # Using V1 delete for now
    await client.delete(f"/api/v1/meta/link-types/{link_id}")
    await client.delete(f"/api/v1/meta/object-types/{obj1_id}")
    await client.delete(f"/api/v1/meta/object-types/{obj2_id}")
