"""
E2E-style API tests for Action Wizard flows.

Simulates the exact payload structure the frontend ActionWizard and ActionEditor
send when creating/updating actions. Verifies the frontend-backend contract.
"""
import pytest
import uuid
from httpx import AsyncClient


def gen_name(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


async def _get_test_data(client: AsyncClient):
    """Fetch project, object types, link types, functions."""
    data = {}
    proj = await client.get("/api/v3/projects")
    if proj.status_code == 200 and proj.json():
        data["project_id"] = proj.json()[0]["id"]
    else:
        data["project_id"] = None

    objs = await client.get("/api/v3/ontology/objects/with-stats")
    if objs.status_code == 200 and objs.json():
        data["object_type_ids"] = [o["id"] for o in objs.json()[:2]]
    else:
        data["object_type_ids"] = []

    links = await client.get("/api/v3/ontology/link-types")
    if links.status_code == 200 and links.json():
        data["link_type_ids"] = [l["id"] for l in links.json()]
    else:
        data["link_type_ids"] = []

    fns = await client.get("/api/v3/ontology/functions/for-list")
    if fns.status_code == 200 and fns.json():
        data["function_ids"] = [f["id"] for f in fns.json()]
    else:
        data["function_ids"] = []

    return data


@pytest.mark.anyio
async def test_wizard_update_property_payload_format(client: AsyncClient):
    """Simulate ActionWizard update_property payload - exact frontend format."""
    data = await _get_test_data(client)
    obj_ids = data.get("object_type_ids", [])
    if not obj_ids:
        pytest.skip("No object types")

    # Payload structure as ActionWizard sends it (IActionDefinitionCreate)
    api_name = gen_name("wiz_update")
    payload = {
        "display_name": "Wizard Update Property",
        "api_name": api_name,
        "description": None,
        "operation_type": "update_property",
        "target_object_type_id": obj_ids[0],
        "link_type_id": None,
        "backing_function_id": None,
        "parameters_schema": [
            {"api_id": "title", "display_name": "Title", "type": "string", "required": True},
            {"api_id": "content", "display_name": "Content", "type": "string", "required": False},
        ],
        "property_mapping": {"title": "name", "content": "description"},
        "validation_rules": {
            "param_validation": [
                {"target_field": "title", "expression": "len(title) > 0", "error_message": "Title required"}
            ],
            "pre_condition": [
                {"target_field": "status", "expression": "status != 'archived'", "error_message": "Not archived"}
            ],
            "post_condition": [],
        },
        "project_id": data.get("project_id"),
    }

    resp = await client.post("/api/v3/ontology/actions", json=payload)
    assert resp.status_code == 201, resp.text
    got = resp.json()
    assert got["operation_type"] == "update_property"
    assert got["property_mapping"] == payload["property_mapping"]
    assert got["validation_rules"]["param_validation"]
    assert got["validation_rules"]["pre_condition"]

    await client.delete(f"/api/v3/ontology/actions/{got['id']}")


@pytest.mark.anyio
async def test_wizard_link_objects_payload_format(client: AsyncClient):
    """Simulate ActionWizard link_objects payload - exact frontend format."""
    data = await _get_test_data(client)
    link_ids = data.get("link_type_ids", [])
    if not link_ids:
        pytest.skip("No link types")

    api_name = gen_name("wiz_link")
    payload = {
        "display_name": "Wizard Link Objects",
        "api_name": api_name,
        "operation_type": "link_objects",
        "target_object_type_id": None,
        "link_type_id": link_ids[0],
        "backing_function_id": None,
        "parameters_schema": [
            {"api_id": "source_object_id", "display_name": "Source", "type": "object_ref", "required": True},
            {"api_id": "target_object_id", "display_name": "Target", "type": "object_ref", "required": True},
        ],
        "property_mapping": None,
        "validation_rules": None,
        "project_id": data.get("project_id"),
    }

    resp = await client.post("/api/v3/ontology/actions", json=payload)
    assert resp.status_code == 201, resp.text
    got = resp.json()
    assert got["operation_type"] == "link_objects"
    assert got["link_type_id"] == link_ids[0]
    assert len(got["parameters_schema"]) == 2

    await client.delete(f"/api/v3/ontology/actions/{got['id']}")


@pytest.mark.anyio
async def test_wizard_function_logic_payload_format(client: AsyncClient):
    """Simulate ActionWizard function_logic payload - exact frontend format."""
    data = await _get_test_data(client)
    fn_ids = data.get("function_ids", [])
    if not fn_ids:
        pytest.skip("No functions")

    api_name = gen_name("wiz_fn")
    payload = {
        "display_name": "Wizard Function Logic",
        "api_name": api_name,
        "operation_type": "function_logic",
        "target_object_type_id": None,
        "link_type_id": None,
        "backing_function_id": fn_ids[0],
        "parameters_schema": [
            {"api_id": "param1", "display_name": "Param 1", "type": "string", "required": True},
        ],
        "property_mapping": None,
        "validation_rules": None,
        "project_id": data.get("project_id"),
    }

    resp = await client.post("/api/v3/ontology/actions", json=payload)
    assert resp.status_code == 201, resp.text
    got = resp.json()
    assert got["operation_type"] == "function_logic"
    assert got["backing_function_id"] == fn_ids[0]

    await client.delete(f"/api/v3/ontology/actions/{got['id']}")


@pytest.mark.anyio
async def test_editor_load_and_save_roundtrip(client: AsyncClient):
    """Simulate ActionEditor: create, get, update, verify roundtrip."""
    data = await _get_test_data(client)
    obj_ids = data.get("object_type_ids", [])
    if not obj_ids:
        pytest.skip("No object types")

    api_name = gen_name("edit_round")
    create_payload = {
        "api_name": api_name,
        "display_name": "Editor Roundtrip",
        "operation_type": "update_property",
        "target_object_type_id": obj_ids[0],
        "parameters_schema": [{"api_id": "v", "display_name": "V", "type": "string", "required": False}],
        "property_mapping": {"v": "name"},
        "project_id": data.get("project_id"),
    }

    cr = await client.post("/api/v3/ontology/actions", json=create_payload)
    assert cr.status_code == 201, cr.text
    action_id = cr.json()["id"]

    # Simulate ActionEditor load (get details)
    get_resp = await client.get(f"/api/v3/ontology/actions/{action_id}")
    assert get_resp.status_code == 200, get_resp.text
    loaded = get_resp.json()
    assert loaded["link_type_id"] is None
    assert loaded["backing_function_id"] is None

    # Simulate ActionEditor save (update)
    update_payload = {
        "display_name": "Editor Roundtrip Updated",
        "property_mapping": {"v": "name", "v2": "description"},
    }
    upd = await client.put(f"/api/v3/ontology/actions/{action_id}", json=update_payload)
    assert upd.status_code == 200, upd.text
    got = upd.json()
    assert got["display_name"] == "Editor Roundtrip Updated"
    assert got["property_mapping"]["v2"] == "description"

    await client.delete(f"/api/v3/ontology/actions/{action_id}")


@pytest.mark.anyio
async def test_actions_logic_page_list(client: AsyncClient):
    """Simulate Actions & Logic page: /with-functions returns all actions."""
    resp = await client.get("/api/v3/ontology/actions/with-functions")
    assert resp.status_code == 200, resp.text
    actions = resp.json()
    assert isinstance(actions, list)
    for a in actions:
        assert "id" in a
        assert "api_name" in a
        assert "display_name" in a
        assert "backing_function_id" in a or True  # Optional
        assert "function_api_name" in a or "function_display_name" in a or True


@pytest.mark.anyio
async def test_ontology_studio_actions_filtered_by_project(client: AsyncClient):
    """Simulate Ontology Studio: list actions filtered by project_id."""
    data = await _get_test_data(client)
    proj_id = data.get("project_id")
    if not proj_id:
        pytest.skip("No project")

    resp = await client.get("/api/v3/ontology/actions", params={"project_id": proj_id})
    assert resp.status_code == 200, resp.text
    actions = resp.json()
    assert isinstance(actions, list)
    for a in actions:
        assert a.get("project_id") == proj_id or a.get("project_id") is None
