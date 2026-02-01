"""
Unit 2: E2E Function Wizard/Editor Contract Tests.
Simulates exact payload structure from FunctionWizard and FunctionEditor.
Verifies frontend-backend contract for function CRUD.
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
async def test_function_wizard_create_payload(client: AsyncClient):
    """E2E-01: FunctionWizard handleFinish payload format - Studio with project_id."""
    proj_id = await _get_project_id(client)
    api_name = _gen_name("wiz_studio")
    # Payload as FunctionWizard sends (handleFinish)
    payload = {
        "api_name": api_name,
        "display_name": f"Wizard Studio {api_name}",
        "description": "E2E wizard test",
        "code_content": "def main(): return 'ok'",
        "input_params_schema": [
            {"name": "x", "type": "string", "required": True},
            {"name": "y", "type": "number", "required": False},
        ],
        "output_type": "STRING",
        "bound_object_type_id": None,
        "project_id": proj_id or None,
    }
    r = await client.post("/api/v3/ontology/functions", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["api_name"] == api_name
    if proj_id:
        assert data.get("project_id") == proj_id
    await client.delete(f"/api/v3/ontology/functions/{data['id']}")


@pytest.mark.asyncio
async def test_function_wizard_create_oma_global(client: AsyncClient):
    """E2E-04: FunctionWizard from OMA (no project_id) - global function."""
    api_name = _gen_name("wiz_oma")
    payload = {
        "api_name": api_name,
        "display_name": f"Wizard OMA {api_name}",
        "description": None,
        "code_content": None,
        "input_params_schema": None,
        "output_type": "VOID",
        "bound_object_type_id": None,
        "project_id": None,
    }
    r = await client.post("/api/v3/ontology/functions", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data.get("project_id") is None
    await client.delete(f"/api/v3/ontology/functions/{data['id']}")


@pytest.mark.asyncio
async def test_function_editor_update_payload(client: AsyncClient):
    """E2E-02: FunctionEditor handleSave payload format."""
    api_name = _gen_name("edit_func")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={"api_name": api_name, "display_name": f"Edit Test {api_name}"},
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    # Payload as FunctionEditor sends (handleSave) - no api_name (cannot change)
    payload = {
        "display_name": "Updated by Editor",
        "description": "E2E editor test",
        "code_content": "def main(): return 42",
        "input_params_schema": [{"name": "a", "type": "string", "required": False}],
        "output_type": "INTEGER",
        "bound_object_type_id": None,
    }
    r = await client.put(f"/api/v3/ontology/functions/{fid}", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["display_name"] == "Updated by Editor"
    assert data["output_type"] == "INTEGER"
    await client.delete(f"/api/v3/ontology/functions/{fid}")


@pytest.mark.asyncio
async def test_function_wizard_minimal_payload(client: AsyncClient):
    """E2E-03: FunctionWizard minimal payload (required fields only)."""
    api_name = _gen_name("wiz_min")
    payload = {
        "api_name": api_name,
        "display_name": f"Minimal {api_name}",
        "description": None,
        "code_content": None,
        "input_params_schema": None,
        "output_type": "VOID",
        "bound_object_type_id": None,
        "project_id": None,
    }
    r = await client.post("/api/v3/ontology/functions", json=payload)
    assert r.status_code == 201
    await client.delete(f"/api/v3/ontology/functions/{r.json()['id']}")
