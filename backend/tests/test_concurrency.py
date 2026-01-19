"""
Concurrency Tests - 并发执行测试
测试并发场景下的正确性和稳定性
"""
import pytest
from httpx import AsyncClient
import asyncio
import uuid


class TestConcurrentCodeExecution:
    """并发代码执行测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_code_executions(self, client: AsyncClient):
        """多个代码执行应该能并发进行"""
        async def execute_code(n: int):
            response = await client.post(
                "/api/v1/execute/code/test",
                json={
                    "code_content": f"def main(ctx): return ctx.get('n', 0) * 2",
                    "context": {"n": n}
                }
            )
            return response.json()
        
        # 并发执行 5 个请求
        tasks = [execute_code(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # 验证所有执行都成功
        for i, result in enumerate(results):
            assert result["success"] is True
            assert result["result"] == i * 2
        
        print(f"✅ Concurrent code executions successful: {[r['result'] for r in results]}")
    
    @pytest.mark.asyncio
    async def test_concurrent_code_executions_isolation(self, client: AsyncClient):
        """并发执行应该相互隔离"""
        async def execute_with_global(name: str, value: int):
            code = f'''
def main(ctx):
    # 每次执行都有自己的局部变量
    local_value = {value}
    return {{"name": "{name}", "value": local_value}}
'''
            response = await client.post(
                "/api/v1/execute/code/test",
                json={"code_content": code, "context": {}}
            )
            return response.json()
        
        # 并发执行多个请求
        tasks = [
            execute_with_global(f"task_{i}", i * 10)
            for i in range(5)
        ]
        results = await asyncio.gather(*tasks)
        
        # 验证结果正确（没有互相干扰）
        for i, result in enumerate(results):
            assert result["success"] is True
            assert result["result"]["name"] == f"task_{i}"
            assert result["result"]["value"] == i * 10
        
        print("✅ Concurrent executions are properly isolated")
    
    @pytest.mark.asyncio
    async def test_concurrent_validate_and_execute(self, client: AsyncClient):
        """并发验证和执行应该正常工作"""
        code = "def main(ctx): return ctx.get('x', 0) ** 2"
        
        async def validate():
            return await client.post(
                "/api/v1/execute/code/validate",
                json={"code_content": code}
            )
        
        async def execute(x: int):
            return await client.post(
                "/api/v1/execute/code/test",
                json={"code_content": code, "context": {"x": x}}
            )
        
        # 并发执行验证和多个执行
        tasks = [
            validate(),
            execute(2),
            execute(3),
            validate(),
            execute(4)
        ]
        results = await asyncio.gather(*tasks)
        
        # 验证结果
        validate_results = [r for r in results if "valid" in r.json()]
        execute_results = [r for r in results if "success" in r.json()]
        
        for vr in validate_results:
            assert vr.json()["valid"] is True
        
        for er in execute_results:
            assert er.json()["success"] is True
        
        print("✅ Concurrent validate and execute works")


class TestConcurrentAPIRequests:
    """并发 API 请求测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_list_requests(self, client: AsyncClient):
        """并发列表查询应该正常工作"""
        async def list_endpoint(endpoint: str):
            response = await client.get(f"/api/v1/meta/{endpoint}")
            return {"endpoint": endpoint, "status": response.status_code, "count": len(response.json())}
        
        endpoints = [
            "object-types",
            "link-types",
            "actions",
            "functions",
            "shared-properties"
        ]
        
        tasks = [list_endpoint(e) for e in endpoints]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            assert result["status"] == 200
            print(f"  {result['endpoint']}: {result['count']} items")
        
        print("✅ Concurrent list requests successful")
    
    @pytest.mark.asyncio
    async def test_concurrent_mixed_operations(self, client: AsyncClient):
        """并发混合操作（读、写、执行）应该正常工作"""
        results = {"reads": 0, "writes": 0, "executes": 0}
        
        async def read_operation():
            response = await client.get("/api/v1/meta/object-types", params={"limit": 5})
            if response.status_code == 200:
                results["reads"] += 1
            return response
        
        async def execute_operation(n: int):
            response = await client.post(
                "/api/v1/execute/code/test",
                json={
                    "code_content": "def main(ctx): return ctx.get('n', 0)",
                    "context": {"n": n}
                }
            )
            if response.status_code == 200 and response.json().get("success"):
                results["executes"] += 1
            return response
        
        # 创建混合任务
        tasks = []
        for i in range(3):
            tasks.append(read_operation())
            tasks.append(execute_operation(i))
        
        await asyncio.gather(*tasks)
        
        assert results["reads"] == 3
        assert results["executes"] == 3
        
        print(f"✅ Concurrent mixed operations: reads={results['reads']}, executes={results['executes']}")
    
    @pytest.mark.asyncio
    async def test_rapid_successive_requests(self, client: AsyncClient):
        """快速连续请求应该正常处理"""
        responses = []
        
        # 快速连续发送 10 个请求
        for i in range(10):
            response = await client.get("/api/v1/meta/object-types", params={"limit": 1})
            responses.append(response.status_code)
        
        # 所有请求应该成功
        assert all(code == 200 for code in responses)
        print(f"✅ Rapid successive requests all successful ({len(responses)} requests)")


class TestConcurrentExecutionLogs:
    """并发执行日志测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_log_queries(self, client: AsyncClient):
        """并发日志查询应该正常工作"""
        async def query_logs(params: dict):
            response = await client.get("/api/v1/execute/logs", params=params)
            return response
        
        # 并发查询不同条件
        tasks = [
            query_logs({"limit": 10}),
            query_logs({"exec_status": "SUCCESS", "limit": 5}),
            query_logs({"exec_status": "FAILED", "limit": 5}),
            query_logs({"skip": 0, "limit": 20}),
        ]
        
        results = await asyncio.gather(*tasks)
        
        for result in results:
            assert result.status_code == 200
            assert isinstance(result.json(), list)
        
        print("✅ Concurrent log queries successful")
    
    @pytest.mark.asyncio
    async def test_execute_and_query_logs_concurrent(self, client: AsyncClient):
        """执行代码的同时查询日志应该正常工作"""
        async def execute_code():
            return await client.post(
                "/api/v1/execute/code/test",
                json={
                    "code_content": "def main(ctx): return 'test'",
                    "context": {}
                }
            )
        
        async def query_logs():
            return await client.get("/api/v1/execute/logs", params={"limit": 10})
        
        # 并发执行代码和查询日志
        tasks = [
            execute_code(),
            query_logs(),
            execute_code(),
            query_logs(),
        ]
        
        results = await asyncio.gather(*tasks)
        
        execute_results = [r for r in results if "success" in r.json()]
        log_results = [r for r in results if isinstance(r.json(), list)]
        
        assert len(execute_results) == 2
        assert len(log_results) == 2
        
        for er in execute_results:
            assert er.json()["success"] is True
        
        print("✅ Execute and query logs concurrent works")


class TestConcurrencyStress:
    """并发压力测试"""
    
    @pytest.mark.asyncio
    async def test_high_concurrency_code_execution(self, client: AsyncClient):
        """高并发代码执行测试"""
        NUM_REQUESTS = 20
        
        async def execute(n: int):
            response = await client.post(
                "/api/v1/execute/code/test",
                json={
                    "code_content": "def main(ctx): return ctx.get('n', 0)",
                    "context": {"n": n},
                    "timeout_seconds": 10
                }
            )
            return {"n": n, "status": response.status_code, "success": response.json().get("success")}
        
        # 高并发执行
        tasks = [execute(i) for i in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)
        
        # 统计结果
        success_count = sum(1 for r in results if r["success"])
        
        print(f"✅ High concurrency test: {success_count}/{NUM_REQUESTS} succeeded")
        
        # 至少 90% 应该成功
        assert success_count >= NUM_REQUESTS * 0.9
    
    @pytest.mark.asyncio
    async def test_concurrent_different_executors(self, client: AsyncClient):
        """并发使用不同执行器"""
        async def execute_builtin():
            return await client.post(
                "/api/v1/execute/code/test",
                json={
                    "code_content": "def main(ctx): return 'builtin'",
                    "context": {},
                    "executor_type": "builtin"
                }
            )
        
        async def execute_subprocess():
            return await client.post(
                "/api/v1/execute/code/test",
                json={
                    "code_content": "def main(ctx): return 'subprocess'",
                    "context": {},
                    "executor_type": "subprocess"
                }
            )
        
        # 并发使用不同执行器
        tasks = [
            execute_builtin(),
            execute_subprocess(),
            execute_builtin(),
            execute_subprocess(),
        ]
        
        results = await asyncio.gather(*tasks)
        
        for result in results:
            data = result.json()
            assert data["success"] is True
            assert data["executor_used"] in ["builtin", "subprocess"]
        
        print("✅ Concurrent different executors work")
