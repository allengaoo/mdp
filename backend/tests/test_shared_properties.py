"""
Tests for SharedProperty API endpoints.
"""
import pytest
from httpx import AsyncClient
import uuid


class TestSharedPropertyAPI:
    """Test cases for /meta/shared-properties endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_shared_properties(self, client: AsyncClient):
        """Test listing all shared properties."""
        response = await client.get("/api/v1/meta/shared-properties")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Found {len(data)} shared properties")
    
    @pytest.mark.asyncio
    async def test_list_shared_properties_with_pagination(self, client: AsyncClient):
        """Test listing shared properties with pagination."""
        response = await client.get("/api/v1/meta/shared-properties", params={"skip": 0, "limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
        print(f"✅ Pagination works, got {len(data)} shared properties")
    
    @pytest.mark.asyncio
    async def test_create_shared_property(self, client: AsyncClient):
        """Test creating a new shared property."""
        unique_name = f"test_prop_{uuid.uuid4().hex[:8]}"
        
        payload = {
            "api_name": unique_name,
            "display_name": f"Test Property {unique_name}",
            "data_type": "STRING",
            "description": "Created by automated test"
        }
        
        response = await client.post("/api/v1/meta/shared-properties", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["api_name"] == unique_name
        print(f"✅ Created shared property: {data['display_name']}")
        
        # Cleanup
        delete_response = await client.delete(f"/api/v1/meta/shared-properties/{data['id']}")
        assert delete_response.status_code == 204
        print("✅ Cleaned up test shared property")
    
    @pytest.mark.asyncio
    async def test_update_shared_property(self, client: AsyncClient):
        """Test updating a shared property."""
        unique_name = f"test_update_{uuid.uuid4().hex[:8]}"
        
        # Create
        create_payload = {
            "api_name": unique_name,
            "display_name": "Original Name",
            "data_type": "STRING"
        }
        
        create_response = await client.post("/api/v1/meta/shared-properties", json=create_payload)
        assert create_response.status_code == 201
        prop_id = create_response.json()["id"]
        
        # Update
        update_payload = {
            "display_name": "Updated Name",
            "description": "Updated description"
        }
        
        update_response = await client.put(f"/api/v1/meta/shared-properties/{prop_id}", json=update_payload)
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["display_name"] == "Updated Name"
        print(f"✅ Updated shared property")
        
        # Cleanup
        await client.delete(f"/api/v1/meta/shared-properties/{prop_id}")
        print("✅ Cleaned up test shared property")
    
    @pytest.mark.asyncio
    async def test_shared_property_has_required_fields(self, client: AsyncClient):
        """Test that shared property response contains required fields."""
        unique_name = f"test_fields_{uuid.uuid4().hex[:8]}"
        
        payload = {
            "api_name": unique_name,
            "display_name": "Field Test",
            "data_type": "INTEGER"
        }
        
        response = await client.post("/api/v1/meta/shared-properties", json=payload)
        assert response.status_code == 201
        data = response.json()
        
        required_fields = ["id", "api_name", "display_name", "data_type"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        print(f"✅ Shared property has all required fields")
        
        # Cleanup
        await client.delete(f"/api/v1/meta/shared-properties/{data['id']}")
