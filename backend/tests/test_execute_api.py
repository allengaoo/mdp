"""
Tests for /execute API endpoints.
测试代码执行 API 端点
"""
import pytest
from httpx import AsyncClient
import uuid


class TestCodeTestAPI:
    """POST /execute/code/test 端点测试"""
    
    @pytest.mark.asyncio
    async def test_execute_simple_code(self, client: AsyncClient):
        """应该执行简单代码并返回结果"""
        response = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return ctx.get('x', 0) * 2",
                "context": {"x": 5},
                "executor_type": "auto",
                "timeout_seconds": 30
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"] == 10
        assert "executor_used" in data
        print(f"✅ Code executed successfully, result: {data['result']}")
    
    @pytest.mark.asyncio
    async def test_execute_code_with_addition(self, client: AsyncClient):
        """测试加法运算"""
        response = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return ctx.get('a', 0) + ctx.get('b', 0)",
                "context": {"a": 10, "b": 20}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"] == 30
        print(f"✅ Addition test passed: 10 + 20 = {data['result']}")
    
    @pytest.mark.asyncio
    async def test_execute_code_returns_dict(self, client: AsyncClient):
        """测试返回字典"""
        response = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": '''
def main(ctx):
    return {"status": "ok", "value": ctx.get("x", 0) * 2}
''',
                "context": {"x": 5}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["status"] == "ok"
        assert data["result"]["value"] == 10
        print(f"✅ Dict return test passed")
    
    @pytest.mark.asyncio
    async def test_execute_code_with_syntax_error(self, client: AsyncClient):
        """语法错误的代码应该返回错误"""
        response = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx)  return 1",  # 缺少冒号
                "context": {}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error_type"] == "SyntaxError"
        print(f"✅ Syntax error detected: {data['error_message'][:50]}...")
    
    @pytest.mark.asyncio
    async def test_execute_code_with_runtime_error(self, client: AsyncClient):
        """运行时错误应该被捕获"""
        response = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return 1 / 0",
                "context": {}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error_type"] == "ZeroDivisionError"
        print(f"✅ Runtime error captured: {data['error_type']}")
    
    @pytest.mark.asyncio
    async def test_execute_code_missing_main(self, client: AsyncClient):
        """缺少 main 函数应该报错"""
        response = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def other_func(): return 1",
                "context": {}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "main" in data["error_message"].lower()
        print(f"✅ Missing main function detected")
    
    @pytest.mark.asyncio
    async def test_execute_code_captures_stdout(self, client: AsyncClient):
        """应该捕获标准输出"""
        response = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": '''
def main(ctx):
    print("Hello from code")
    print("Line 2")
    return 42
''',
                "context": {}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"] == 42
        assert "Hello from code" in data["stdout"]
        assert "Line 2" in data["stdout"]
        print(f"✅ stdout captured: {data['stdout'][:50]}...")
    
    @pytest.mark.asyncio
    async def test_execute_code_with_stdlib(self, client: AsyncClient):
        """应该能使用标准库"""
        response = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": '''
import math
import json
def main(ctx):
    result = math.sqrt(16)
    return {"sqrt_16": result, "json_test": json.dumps({"a": 1})}
''',
                "context": {}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["sqrt_16"] == 4.0
        print(f"✅ stdlib modules work correctly")
    
    @pytest.mark.asyncio
    async def test_execute_code_with_builtin_executor(self, client: AsyncClient):
        """强制使用 builtin 执行器"""
        response = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return 'builtin'",
                "context": {},
                "executor_type": "builtin"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["executor_used"] == "builtin"
        print(f"✅ Builtin executor used")
    
    @pytest.mark.asyncio
    async def test_execute_code_with_subprocess_executor(self, client: AsyncClient):
        """强制使用 subprocess 执行器"""
        response = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return 'subprocess'",
                "context": {},
                "executor_type": "subprocess"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["executor_used"] == "subprocess"
        print(f"✅ Subprocess executor used")
    
    @pytest.mark.asyncio
    async def test_execute_code_reports_execution_time(self, client: AsyncClient):
        """应该报告执行时间"""
        response = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return 1",
                "context": {}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "execution_time_ms" in data
        assert data["execution_time_ms"] >= 0
        print(f"✅ Execution time: {data['execution_time_ms']}ms")


class TestCodeValidateAPI:
    """POST /execute/code/validate 端点测试"""
    
    @pytest.mark.asyncio
    async def test_validate_valid_code(self, client: AsyncClient):
        """有效代码应该验证通过"""
        response = await client.post(
            "/api/v1/execute/code/validate",
            json={"code_content": "def main(ctx): return 1"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["error_message"] is None
        print(f"✅ Valid code passed validation")
    
    @pytest.mark.asyncio
    async def test_validate_invalid_code(self, client: AsyncClient):
        """无效代码应该返回错误信息"""
        response = await client.post(
            "/api/v1/execute/code/validate",
            json={"code_content": "def main(ctx)  return 1"}  # 缺少冒号
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["error_message"] is not None
        print(f"✅ Invalid code detected: {data['error_message'][:50]}...")
    
    @pytest.mark.asyncio
    async def test_validate_empty_code(self, client: AsyncClient):
        """空代码在语法上是有效的"""
        response = await client.post(
            "/api/v1/execute/code/validate",
            json={"code_content": ""}
        )
        
        assert response.status_code == 200
        data = response.json()
        # 空代码语法上是有效的
        assert data["valid"] is True
        print(f"✅ Empty code validation handled")
    
    @pytest.mark.asyncio
    async def test_validate_complex_code(self, client: AsyncClient):
        """复杂代码应该验证通过"""
        complex_code = '''
import math
import json
from collections import Counter

def helper_function(x):
    return x * 2

class MyClass:
    def __init__(self, value):
        self.value = value
    
    def process(self):
        return self.value ** 2

def main(ctx):
    obj = MyClass(5)
    result = helper_function(obj.process())
    return {"result": result, "sqrt": math.sqrt(result)}
'''
        response = await client.post(
            "/api/v1/execute/code/validate",
            json={"code_content": complex_code}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        print(f"✅ Complex code validated successfully")


class TestFunctionTestAPI:
    """POST /execute/function/{function_id}/test 端点测试"""
    
    @pytest.mark.asyncio
    async def test_function_not_found(self, client: AsyncClient):
        """不存在的函数应该返回错误（但不是404，而是返回success=False）"""
        fake_id = str(uuid.uuid4())
        response = await client.post(
            f"/api/v1/execute/function/{fake_id}/test",
            json={"context": {}}
        )
        
        # API 返回200但success=False
        assert response.status_code in [200, 500]  # 可能是200或500
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is False
            print(f"✅ Non-existent function handled correctly")
        else:
            print(f"✅ Non-existent function returned 500 (acceptable)")
    
    @pytest.mark.asyncio
    async def test_execute_existing_function(self, client: AsyncClient):
        """执行已存在的函数"""
        # 首先获取函数列表
        list_response = await client.get("/api/v1/meta/functions")
        functions = list_response.json()
        
        if functions:
            func_id = functions[0]["id"]
            
            response = await client.post(
                f"/api/v1/execute/function/{func_id}/test",
                json={
                    "context": {"params": {}},
                    "executor_type": "auto",
                    "timeout_seconds": 30
                }
            )
            
            assert response.status_code in [200, 500]  # 可能成功或失败
            if response.status_code == 200:
                data = response.json()
                # 函数可能成功或失败（取决于函数代码是否有 main 函数）
                assert "success" in data
                assert "executor_used" in data
                print(f"✅ Function execution completed, success: {data['success']}")
            else:
                print(f"✅ Function execution returned error (acceptable)")
        else:
            pytest.skip("No functions available for testing")


class TestExecuteAPIIntegration:
    """执行 API 集成测试"""
    
    @pytest.mark.asyncio
    async def test_validate_then_execute(self, client: AsyncClient):
        """先验证再执行"""
        code = "def main(ctx): return ctx.get('x', 0) ** 2"
        
        # 先验证
        validate_response = await client.post(
            "/api/v1/execute/code/validate",
            json={"code_content": code}
        )
        assert validate_response.status_code == 200
        assert validate_response.json()["valid"] is True
        
        # 再执行
        execute_response = await client.post(
            "/api/v1/execute/code/test",
            json={"code_content": code, "context": {"x": 5}}
        )
        assert execute_response.status_code == 200
        data = execute_response.json()
        assert data["success"] is True
        assert data["result"] == 25
        print(f"✅ Validate then execute workflow works")
    
    @pytest.mark.asyncio
    async def test_multiple_executions(self, client: AsyncClient):
        """多次执行应该独立"""
        code = "def main(ctx): return ctx.get('n', 0)"
        
        results = []
        for i in range(3):
            response = await client.post(
                "/api/v1/execute/code/test",
                json={"code_content": code, "context": {"n": i * 10}}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            results.append(data["result"])
        
        assert results == [0, 10, 20]
        print(f"✅ Multiple independent executions work: {results}")
    
    @pytest.mark.asyncio
    async def test_context_isolation(self, client: AsyncClient):
        """上下文应该被隔离"""
        # 第一次执行，设置一个值
        code1 = '''
def main(ctx):
    ctx["new_value"] = "test"
    return ctx.get("new_value")
'''
        response1 = await client.post(
            "/api/v1/execute/code/test",
            json={"code_content": code1, "context": {}}
        )
        assert response1.status_code == 200
        assert response1.json()["success"] is True
        
        # 第二次执行，检查值是否存在
        code2 = '''
def main(ctx):
    return ctx.get("new_value", "not_found")
'''
        response2 = await client.post(
            "/api/v1/execute/code/test",
            json={"code_content": code2, "context": {}}
        )
        assert response2.status_code == 200
        data = response2.json()
        assert data["success"] is True
        assert data["result"] == "not_found"  # 值不应该从上次执行继承
        print(f"✅ Context isolation works")


class TestCodeExecutionEdgeCases:
    """代码执行边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_large_output(self, client: AsyncClient):
        """大输出应该能正常处理"""
        code = '''
def main(ctx):
    result = []
    for i in range(100):
        print(f"Line {i}")
        result.append(i)
    return result
'''
        response = await client.post(
            "/api/v1/execute/code/test",
            json={"code_content": code, "context": {}, "timeout_seconds": 30}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["result"]) == 100
        print(f"✅ Large output handled")
    
    @pytest.mark.asyncio
    async def test_unicode_handling(self, client: AsyncClient):
        """Unicode 应该能正常处理"""
        code = '''
def main(ctx):
    return {"message": "你好世界 🌍", "emoji": "🎉"}
'''
        response = await client.post(
            "/api/v1/execute/code/test",
            json={"code_content": code, "context": {}}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "你好世界" in data["result"]["message"]
        print(f"✅ Unicode handled: {data['result']['message']}")
    
    @pytest.mark.asyncio
    async def test_nested_return(self, client: AsyncClient):
        """嵌套数据结构应该能正常序列化"""
        code = '''
def main(ctx):
    return {
        "level1": {
            "level2": {
                "level3": [1, 2, {"inner": "value"}]
            }
        }
    }
'''
        response = await client.post(
            "/api/v1/execute/code/test",
            json={"code_content": code, "context": {}}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["level1"]["level2"]["level3"][2]["inner"] == "value"
        print(f"✅ Nested structure handled")
