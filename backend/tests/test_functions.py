"""
Tests for FunctionDefinition API endpoints.
"""
import pytest
from httpx import AsyncClient
import uuid


class TestFunctionDefinitionAPI:
    """Test cases for /meta/functions endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_functions(self, client: AsyncClient):
        """Test listing all function definitions."""
        response = await client.get("/api/v1/meta/functions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Found {len(data)} functions")
    
    @pytest.mark.asyncio
    async def test_list_functions_with_pagination(self, client: AsyncClient):
        """Test listing functions with pagination."""
        response = await client.get("/api/v1/meta/functions", params={"skip": 0, "limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
        print(f"✅ Pagination works, got {len(data)} functions")
    
    @pytest.mark.asyncio
    async def test_get_function_by_id(self, client: AsyncClient):
        """Test getting a single function by ID."""
        list_response = await client.get("/api/v1/meta/functions")
        functions = list_response.json()
        
        if functions:
            func_id = functions[0]["id"]
            response = await client.get(f"/api/v1/meta/functions/{func_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == func_id
            print(f"✅ Got function: {data['display_name']}")
        else:
            pytest.skip("No functions available for testing")
    
    @pytest.mark.asyncio
    async def test_function_has_required_fields(self, client: AsyncClient):
        """Test that function response contains required fields."""
        list_response = await client.get("/api/v1/meta/functions")
        functions = list_response.json()
        
        if functions:
            func = functions[0]
            required_fields = ["id", "api_name", "display_name", "output_type"]
            for field in required_fields:
                assert field in func, f"Missing required field: {field}"
            print(f"✅ Function has all required fields")
        else:
            pytest.skip("No functions available for testing")
    
    @pytest.mark.asyncio
    async def test_create_function(self, client: AsyncClient):
        """Test creating a new function definition."""
        unique_name = f"test_func_{uuid.uuid4().hex[:8]}"
        
        payload = {
            "api_name": unique_name,
            "display_name": f"Test Function {unique_name}",
            "description": "Created by automated test",
            "code_content": "def test_func():\n    return 'Hello, World!'",
            "input_params_schema": [
                {"name": "param1", "type": "STRING", "required": True}
            ],
            "output_type": "STRING"
        }
        
        response = await client.post("/api/v1/meta/functions", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["api_name"] == unique_name
        print(f"✅ Created function: {data['display_name']}")
        
        # Cleanup
        delete_response = await client.delete(f"/api/v1/meta/functions/{data['id']}")
        assert delete_response.status_code == 204
        print("✅ Cleaned up test function")

    @pytest.mark.asyncio
    async def test_v3_create_and_delete_function(self, client: AsyncClient):
        """Test V3 function CRUD: create, list, get, delete."""
        unique_name = f"test_v3_func_{uuid.uuid4().hex[:8]}"

        # Create
        payload = {
            "api_name": unique_name,
            "display_name": f"V3 Test Function {unique_name}",
            "code_content": "def main(): return 'ok'",
            "output_type": "STRING",
        }
        cr = await client.post("/api/v3/ontology/functions", json=payload)
        assert cr.status_code == 201, cr.text
        data = cr.json()
        fid = data["id"]
        assert data["api_name"] == unique_name

        # List
        list_r = await client.get("/api/v3/ontology/functions")
        assert list_r.status_code == 200
        assert any(f["id"] == fid for f in list_r.json())

        # Get
        get_r = await client.get(f"/api/v3/ontology/functions/{fid}")
        assert get_r.status_code == 200
        assert get_r.json()["api_name"] == unique_name

        # Delete
        del_r = await client.delete(f"/api/v3/ontology/functions/{fid}")
        assert del_r.status_code == 204
