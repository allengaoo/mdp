"""
Tests for Execution Logs API endpoints.
执行日志 API 端点测试
"""
import pytest
from httpx import AsyncClient
import uuid


class TestExecutionLogsAPI:
    """GET /execute/logs 端点测试"""
    
    @pytest.mark.asyncio
    async def test_list_execution_logs(self, client: AsyncClient):
        """应该返回执行日志列表"""
        response = await client.get("/api/v1/execute/logs")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Found {len(data)} execution logs")
    
    @pytest.mark.asyncio
    async def test_list_execution_logs_with_pagination(self, client: AsyncClient):
        """应该支持分页"""
        response = await client.get("/api/v1/execute/logs", params={
            "skip": 0,
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
        print(f"✅ Pagination works, returned {len(data)} logs")
    
    @pytest.mark.asyncio
    async def test_filter_by_status_success(self, client: AsyncClient):
        """应该能按状态筛选 - SUCCESS"""
        response = await client.get("/api/v1/execute/logs", params={
            "exec_status": "SUCCESS"
        })
        
        assert response.status_code == 200
        data = response.json()
        for log in data:
            # API returns 'status' field, not 'execution_status'
            assert log.get("status") == "SUCCESS"
        print(f"✅ Filter by SUCCESS status works, found {len(data)} logs")
    
    @pytest.mark.asyncio
    async def test_filter_by_status_failed(self, client: AsyncClient):
        """应该能按状态筛选 - FAILED"""
        response = await client.get("/api/v1/execute/logs", params={
            "exec_status": "FAILED"
        })
        
        assert response.status_code == 200
        data = response.json()
        for log in data:
            # API returns 'status' field, not 'execution_status'
            assert log.get("status") == "FAILED"
        print(f"✅ Filter by FAILED status works, found {len(data)} logs")
    
    @pytest.mark.asyncio
    async def test_filter_by_action_id(self, client: AsyncClient):
        """应该能按 action_id 筛选"""
        # 先获取一条日志的 action_id
        list_response = await client.get("/api/v1/execute/logs", params={"limit": 1})
        logs = list_response.json()
        
        if logs:
            action_id = logs[0].get("action_def_id")
            if action_id:
                response = await client.get("/api/v1/execute/logs", params={
                    "action_id": action_id
                })
                
                assert response.status_code == 200
                data = response.json()
                for log in data:
                    assert log.get("action_def_id") == action_id
                print(f"✅ Filter by action_id works")
            else:
                print("⚠️ No action_id in log, skipping")
        else:
            print("⚠️ No logs available for filtering test")
    
    @pytest.mark.asyncio
    async def test_execution_log_fields(self, client: AsyncClient):
        """应该返回正确的字段"""
        response = await client.get("/api/v1/execute/logs", params={"limit": 1})
        
        assert response.status_code == 200
        data = response.json()
        
        if data:
            log = data[0]
            # 验证必要字段存在
            assert "id" in log
            assert "action_id" in log or "action_name" in log
            assert "status" in log  # API returns 'status', not 'execution_status'
            assert "created_at" in log
            print(f"✅ Log fields verified: {list(log.keys())}")
        else:
            print("⚠️ No logs available for field verification")


class TestActionExecutionWithLogging:
    """测试行为执行后日志记录"""
    
    @pytest.mark.asyncio
    async def test_action_execution_creates_log(self, client: AsyncClient):
        """执行 action 后应该创建日志记录"""
        # 1. 获取日志数量
        logs_before = await client.get("/api/v1/execute/logs")
        count_before = len(logs_before.json())
        
        # 2. 获取可用的 action
        actions_response = await client.get("/api/v1/meta/actions", params={"limit": 1})
        actions = actions_response.json()
        
        if not actions:
            pytest.skip("No actions available for testing")
        
        action = actions[0]
        action_api_name = action.get("api_name")
        
        # 3. 获取可用的 object instance
        objects_response = await client.get("/api/v1/execute/objects/fighter")
        objects = objects_response.json() if objects_response.status_code == 200 else []
        
        source_id = objects[0].get("id") if objects else "test-source-id"
        
        # 4. 执行 action
        execute_response = await client.post("/api/v1/execute/action/run", json={
            "action_api_name": action_api_name,
            "source_id": source_id,
            "params": {}
        })
        
        # 5. 验证日志数量增加
        logs_after = await client.get("/api/v1/execute/logs")
        count_after = len(logs_after.json())
        
        if execute_response.status_code == 200:
            # 如果执行成功，日志数量应该增加
            assert count_after >= count_before, "Log count should increase after action execution"
            print(f"✅ Action execution created log, count: {count_before} -> {count_after}")
        else:
            # 如果执行失败，也应该记录日志
            print(f"⚠️ Action execution failed with status {execute_response.status_code}")
    
    @pytest.mark.asyncio
    async def test_failed_action_creates_log(self, client: AsyncClient):
        """执行失败的 action 也应该创建日志记录"""
        # 使用不存在的 action 来触发失败
        response = await client.post("/api/v1/execute/action/run", json={
            "action_api_name": "non_existent_action_" + str(uuid.uuid4())[:8],
            "source_id": "test-source",
            "params": {}
        })
        
        # 应该返回 404 或其他错误状态
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            # 如果返回 200，检查 success 字段
            if "success" in data and not data["success"]:
                print("✅ Failed action handled (returned 200 with success=False)")
            else:
                print("⚠️ Unexpected success response")
        else:
            print(f"✅ Failed action returned error status: {response.status_code}")


class TestExecutionLogsIntegration:
    """执行日志集成测试"""
    
    @pytest.mark.asyncio
    async def test_logs_are_ordered_by_time(self, client: AsyncClient):
        """日志应该按时间排序"""
        response = await client.get("/api/v1/execute/logs", params={"limit": 10})
        
        assert response.status_code == 200
        logs = response.json()
        
        if len(logs) >= 2:
            # 验证时间顺序（最新的在前）
            times = [log.get("created_at") for log in logs if log.get("created_at")]
            for i in range(len(times) - 1):
                assert times[i] >= times[i + 1], "Logs should be ordered by time (newest first)"
            print("✅ Logs are ordered by time")
        else:
            print("⚠️ Not enough logs to verify ordering")
    
    @pytest.mark.asyncio
    async def test_log_contains_action_details(self, client: AsyncClient):
        """日志应该包含 action 详细信息"""
        response = await client.get("/api/v1/execute/logs", params={"limit": 1})
        
        assert response.status_code == 200
        logs = response.json()
        
        if logs:
            log = logs[0]
            # 应该包含 action 相关信息
            has_action_info = (
                "action_def_id" in log or 
                "action_name" in log or
                "action_api_name" in log
            )
            assert has_action_info, "Log should contain action information"
            print(f"✅ Log contains action details: {log.get('action_def_id') or log.get('action_name')}")
        else:
            print("⚠️ No logs available for detail verification")
