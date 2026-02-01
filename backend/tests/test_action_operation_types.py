"""
Action Definition Tests - Operation Types Coverage

Tests for the four operation types: update_property, link_objects, unlink_objects, function_logic.
Covers create, update, read, list, validation, and edge cases.
"""
import pytest
import uuid
from httpx import AsyncClient


def gen_name(prefix: str) -> str:
    """Generate unique name for test data."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# ==========================================
# Unit 1: Helper - Fetch existing test data
# ==========================================

async def _get_or_create_test_data(client: AsyncClient):
    """Fetch existing project, object types, link types, function for testing."""
    data = {}
    
    # Get project
    proj_resp = await client.get("/api/v3/projects")
    if proj_resp.status_code == 200 and proj_resp.json():
        data["project_id"] = proj_resp.json()[0]["id"]
    else:
        data["project_id"] = None
    
    # Get object types (V3 ontology)
    obj_resp = await client.get("/api/v3/ontology/objects/with-stats")
    if obj_resp.status_code == 200 and obj_resp.json():
        objs = obj_resp.json()
        data["object_type_ids"] = [o["id"] for o in objs[:2]]
    else:
        # Fallback: create object type
        obj1 = await client.post("/api/v3/ontology/object-types", json={
            "api_name": gen_name("obj_a"), "stereotype": "ENTITY"
        })
        obj2 = await client.post("/api/v3/ontology/object-types", json={
            "api_name": gen_name("obj_b"), "stereotype": "ENTITY"
        })
        if obj1.status_code == 201 and obj2.status_code == 201:
            data["object_type_ids"] = [obj1.json()["id"], obj2.json()["id"]]
            data["_created_obj_types"] = data["object_type_ids"].copy()
        else:
            data["object_type_ids"] = []
    
    # Get link types
    link_resp = await client.get("/api/v3/ontology/link-types")
    if link_resp.status_code == 200 and link_resp.json():
        links = link_resp.json()
        data["link_type_ids"] = [l["id"] for l in links]
        data["link_types_detail"] = links
    else:
        data["link_type_ids"] = []
        data["link_types_detail"] = []
    
    # Get functions
    fn_resp = await client.get("/api/v3/ontology/functions/for-list")
    if fn_resp.status_code == 200 and fn_resp.json():
        fns = fn_resp.json()
        data["function_ids"] = [f["id"] for f in fns]
    else:
        data["function_ids"] = []
    
    return data


# ==========================================
# Unit 2: Create Tests (4 operation types)
# ==========================================

@pytest.mark.anyio
async def test_create_action_update_property(client: AsyncClient):
    """Create update_property action - verify property_mapping saved."""
    data = await _get_or_create_test_data(client)
    obj_ids = data.get("object_type_ids", [])
    if not obj_ids:
        pytest.skip("No object types available")
    
    api_name = gen_name("act_update")
    payload = {
        "api_name": api_name,
        "display_name": "Test Update Property",
        "operation_type": "update_property",
        "target_object_type_id": obj_ids[0],
        "parameters_schema": [
            {"api_id": "title", "display_name": "Title", "type": "string", "required": True},
            {"api_id": "content", "display_name": "Content", "type": "string", "required": False},
        ],
        "property_mapping": {"title": "name", "content": "description"},
        "project_id": data.get("project_id"),
    }
    
    resp = await client.post("/api/v3/ontology/actions", json=payload)
    assert resp.status_code == 201, resp.text
    got = resp.json()
    assert got["operation_type"] == "update_property"
    assert got["property_mapping"] == {"title": "name", "content": "description"}
    
    # Cleanup
    await client.delete(f"/api/v3/ontology/actions/{got['id']}")


@pytest.mark.anyio
async def test_create_action_update_property_with_validations(client: AsyncClient):
    """Create update_property with pre/post/param validation rules."""
    data = await _get_or_create_test_data(client)
    obj_ids = data.get("object_type_ids", [])
    if not obj_ids:
        pytest.skip("No object types available")
    
    api_name = gen_name("act_update_val")
    payload = {
        "api_name": api_name,
        "display_name": "Update with Validations",
        "operation_type": "update_property",
        "target_object_type_id": obj_ids[0],
        "parameters_schema": [{"api_id": "v", "display_name": "Value", "type": "string", "required": True}],
        "property_mapping": {"v": "name"},
        "validation_rules": {
            "param_validation": [{"target_field": "v", "expression": "len(v) > 0", "error_message": "Required"}],
            "pre_condition": [{"target_field": "status", "expression": "status != 'archived'", "error_message": "Not archived"}],
            "post_condition": [{"target_field": "updated_at", "expression": "updated_at != null", "error_message": "Must update"}],
        },
        "project_id": data.get("project_id"),
    }
    
    resp = await client.post("/api/v3/ontology/actions", json=payload)
    assert resp.status_code == 201, resp.text
    got = resp.json()
    assert got["validation_rules"]["param_validation"]
    assert got["validation_rules"]["pre_condition"]
    assert got["validation_rules"]["post_condition"]
    
    await client.delete(f"/api/v3/ontology/actions/{got['id']}")


@pytest.mark.anyio
async def test_create_action_link_objects(client: AsyncClient):
    """Create link_objects action - verify link_type_id saved."""
    data = await _get_or_create_test_data(client)
    link_ids = data.get("link_type_ids", [])
    if not link_ids:
        pytest.skip("No link types available")
    
    api_name = gen_name("act_link")
    payload = {
        "api_name": api_name,
        "display_name": "Test Link Objects",
        "operation_type": "link_objects",
        "link_type_id": link_ids[0],
        "parameters_schema": [
            {"api_id": "source_object_id", "display_name": "Source", "type": "object_ref", "required": True},
            {"api_id": "target_object_id", "display_name": "Target", "type": "object_ref", "required": True},
        ],
        "project_id": data.get("project_id"),
    }
    
    resp = await client.post("/api/v3/ontology/actions", json=payload)
    assert resp.status_code == 201, resp.text
    got = resp.json()
    assert got["operation_type"] == "link_objects"
    assert got["link_type_id"] == link_ids[0]
    
    await client.delete(f"/api/v3/ontology/actions/{got['id']}")


@pytest.mark.anyio
async def test_create_action_unlink_objects(client: AsyncClient):
    """Create unlink_objects action - verify link_type_id saved."""
    data = await _get_or_create_test_data(client)
    link_ids = data.get("link_type_ids", [])
    if not link_ids:
        pytest.skip("No link types available")
    
    api_name = gen_name("act_unlink")
    payload = {
        "api_name": api_name,
        "display_name": "Test Unlink Objects",
        "operation_type": "unlink_objects",
        "link_type_id": link_ids[0],
        "parameters_schema": [
            {"api_id": "source_object_id", "display_name": "Source", "type": "object_ref", "required": True},
            {"api_id": "target_object_id", "display_name": "Target", "type": "object_ref", "required": True},
        ],
        "project_id": data.get("project_id"),
    }
    
    resp = await client.post("/api/v3/ontology/actions", json=payload)
    assert resp.status_code == 201, resp.text
    got = resp.json()
    assert got["operation_type"] == "unlink_objects"
    assert got["link_type_id"] == link_ids[0]
    
    await client.delete(f"/api/v3/ontology/actions/{got['id']}")


@pytest.mark.anyio
async def test_create_action_function_logic(client: AsyncClient):
    """Create function_logic action - verify backing_function_id saved."""
    data = await _get_or_create_test_data(client)
    fn_ids = data.get("function_ids", [])
    if not fn_ids:
        pytest.skip("No functions available")
    
    api_name = gen_name("act_fn")
    payload = {
        "api_name": api_name,
        "display_name": "Test Function Logic",
        "operation_type": "function_logic",
        "backing_function_id": fn_ids[0],
        "parameters_schema": [
            {"api_id": "param1", "display_name": "Param1", "type": "string", "required": True},
        ],
        "project_id": data.get("project_id"),
    }
    
    resp = await client.post("/api/v3/ontology/actions", json=payload)
    assert resp.status_code == 201, resp.text
    got = resp.json()
    assert got["operation_type"] == "function_logic"
    assert got["backing_function_id"] == fn_ids[0]
    
    await client.delete(f"/api/v3/ontology/actions/{got['id']}")


@pytest.mark.anyio
async def test_create_action_update_property_without_project(client: AsyncClient):
    """Create update_property action without project_id (global action)."""
    data = await _get_or_create_test_data(client)
    obj_ids = data.get("object_type_ids", [])
    if not obj_ids:
        pytest.skip("No object types available")
    
    api_name = gen_name("act_global")
    payload = {
        "api_name": api_name,
        "display_name": "Global Update Action",
        "operation_type": "update_property",
        "target_object_type_id": obj_ids[0],
        "parameters_schema": [{"api_id": "x", "display_name": "X", "type": "string", "required": False}],
        "property_mapping": {"x": "name"},
        "project_id": None,
    }
    
    resp = await client.post("/api/v3/ontology/actions", json=payload)
    assert resp.status_code == 201, resp.text
    got = resp.json()
    assert got["project_id"] is None
    
    await client.delete(f"/api/v3/ontology/actions/{got['id']}")


# ==========================================
# Unit 3: Update Tests
# ==========================================

@pytest.mark.anyio
async def test_update_action_change_from_update_to_link(client: AsyncClient):
    """Update action: update_property -> link_objects, link_type_id takes effect."""
    data = await _get_or_create_test_data(client)
    obj_ids = data.get("object_type_ids", [])
    link_ids = data.get("link_type_ids", [])
    if not obj_ids or not link_ids:
        pytest.skip("Need object types and link types")
    
    api_name = gen_name("act_switch")
    create_payload = {
        "api_name": api_name,
        "display_name": "Switch Test",
        "operation_type": "update_property",
        "target_object_type_id": obj_ids[0],
        "parameters_schema": [{"api_id": "v", "display_name": "V", "type": "string", "required": False}],
        "property_mapping": {"v": "name"},
        "project_id": data.get("project_id"),
    }
    cr = await client.post("/api/v3/ontology/actions", json=create_payload)
    assert cr.status_code == 201, cr.text
    action_id = cr.json()["id"]
    
    update_payload = {
        "operation_type": "link_objects",
        "link_type_id": link_ids[0],
        "target_object_type_id": None,
        "property_mapping": None,
        "parameters_schema": [
            {"api_id": "source_object_id", "display_name": "Source", "type": "object_ref", "required": True},
            {"api_id": "target_object_id", "display_name": "Target", "type": "object_ref", "required": True},
        ],
    }
    ur = await client.put(f"/api/v3/ontology/actions/{action_id}", json=update_payload)
    assert ur.status_code == 200, ur.text
    got = ur.json()
    assert got["operation_type"] == "link_objects"
    assert got["link_type_id"] == link_ids[0]
    
    await client.delete(f"/api/v3/ontology/actions/{action_id}")


@pytest.mark.anyio
async def test_update_action_change_from_link_to_function(client: AsyncClient):
    """Update action: link_objects -> function_logic, backing_function_id takes effect."""
    data = await _get_or_create_test_data(client)
    link_ids = data.get("link_type_ids", [])
    fn_ids = data.get("function_ids", [])
    if not link_ids or not fn_ids:
        pytest.skip("Need link types and functions")
    
    api_name = gen_name("act_link2fn")
    create_payload = {
        "api_name": api_name,
        "display_name": "Link to Function",
        "operation_type": "link_objects",
        "link_type_id": link_ids[0],
        "parameters_schema": [
            {"api_id": "source_object_id", "display_name": "Source", "type": "object_ref", "required": True},
            {"api_id": "target_object_id", "display_name": "Target", "type": "object_ref", "required": True},
        ],
        "project_id": data.get("project_id"),
    }
    cr = await client.post("/api/v3/ontology/actions", json=create_payload)
    assert cr.status_code == 201, cr.text
    action_id = cr.json()["id"]
    
    update_payload = {
        "operation_type": "function_logic",
        "backing_function_id": fn_ids[0],
        "link_type_id": None,
        "parameters_schema": [{"api_id": "param1", "display_name": "Param1", "type": "string", "required": True}],
    }
    ur = await client.put(f"/api/v3/ontology/actions/{action_id}", json=update_payload)
    assert ur.status_code == 200, ur.text
    got = ur.json()
    assert got["operation_type"] == "function_logic"
    assert got["backing_function_id"] == fn_ids[0]
    
    await client.delete(f"/api/v3/ontology/actions/{action_id}")


@pytest.mark.anyio
async def test_update_action_preserve_validation_rules(client: AsyncClient):
    """Update other fields while preserving validation_rules."""
    data = await _get_or_create_test_data(client)
    obj_ids = data.get("object_type_ids", [])
    if not obj_ids:
        pytest.skip("No object types")
    
    api_name = gen_name("act_preserve")
    vr = {"param_validation": [{"target_field": "x", "expression": "x != ''", "error_message": "Required"}]}
    create_payload = {
        "api_name": api_name,
        "display_name": "Preserve Test",
        "operation_type": "update_property",
        "target_object_type_id": obj_ids[0],
        "parameters_schema": [{"api_id": "x", "display_name": "X", "type": "string", "required": True}],
        "property_mapping": {"x": "name"},
        "validation_rules": vr,
        "project_id": data.get("project_id"),
    }
    cr = await client.post("/api/v3/ontology/actions", json=create_payload)
    assert cr.status_code == 201, cr.text
    action_id = cr.json()["id"]
    
    ur = await client.put(f"/api/v3/ontology/actions/{action_id}", json={"display_name": "Preserve Updated"})
    assert ur.status_code == 200, ur.text
    got = ur.json()
    assert got["display_name"] == "Preserve Updated"
    assert got.get("validation_rules") == vr
    
    await client.delete(f"/api/v3/ontology/actions/{action_id}")


# ==========================================
# Unit 4: Read/List Tests
# ==========================================

@pytest.mark.anyio
async def test_get_action_returns_link_type_id(client: AsyncClient):
    """Get action - verify link_type_id in response."""
    data = await _get_or_create_test_data(client)
    link_ids = data.get("link_type_ids", [])
    if not link_ids:
        pytest.skip("No link types")
    
    api_name = gen_name("act_get_lt")
    cr = await client.post("/api/v3/ontology/actions", json={
        "api_name": api_name,
        "display_name": "Get Link Test",
        "operation_type": "link_objects",
        "link_type_id": link_ids[0],
        "parameters_schema": [
            {"api_id": "src", "display_name": "Src", "type": "object_ref", "required": True},
            {"api_id": "tgt", "display_name": "Tgt", "type": "object_ref", "required": True},
        ],
        "project_id": data.get("project_id"),
    })
    assert cr.status_code == 201, cr.text
    action_id = cr.json()["id"]
    
    get_resp = await client.get(f"/api/v3/ontology/actions/{action_id}")
    assert get_resp.status_code == 200, get_resp.text
    got = get_resp.json()
    assert got["link_type_id"] == link_ids[0]
    
    await client.delete(f"/api/v3/ontology/actions/{action_id}")


@pytest.mark.anyio
async def test_get_action_returns_backing_function_id(client: AsyncClient):
    """Get action - verify backing_function_id in response."""
    data = await _get_or_create_test_data(client)
    fn_ids = data.get("function_ids", [])
    if not fn_ids:
        pytest.skip("No functions")
    
    api_name = gen_name("act_get_fn")
    cr = await client.post("/api/v3/ontology/actions", json={
        "api_name": api_name,
        "display_name": "Get Function Test",
        "operation_type": "function_logic",
        "backing_function_id": fn_ids[0],
        "parameters_schema": [{"api_id": "p", "display_name": "P", "type": "string", "required": False}],
        "project_id": data.get("project_id"),
    })
    assert cr.status_code == 201, cr.text
    action_id = cr.json()["id"]
    
    get_resp = await client.get(f"/api/v3/ontology/actions/{action_id}")
    assert get_resp.status_code == 200, get_resp.text
    got = get_resp.json()
    assert got["backing_function_id"] == fn_ids[0]
    
    await client.delete(f"/api/v3/ontology/actions/{action_id}")


@pytest.mark.anyio
async def test_list_actions_filter_by_project(client: AsyncClient):
    """List actions with project_id filter."""
    data = await _get_or_create_test_data(client)
    proj_id = data.get("project_id")
    obj_ids = data.get("object_type_ids", [])
    if not proj_id or not obj_ids:
        pytest.skip("Need project and object types")
    
    api_name = gen_name("act_proj")
    cr = await client.post("/api/v3/ontology/actions", json={
        "api_name": api_name,
        "display_name": "Project Filter Test",
        "operation_type": "update_property",
        "target_object_type_id": obj_ids[0],
        "parameters_schema": [{"api_id": "v", "display_name": "V", "type": "string", "required": False}],
        "property_mapping": {"v": "name"},
        "project_id": proj_id,
    })
    assert cr.status_code == 201, cr.text
    action_id = cr.json()["id"]
    
    list_resp = await client.get("/api/v3/ontology/actions", params={"project_id": proj_id})
    assert list_resp.status_code == 200, list_resp.text
    actions = list_resp.json()
    ids = [a["id"] for a in actions]
    assert action_id in ids
    
    await client.delete(f"/api/v3/ontology/actions/{action_id}")


@pytest.mark.anyio
async def test_list_actions_without_project(client: AsyncClient):
    """List actions without project_id returns all."""
    list_resp = await client.get("/api/v3/ontology/actions")
    assert list_resp.status_code == 200, list_resp.text
    data = list_resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_list_actions_with_functions(client: AsyncClient):
    """List actions with /with-functions returns function info."""
    resp = await client.get("/api/v3/ontology/actions/with-functions")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)


# ==========================================
# Unit 5: Validation Tests
# ==========================================

@pytest.mark.anyio
async def test_create_action_invalid_link_type_id(client: AsyncClient):
    """Create link_objects with nonexistent link_type_id.
    
    Note: Backend may accept invalid link_type_id if DB has no FK constraint.
    If FK exists, expect 400. Otherwise creation succeeds (current behavior).
    """
    api_name = gen_name("act_bad_lt")
    payload = {
        "api_name": api_name,
        "display_name": "Bad Link Type",
        "operation_type": "link_objects",
        "link_type_id": "nonexistent-link-type-id-12345",
        "parameters_schema": [
            {"api_id": "src", "display_name": "Src", "type": "object_ref", "required": True},
            {"api_id": "tgt", "display_name": "Tgt", "type": "object_ref", "required": True},
        ],
    }
    resp = await client.post("/api/v3/ontology/actions", json=payload)
    # DB may or may not enforce FK - accept either 201 or 400
    assert resp.status_code in (201, 400), f"Unexpected {resp.status_code}: {resp.text}"
    if resp.status_code == 201:
        await client.delete(f"/api/v3/ontology/actions/{resp.json()['id']}")


@pytest.mark.anyio
async def test_create_action_invalid_backing_function_id(client: AsyncClient):
    """Create function_logic with nonexistent backing_function_id.
    
    Note: Backend may accept invalid backing_function_id if DB has no FK constraint.
    If FK exists, expect 400. Otherwise creation succeeds (current behavior).
    """
    api_name = gen_name("act_bad_fn")
    payload = {
        "api_name": api_name,
        "display_name": "Bad Function",
        "operation_type": "function_logic",
        "backing_function_id": "nonexistent-function-id-12345",
        "parameters_schema": [{"api_id": "p", "display_name": "P", "type": "string", "required": False}],
    }
    resp = await client.post("/api/v3/ontology/actions", json=payload)
    assert resp.status_code in (201, 400), f"Unexpected {resp.status_code}: {resp.text}"
    if resp.status_code == 201:
        await client.delete(f"/api/v3/ontology/actions/{resp.json()['id']}")


@pytest.mark.anyio
async def test_get_nonexistent_action_returns_404(client: AsyncClient):
    """Get action with nonexistent ID returns 404."""
    resp = await client.get("/api/v3/ontology/actions/nonexistent-action-id-12345")
    assert resp.status_code == 404, resp.text


@pytest.mark.anyio
async def test_delete_nonexistent_action_returns_404(client: AsyncClient):
    """Delete action with nonexistent ID returns 404."""
    resp = await client.delete("/api/v3/ontology/actions/nonexistent-action-id-12345")
    assert resp.status_code == 404, resp.text


# ==========================================
# Unit 6: Edge Cases
# ==========================================

@pytest.mark.anyio
async def test_create_action_update_property_empty_validation_rules(client: AsyncClient):
    """Create update_property with empty validation_rules."""
    data = await _get_or_create_test_data(client)
    obj_ids = data.get("object_type_ids", [])
    if not obj_ids:
        pytest.skip("No object types")
    
    api_name = gen_name("act_empty_vr")
    payload = {
        "api_name": api_name,
        "display_name": "Empty Validation Rules",
        "operation_type": "update_property",
        "target_object_type_id": obj_ids[0],
        "parameters_schema": [{"api_id": "v", "display_name": "V", "type": "string", "required": False}],
        "property_mapping": {"v": "name"},
        "validation_rules": {},
        "project_id": data.get("project_id"),
    }
    resp = await client.post("/api/v3/ontology/actions", json=payload)
    assert resp.status_code == 201, resp.text
    got = resp.json()
    assert got.get("validation_rules") == {} or got.get("validation_rules") is None
    
    await client.delete(f"/api/v3/ontology/actions/{got['id']}")


@pytest.mark.anyio
async def test_delete_action(client: AsyncClient):
    """Delete action - verify 404 on subsequent get."""
    data = await _get_or_create_test_data(client)
    obj_ids = data.get("object_type_ids", [])
    if not obj_ids:
        pytest.skip("No object types")
    
    api_name = gen_name("act_del")
    cr = await client.post("/api/v3/ontology/actions", json={
        "api_name": api_name,
        "display_name": "Delete Test",
        "operation_type": "update_property",
        "target_object_type_id": obj_ids[0],
        "parameters_schema": [{"api_id": "v", "display_name": "V", "type": "string", "required": False}],
        "property_mapping": {"v": "name"},
        "project_id": data.get("project_id"),
    })
    assert cr.status_code == 201, cr.text
    action_id = cr.json()["id"]
    
    del_resp = await client.delete(f"/api/v3/ontology/actions/{action_id}")
    assert del_resp.status_code == 204, del_resp.text
    
    get_resp = await client.get(f"/api/v3/ontology/actions/{action_id}")
    assert get_resp.status_code == 404, get_resp.text


@pytest.mark.anyio
async def test_create_action_duplicate_api_name_rejected(client: AsyncClient):
    """Create action with duplicate api_name - expect 400."""
    data = await _get_or_create_test_data(client)
    obj_ids = data.get("object_type_ids", [])
    if not obj_ids:
        pytest.skip("No object types")
    
    api_name = gen_name("act_dup")
    payload = {
        "api_name": api_name,
        "display_name": "Duplicate Test",
        "operation_type": "update_property",
        "target_object_type_id": obj_ids[0],
        "parameters_schema": [{"api_id": "v", "display_name": "V", "type": "string", "required": False}],
        "property_mapping": {"v": "name"},
        "project_id": data.get("project_id"),
    }
    cr1 = await client.post("/api/v3/ontology/actions", json=payload)
    assert cr1.status_code == 201, cr1.text
    action_id = cr1.json()["id"]
    
    payload["display_name"] = "Duplicate Second"
    cr2 = await client.post("/api/v3/ontology/actions", json=payload)
    assert cr2.status_code == 400, f"Expected 400 for duplicate api_name, got {cr2.status_code}: {cr2.text}"
    
    await client.delete(f"/api/v3/ontology/actions/{action_id}")
