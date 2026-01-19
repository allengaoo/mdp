"""
Tests for ActionDefinition API endpoints.
"""
import pytest
from httpx import AsyncClient
import uuid


class TestActionDefinitionAPI:
    """Test cases for /meta/actions and /meta/action-definitions endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_actions(self, client: AsyncClient):
        """Test listing all action definitions."""
        response = await client.get("/api/v1/meta/actions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Found {len(data)} actions")
    
    @pytest.mark.asyncio
    async def test_list_actions_alias(self, client: AsyncClient):
        """Test listing actions using alias endpoint."""
        response = await client.get("/api/v1/meta/action-definitions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Alias endpoint works, found {len(data)} actions")
    
    @pytest.mark.asyncio
    async def test_get_action_by_id(self, client: AsyncClient):
        """Test getting a single action by ID."""
        list_response = await client.get("/api/v1/meta/actions")
        actions = list_response.json()
        
        if actions:
            action_id = actions[0]["id"]
            response = await client.get(f"/api/v1/meta/actions/{action_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == action_id
            print(f"✅ Got action: {data['display_name']}")
        else:
            pytest.skip("No actions available for testing")
    
    @pytest.mark.asyncio
    async def test_get_action_alias(self, client: AsyncClient):
        """Test getting action using alias endpoint."""
        list_response = await client.get("/api/v1/meta/action-definitions")
        actions = list_response.json()
        
        if actions:
            action_id = actions[0]["id"]
            response = await client.get(f"/api/v1/meta/action-definitions/{action_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == action_id
            print(f"✅ Alias endpoint works for single action")
        else:
            pytest.skip("No actions available for testing")
    
    @pytest.mark.asyncio
    async def test_action_has_required_fields(self, client: AsyncClient):
        """Test that action response contains required fields."""
        list_response = await client.get("/api/v1/meta/actions")
        actions = list_response.json()
        
        if actions:
            action = actions[0]
            required_fields = ["id", "api_name", "display_name", "backing_function_id"]
            for field in required_fields:
                assert field in action, f"Missing required field: {field}"
            print(f"✅ Action has all required fields")
        else:
            pytest.skip("No actions available for testing")
    
    @pytest.mark.asyncio
    async def test_create_and_update_action(self, client: AsyncClient):
        """Test creating and updating an action definition."""
        # First, get a function ID to use as backing function
        functions_response = await client.get("/api/v1/meta/functions")
        functions = functions_response.json()
        
        if not functions:
            pytest.skip("No functions available for testing")
        
        backing_function_id = functions[0]["id"]
        unique_name = f"test_action_{uuid.uuid4().hex[:8]}"
        
        # Create action
        create_payload = {
            "api_name": unique_name,
            "display_name": "Test Action Original",
            "backing_function_id": backing_function_id
        }
        
        create_response = await client.post("/api/v1/meta/actions", json=create_payload)
        assert create_response.status_code == 201
        action_id = create_response.json()["id"]
        print(f"✅ Created action: {unique_name}")
        
        # Update action
        update_payload = {
            "display_name": "Test Action Updated"
        }
        
        update_response = await client.put(f"/api/v1/meta/actions/{action_id}", json=update_payload)
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["display_name"] == "Test Action Updated"
        print(f"✅ Updated action display name")
        
        # Cleanup
        delete_response = await client.delete(f"/api/v1/meta/actions/{action_id}")
        assert delete_response.status_code == 204
        print("✅ Cleaned up test action")
    
    @pytest.mark.asyncio
    async def test_update_action_alias(self, client: AsyncClient):
        """Test updating action using alias endpoint."""
        # First, get a function ID to use as backing function
        functions_response = await client.get("/api/v1/meta/functions")
        functions = functions_response.json()
        
        if not functions:
            pytest.skip("No functions available for testing")
        
        backing_function_id = functions[0]["id"]
        unique_name = f"test_alias_{uuid.uuid4().hex[:8]}"
        
        # Create action
        create_payload = {
            "api_name": unique_name,
            "display_name": "Alias Test Original",
            "backing_function_id": backing_function_id
        }
        
        create_response = await client.post("/api/v1/meta/action-definitions", json=create_payload)
        assert create_response.status_code == 201
        action_id = create_response.json()["id"]
        
        # Update via alias
        update_payload = {
            "display_name": "Alias Test Updated"
        }
        
        update_response = await client.put(f"/api/v1/meta/action-definitions/{action_id}", json=update_payload)
        assert update_response.status_code == 200
        assert update_response.json()["display_name"] == "Alias Test Updated"
        print(f"✅ Alias PUT endpoint works")
        
        # Cleanup
        await client.delete(f"/api/v1/meta/action-definitions/{action_id}")
        print("✅ Cleaned up test action")
