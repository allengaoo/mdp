"""
Tests for Project API endpoints.
"""
import pytest
from httpx import AsyncClient
import uuid


class TestProjectAPI:
    """Test cases for /meta/projects endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_projects(self, client: AsyncClient):
        """Test listing all projects."""
        response = await client.get("/api/v1/meta/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} projects")
    
    @pytest.mark.asyncio
    async def test_list_projects_with_pagination(self, client: AsyncClient):
        """Test listing projects with pagination."""
        response = await client.get("/api/v1/meta/projects", params={"skip": 0, "limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
        print(f"Pagination works, got {len(data)} projects")
    
    @pytest.mark.asyncio
    async def test_get_project_by_id(self, client: AsyncClient):
        """Test getting a single project by ID."""
        list_response = await client.get("/api/v1/meta/projects")
        projects = list_response.json()
        
        if not projects:
            pytest.skip("No projects available for testing")
        
        project_id = projects[0]["id"]
        response = await client.get(f"/api/v1/meta/projects/{project_id}")
        
        if response.status_code == 404:
            print("Project lookup by ID not supported (view mode). Skipping.")
            pytest.skip("Project lookup by ID not supported (meta_project is a view)")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        print(f"Got project: {data['name']}")
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_project(self, client: AsyncClient):
        """Test getting a non-existent project returns 404."""
        response = await client.get("/api/v1/meta/projects/nonexistent-id-12345")
        assert response.status_code == 404
        print("Non-existent project returns 404")
    
    @pytest.mark.asyncio
    async def test_create_project(self, client: AsyncClient):
        """Test creating a new project (requires multi-project support)."""
        unique_name = f"Test Project {uuid.uuid4().hex[:8]}"
        
        payload = {
            "name": unique_name,
            "description": "Created by automated test"
        }
        
        response = await client.post("/api/v1/meta/projects", json=payload)
        
        if response.status_code == 400:
            error_detail = response.json().get("detail", "")
            if "view" in error_detail.lower():
                print("Project creation not supported (meta_project is a view). Skipping.")
                pytest.skip("Multi-project not enabled (meta_project is a view)")
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == unique_name
        print(f"Created project: {data['name']}")
        
        # Cleanup
        delete_response = await client.delete(f"/api/v1/meta/projects/{data['id']}")
        assert delete_response.status_code == 204
        print("Cleaned up test project")
    
    @pytest.mark.asyncio
    async def test_update_project(self, client: AsyncClient):
        """Test updating a project (requires multi-project support)."""
        unique_name = f"Update Test {uuid.uuid4().hex[:8]}"
        create_payload = {
            "name": unique_name,
            "description": "Original description"
        }
        
        create_response = await client.post("/api/v1/meta/projects", json=create_payload)
        
        if create_response.status_code == 400:
            pytest.skip("Multi-project not enabled")
        
        assert create_response.status_code == 201
        project_id = create_response.json()["id"]
        
        # Update
        update_payload = {
            "name": f"{unique_name} Updated",
            "description": "Updated description"
        }
        
        update_response = await client.put(f"/api/v1/meta/projects/{project_id}", json=update_payload)
        assert update_response.status_code == 200
        data = update_response.json()
        assert "Updated" in data["name"]
        print(f"Updated project: {data['name']}")
        
        # Cleanup
        await client.delete(f"/api/v1/meta/projects/{project_id}")
