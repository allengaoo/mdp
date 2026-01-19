"""
Tests for LinkType API endpoints.
"""
import pytest
from httpx import AsyncClient


class TestLinkTypeAPI:
    """Test cases for /meta/link-types endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_link_types(self, client: AsyncClient):
        """Test listing all link types."""
        response = await client.get("/api/v1/meta/link-types")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Found {len(data)} link types")
    
    @pytest.mark.asyncio
    async def test_list_link_types_with_pagination(self, client: AsyncClient):
        """Test listing link types with pagination."""
        response = await client.get("/api/v1/meta/link-types", params={"skip": 0, "limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
        print(f"✅ Pagination works, got {len(data)} link types")
    
    @pytest.mark.asyncio
    async def test_get_link_type_by_id(self, client: AsyncClient):
        """Test getting a single link type by ID."""
        list_response = await client.get("/api/v1/meta/link-types")
        link_types = list_response.json()
        
        if link_types:
            link_id = link_types[0]["id"]
            response = await client.get(f"/api/v1/meta/link-types/{link_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == link_id
            print(f"✅ Got link type: {data['display_name']}")
        else:
            pytest.skip("No link types available for testing")
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_link_type(self, client: AsyncClient):
        """Test getting a non-existent link type returns 404."""
        response = await client.get("/api/v1/meta/link-types/nonexistent-id-12345")
        assert response.status_code == 404
        print("✅ Non-existent link type returns 404")
