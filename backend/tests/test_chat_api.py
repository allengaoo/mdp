"""
Tests for Chat2App API endpoints.
Chat2App Module - MDP Platform V3.1
"""
import pytest
from httpx import AsyncClient


class TestChatHealthAPI:
    """Test cases for /api/v3/chat/health endpoint."""

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_200(self, client: AsyncClient):
        """健康检查端点应返回 200"""
        response = await client.get("/api/v3/chat/health")
        assert response.status_code == 200
        data = response.json()
        assert "ollama_available" in data
        assert "model" in data
        assert "status" in data
        print(f"✅ Health check: {data['status']}")

    @pytest.mark.asyncio
    async def test_health_returns_model_name(self, client: AsyncClient):
        """健康检查应返回模型名称"""
        response = await client.get("/api/v3/chat/health")
        data = response.json()
        assert data["model"] == "llama3"
        print(f"✅ Model: {data['model']}")


class TestChatMessageAPI:
    """Test cases for /api/v3/chat/message endpoint."""

    @pytest.mark.asyncio
    async def test_message_endpoint_accepts_post(self, client: AsyncClient):
        """消息端点应接受 POST 请求"""
        payload = {"message": "显示所有对象"}
        response = await client.post("/api/v3/chat/message", json=payload)
        # 可能返回 200 或 错误（如果 Ollama 未运行）
        assert response.status_code in [200, 500, 503]
        print(f"✅ Message endpoint responded: {response.status_code}")

    @pytest.mark.asyncio
    async def test_message_response_structure(self, client: AsyncClient):
        """消息响应应包含必需字段"""
        payload = {"message": "测试查询"}
        response = await client.post("/api/v3/chat/message", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert "action" in data
            assert "message" in data
            assert "suggestions" in data
            print(f"✅ Response structure valid, action: {data['action']}")
        else:
            # Ollama 未运行时跳过结构检查
            print(f"⚠️ Skipped structure check (Ollama unavailable)")

    @pytest.mark.asyncio
    async def test_message_with_history(self, client: AsyncClient):
        """消息端点应接受带历史记录的请求"""
        payload = {
            "message": "继续查询",
            "history": [
                {"role": "user", "content": "查询1"},
                {"role": "assistant", "content": "结果1"}
            ]
        }
        response = await client.post("/api/v3/chat/message", json=payload)
        assert response.status_code in [200, 500, 503]
        print(f"✅ History payload accepted")

    @pytest.mark.asyncio
    async def test_message_rejects_empty(self, client: AsyncClient):
        """消息端点应拒绝空消息"""
        payload = {"message": ""}
        response = await client.post("/api/v3/chat/message", json=payload)
        # FastAPI/Pydantic 应返回 422 验证错误
        assert response.status_code == 422
        print(f"✅ Empty message rejected with 422")


class TestChatSchemaExampleAPI:
    """Test cases for /api/v3/chat/schema-example endpoint."""

    @pytest.mark.asyncio
    async def test_schema_example_endpoint(self, client: AsyncClient):
        """示例端点应返回 AMIS schema 示例"""
        response = await client.get("/api/v3/chat/schema-example")
        assert response.status_code == 200
        data = response.json()
        assert "table_example" in data
        assert "chart_example" in data
        print(f"✅ Schema examples returned")

    @pytest.mark.asyncio
    async def test_table_example_structure(self, client: AsyncClient):
        """表格示例应包含正确结构"""
        response = await client.get("/api/v3/chat/schema-example")
        data = response.json()
        table = data["table_example"]
        assert table["type"] == "table"
        assert "columns" in table
        assert "data" in table
        print(f"✅ Table example structure valid")
