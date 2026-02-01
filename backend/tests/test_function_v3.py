"""
Unit 1: V3 Function Definition API Tests.
Comprehensive tests for /api/v3/ontology/functions endpoints.
"""
import pytest
import uuid
from httpx import AsyncClient


def _gen_name(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


async def _get_project_id(client: AsyncClient) -> str | None:
    """Get first available project ID for project-scoped tests."""
    r = await client.get("/api/v3/projects")
    if r.status_code == 200 and r.json():
        return r.json()[0]["id"]
    return None


# -----------------------------------------------------------------------------
# A. Create
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_global_function(client: AsyncClient):
    """B-C-01: Create function without project_id (global)."""
    api_name = _gen_name("global_func")
    payload = {
        "api_name": api_name,
        "display_name": f"Global Function {api_name}",
    }
    r = await client.post("/api/v3/ontology/functions", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["api_name"] == api_name
    assert data.get("project_id") is None
    # Cleanup
    await client.delete(f"/api/v3/ontology/functions/{data['id']}")


@pytest.mark.asyncio
async def test_create_project_scoped_function(client: AsyncClient):
    """B-C-02: Create function with project_id."""
    proj_id = await _get_project_id(client)
    if not proj_id:
        pytest.skip("No project available")
    api_name = _gen_name("proj_func")
    payload = {
        "api_name": api_name,
        "display_name": f"Project Function {api_name}",
        "project_id": proj_id,
    }
    r = await client.post("/api/v3/ontology/functions", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["project_id"] == proj_id
    await client.delete(f"/api/v3/ontology/functions/{data['id']}")


@pytest.mark.asyncio
async def test_create_with_full_params(client: AsyncClient):
    """B-C-03: Create with description, input_params_schema, bound_object_type_id."""
    api_name = _gen_name("full_func")
    payload = {
        "api_name": api_name,
        "display_name": f"Full Function {api_name}",
        "description": "Test description",
        "code_content": "def main(): return 42",
        "input_params_schema": [
            {"name": "x", "type": "string", "required": True},
            {"name": "y", "type": "number", "required": False},
        ],
        "output_type": "INTEGER",
    }
    r = await client.post("/api/v3/ontology/functions", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["description"] == "Test description"
    assert len(data.get("input_params_schema", [])) == 2
    assert data["output_type"] == "INTEGER"
    await client.delete(f"/api/v3/ontology/functions/{data['id']}")


@pytest.mark.asyncio
async def test_create_minimal_params(client: AsyncClient):
    """B-C-04: Create with only api_name and display_name."""
    api_name = _gen_name("min_func")
    payload = {"api_name": api_name, "display_name": f"Minimal {api_name}"}
    r = await client.post("/api/v3/ontology/functions", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data.get("code_content") is None or data.get("code_content") == ""
    assert data.get("output_type") == "VOID"
    await client.delete(f"/api/v3/ontology/functions/{data['id']}")


@pytest.mark.asyncio
async def test_create_missing_api_name(client: AsyncClient):
    """B-C-06: Create without api_name returns 422."""
    payload = {"display_name": "No API Name"}
    r = await client.post("/api/v3/ontology/functions", json=payload)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_missing_display_name(client: AsyncClient):
    """B-C-07: Create without display_name returns 422."""
    payload = {"api_name": _gen_name("noname")}
    r = await client.post("/api/v3/ontology/functions", json=payload)
    assert r.status_code == 422


# -----------------------------------------------------------------------------
# B. Read
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_function_by_id(client: AsyncClient):
    """B-R-01: Get function by valid ID."""
    api_name = _gen_name("get_func")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={"api_name": api_name, "display_name": f"Get Test {api_name}"},
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    r = await client.get(f"/api/v3/ontology/functions/{fid}")
    assert r.status_code == 200
    assert r.json()["id"] == fid
    await client.delete(f"/api/v3/ontology/functions/{fid}")


@pytest.mark.asyncio
async def test_get_function_not_found(client: AsyncClient):
    """B-R-02: Get non-existent function returns 404."""
    r = await client.get("/api/v3/ontology/functions/nonexistent-id-12345")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_function_response_fields(client: AsyncClient):
    """B-R-03: Response contains required fields."""
    api_name = _gen_name("fields_func")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={"api_name": api_name, "display_name": f"Fields {api_name}"},
    )
    assert cr.status_code == 201
    data = cr.json()
    required = ["id", "api_name", "display_name", "output_type"]
    for f in required:
        assert f in data
    await client.delete(f"/api/v3/ontology/functions/{data['id']}")


# -----------------------------------------------------------------------------
# C. List
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_all_functions(client: AsyncClient):
    """B-L-01: List functions without filter returns all."""
    r = await client.get("/api/v3/ontology/functions")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_filter_by_project(client: AsyncClient):
    """B-L-02: List with project_id filter."""
    proj_id = await _get_project_id(client)
    if not proj_id:
        pytest.skip("No project available")
    api_name = _gen_name("list_proj")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={"api_name": api_name, "display_name": f"List Proj {api_name}", "project_id": proj_id},
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    r = await client.get("/api/v3/ontology/functions", params={"project_id": proj_id})
    assert r.status_code == 200
    ids = [f["id"] for f in r.json()]
    assert fid in ids
    await client.delete(f"/api/v3/ontology/functions/{fid}")


@pytest.mark.asyncio
async def test_list_filter_nonexistent_project(client: AsyncClient):
    """B-L-03: List with nonexistent project_id returns empty list."""
    r = await client.get("/api/v3/ontology/functions", params={"project_id": "proj-nonexistent"})
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_list_pagination(client: AsyncClient):
    """B-L-04: List with skip and limit."""
    r = await client.get("/api/v3/ontology/functions", params={"skip": 0, "limit": 5})
    assert r.status_code == 200
    data = r.json()
    assert len(data) <= 5


@pytest.mark.asyncio
async def test_for_list_endpoint(client: AsyncClient):
    """B-L-05: GET /functions/for-list returns list."""
    r = await client.get("/api/v3/ontology/functions/for-list")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


# -----------------------------------------------------------------------------
# D. Update
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_display_name(client: AsyncClient):
    """B-U-01: Update display_name."""
    api_name = _gen_name("upd_func")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={"api_name": api_name, "display_name": "Original"},
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    r = await client.put(f"/api/v3/ontology/functions/{fid}", json={"display_name": "Updated Name"})
    assert r.status_code == 200
    assert r.json()["display_name"] == "Updated Name"
    await client.delete(f"/api/v3/ontology/functions/{fid}")


@pytest.mark.asyncio
async def test_update_code_content(client: AsyncClient):
    """B-U-02: Update code_content."""
    api_name = _gen_name("upd_code")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={"api_name": api_name, "display_name": f"Code {api_name}"},
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    r = await client.put(
        f"/api/v3/ontology/functions/{fid}",
        json={"code_content": "def main(): return 'updated'"},
    )
    assert r.status_code == 200
    assert "updated" in (r.json().get("code_content") or "")
    await client.delete(f"/api/v3/ontology/functions/{fid}")


@pytest.mark.asyncio
async def test_update_project_id(client: AsyncClient):
    """B-U-04: Update project_id."""
    proj_id = await _get_project_id(client)
    if not proj_id:
        pytest.skip("No project available")
    api_name = _gen_name("upd_proj")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={"api_name": api_name, "display_name": f"Proj {api_name}"},
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    r = await client.put(f"/api/v3/ontology/functions/{fid}", json={"project_id": proj_id})
    assert r.status_code == 200
    assert r.json()["project_id"] == proj_id
    await client.delete(f"/api/v3/ontology/functions/{fid}")


@pytest.mark.asyncio
async def test_update_not_found(client: AsyncClient):
    """B-U-06: Update non-existent function returns 404."""
    r = await client.put(
        "/api/v3/ontology/functions/nonexistent-id",
        json={"display_name": "Should Fail"},
    )
    assert r.status_code == 404


# -----------------------------------------------------------------------------
# E. Delete
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_function(client: AsyncClient):
    """B-D-01: Delete function returns 204."""
    api_name = _gen_name("del_func")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={"api_name": api_name, "display_name": f"Del {api_name}"},
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    r = await client.delete(f"/api/v3/ontology/functions/{fid}")
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_delete_then_get_404(client: AsyncClient):
    """B-D-02: Get after delete returns 404."""
    api_name = _gen_name("del_get")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={"api_name": api_name, "display_name": f"DelGet {api_name}"},
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    await client.delete(f"/api/v3/ontology/functions/{fid}")
    r = await client.get(f"/api/v3/ontology/functions/{fid}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_not_found(client: AsyncClient):
    """B-D-03: Delete non-existent returns 404."""
    r = await client.delete("/api/v3/ontology/functions/nonexistent-id")
    assert r.status_code == 404


# -----------------------------------------------------------------------------
# F. Project Scope
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_studio_shows_project_functions(client: AsyncClient):
    """B-S-01: Project filter includes project-scoped functions."""
    proj_id = await _get_project_id(client)
    if not proj_id:
        pytest.skip("No project available")
    api_name = _gen_name("scope_proj")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={"api_name": api_name, "display_name": f"Scope {api_name}", "project_id": proj_id},
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    r = await client.get("/api/v3/ontology/functions", params={"project_id": proj_id})
    ids = [f["id"] for f in r.json()]
    assert fid in ids
    await client.delete(f"/api/v3/ontology/functions/{fid}")


@pytest.mark.asyncio
async def test_oma_shows_global_functions(client: AsyncClient):
    """B-S-02: List without project_id includes global functions."""
    api_name = _gen_name("scope_global")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={"api_name": api_name, "display_name": f"Global {api_name}"},
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    r = await client.get("/api/v3/ontology/functions")
    ids = [f["id"] for f in r.json()]
    assert fid in ids
    await client.delete(f"/api/v3/ontology/functions/{fid}")


@pytest.mark.asyncio
async def test_studio_excludes_other_project(client: AsyncClient):
    """B-S-03: Project filter excludes functions from other projects."""
    proj_id = await _get_project_id(client)
    if not proj_id:
        pytest.skip("No project available")
    api_name = _gen_name("scope_other")
    cr = await client.post(
        "/api/v3/ontology/functions",
        json={"api_name": api_name, "display_name": f"Other {api_name}", "project_id": proj_id},
    )
    assert cr.status_code == 201
    fid = cr.json()["id"]
    # Filter by a different project (use a known non-matching ID)
    other_proj = "proj-other-00000000-0000-0000-0000-000000000000"
    r = await client.get("/api/v3/ontology/functions", params={"project_id": other_proj})
    ids = [f["id"] for f in r.json()]
    assert fid not in ids
    await client.delete(f"/api/v3/ontology/functions/{fid}")
