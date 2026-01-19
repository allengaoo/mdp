"""
Tests for DataSource API endpoints.
"""
import pytest
from httpx import AsyncClient


class TestDataSourceAPI:
    """Test cases for /meta/datasources endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_datasources(self, client: AsyncClient):
        """Test listing all datasources."""
        response = await client.get("/api/v1/meta/datasources")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Found {len(data)} datasources")
    
    @pytest.mark.asyncio
    async def test_list_datasource_tables(self, client: AsyncClient):
        """Test listing datasource tables (alias endpoint)."""
        response = await client.get("/api/v1/meta/datasource-tables")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Found {len(data)} datasource tables")
    
    @pytest.mark.asyncio
    async def test_datasource_has_required_fields(self, client: AsyncClient):
        """Test that datasource response contains required fields."""
        response = await client.get("/api/v1/meta/datasources")
        data = response.json()
        
        if data:
            datasource = data[0]
            required_fields = ["id", "table_name", "db_type"]
            for field in required_fields:
                assert field in datasource, f"Missing required field: {field}"
            print(f"✅ Datasource has all required fields")
        else:
            pytest.skip("No datasources available for testing")
