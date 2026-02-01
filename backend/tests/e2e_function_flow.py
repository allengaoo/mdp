"""
Unit 3: E2E Function Full Flow Tests.
Complete flows: Create -> List -> Edit -> Delete.
Action-Function relationship verification.
"""
import pytest
import uuid
from httpx import AsyncClient


def _gen_name(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


async def _get_project_id(client: AsyncClient) -> str | None:
    r = await client.get("/api/v3/projects")
    if r.status_code == 200 and r.json():
        return r.json()[0]["id"]
    return None


@pytest.mark.asyncio
async def test_full_flow_studio_create_list_edit_delete(client: AsyncClient):
    """E2E-10: Studio flow - create -> list (filter) -> edit -> delete."""
    proj_id = await _get_project_id(client)
    if not proj_id:
        pytest.skip("No project available")
    api_name = _gen_name("flow_studio")
    # Create
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={
            "api_name": api_name,
            "display_name": f"Flow Studio {api_name}",
            "project_id": proj_id,
        },
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    # List filtered by project
    lst = await client.get("/api/v3/ontology/functions", params={"project_id": proj_id})
    assert lst.status_code == 200
    ids = [f["id"] for f in lst.json()]
    assert fid in ids
    # Edit
    upd = await client.put(
        f"/api/v3/ontology/functions/{fid}",
        json={"display_name": "Flow Studio Updated"},
    )
    assert upd.status_code == 200
    assert upd.json()["display_name"] == "Flow Studio Updated"
    # Delete
    dlt = await client.delete(f"/api/v3/ontology/functions/{fid}")
    assert dlt.status_code == 204
    # Get 404
    get_r = await client.get(f"/api/v3/ontology/functions/{fid}")
    assert get_r.status_code == 404


@pytest.mark.asyncio
async def test_oma_create_then_for_list_visible(client: AsyncClient):
    """E2E-11: OMA - create global function, visible in for-list."""
    api_name = _gen_name("flow_oma")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={"api_name": api_name, "display_name": f"Flow OMA {api_name}"},
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    r = await client.get("/api/v3/ontology/functions/for-list")
    assert r.status_code == 200
    ids = [f["id"] for f in r.json()]
    assert fid in ids
    await client.delete(f"/api/v3/ontology/functions/{fid}")


@pytest.mark.asyncio
async def test_action_uses_function(client: AsyncClient):
    """E2E-12: Action with backing_function_id - get action details."""
    api_name = _gen_name("flow_func")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={
            "api_name": api_name,
            "display_name": f"Flow Func {api_name}",
            "code_content": "def main(params): return params",
            "input_params_schema": [{"name": "x", "type": "string", "required": True}],
            "output_type": "STRING",
        },
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    proj_id = await _get_project_id(client)
    # Create action with backing_function_id
    act_name = _gen_name("flow_act")
    act_cr = await client.post(
        "/api/v3/ontology/actions",
        json={
            "api_name": act_name,
            "display_name": f"Flow Action {act_name}",
            "operation_type": "function_logic",
            "target_object_type_id": None,
            "link_type_id": None,
            "backing_function_id": fid,
            "parameters_schema": [{"api_id": "x", "display_name": "X", "type": "string", "required": True}],
            "property_mapping": None,
            "validation_rules": None,
            "project_id": proj_id,
        },
    )
    assert act_cr.status_code == 201
    aid = act_cr.json()["id"]
    # Get action details (includes function info)
    det = await client.get(f"/api/v3/ontology/actions/{aid}/details")
    assert det.status_code == 200
    d = det.json()
    assert d["backing_function_id"] == fid
    assert d.get("function_api_name") == api_name
    # Cleanup
    await client.delete(f"/api/v3/ontology/actions/{aid}")
    await client.delete(f"/api/v3/ontology/functions/{fid}")
