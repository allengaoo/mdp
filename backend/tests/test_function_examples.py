"""
Function execution examples - 用于验证函数试运行功能的测试用例。

覆盖场景：
- 正常运行：简单计算、stdlib、返回字典、print 捕获
- 预期失败：缺少 main、语法错误、运行时错误、禁用 builtins、subprocess 无运行时 API
"""
import pytest
from httpx import AsyncClient


class TestFunctionExamplesSuccess:
    """预期成功的函数示例"""

    @pytest.mark.asyncio
    async def test_simple_calculation(self, client: AsyncClient):
        """简单计算"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return ctx.get('x', 0) * 2",
                "context": {"x": 5},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["result"] == 10

    @pytest.mark.asyncio
    async def test_return_dict(self, client: AsyncClient):
        """返回字典"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": """
def main(ctx):
    return {"sum": ctx.get("a", 0) + ctx.get("b", 0)}
""",
                "context": {"a": 10, "b": 20},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["result"]["sum"] == 30

    @pytest.mark.asyncio
    async def test_use_math(self, client: AsyncClient):
        """使用预加载的 math"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return math.sqrt(ctx.get('n', 9))",
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["result"] == 3.0

    @pytest.mark.asyncio
    async def test_use_json(self, client: AsyncClient):
        """使用预加载的 json"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return json.dumps({'echo': ctx})",
                "context": {"key": "value"},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        import json
        parsed = json.loads(data["result"])
        assert parsed["echo"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_use_datetime(self, client: AsyncClient):
        """使用预加载的 datetime"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return str(datetime.datetime.now())[:10]",
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["result"]) >= 10  # "YYYY-MM-DD"

    @pytest.mark.asyncio
    async def test_use_random(self, client: AsyncClient):
        """使用预加载的 random"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return random.randint(1, 100)",
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert 1 <= data["result"] <= 100

    @pytest.mark.asyncio
    async def test_stdout_captured(self, client: AsyncClient):
        """print 输出被捕获"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": """
def main(ctx):
    print("Hello from code")
    return 42
""",
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["result"] == 42
        assert "Hello from code" in data.get("stdout", "")

    @pytest.mark.asyncio
    async def test_empty_context(self, client: AsyncClient):
        """空 context"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return ctx.get('x', 'default')",
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["result"] == "default"

    @pytest.mark.asyncio
    async def test_exception_handling(self, client: AsyncClient):
        """用户代码内部捕获异常"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": """
def main(ctx):
    try:
        return 1 / 0
    except ZeroDivisionError:
        return "caught"
""",
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["result"] == "caught"


class TestFunctionExamplesFailure:
    """预期失败的函数示例"""

    @pytest.mark.asyncio
    async def test_missing_main(self, client: AsyncClient):
        """缺少 main 函数"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def foo(): return 1",
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert "main" in data.get("error_message", "").lower()

    @pytest.mark.asyncio
    async def test_syntax_error(self, client: AsyncClient):
        """语法错误"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx) return 1",  # 缺少冒号
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert data.get("error_type") == "SyntaxError"

    @pytest.mark.asyncio
    async def test_zero_division(self, client: AsyncClient):
        """除零错误"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return 1 / 0",
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert data.get("error_type") == "ZeroDivisionError"

    @pytest.mark.asyncio
    async def test_key_error(self, client: AsyncClient):
        """KeyError"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": 'def main(ctx): return ctx["missing_key"]',
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert "KeyError" in str(data.get("error_type", ""))

    @pytest.mark.asyncio
    async def test_open_forbidden(self, client: AsyncClient):
        """open 被 builtin 限制 -> NameError"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): open('/tmp/x'); return 1",
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert "NameError" in str(data.get("error_type", ""))

    @pytest.mark.asyncio
    async def test_eval_forbidden(self, client: AsyncClient):
        """eval 被 builtin 限制 -> NameError"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "def main(ctx): return eval('1+1')",
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert "NameError" in str(data.get("error_type", ""))

    @pytest.mark.asyncio
    async def test_main_not_callable(self, client: AsyncClient):
        """main 不是可调用对象"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": "main = 123",
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert "callable" in data.get("error_message", "").lower()


class TestFunctionExamplesSubprocess:
    """Subprocess 模式下的行为"""

    @pytest.mark.asyncio
    async def test_numpy_triggers_subprocess_if_installed(self, client: AsyncClient):
        """import numpy 会触发 subprocess；numpy 已安装则成功，未安装则失败"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": """
import numpy as np
def main(ctx):
    return float(np.sum([1, 2, 3]))
""",
                "context": {},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        if data["success"]:
            assert data["result"] == 6.0
            assert data.get("executor_used") == "subprocess"
        else:
            assert "error_type" in data  # ImportError 等

    @pytest.mark.asyncio
    async def test_subprocess_no_runtime_api(self, client: AsyncClient):
        """强制 subprocess 模式下 get_object 不可用 -> NameError"""
        resp = await client.post(
            "/api/v1/execute/code/test",
            json={
                "code_content": 'def main(ctx): return get_object("some-id")',
                "context": {},
                "executor_type": "subprocess",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert data.get("executor_used") == "subprocess"
        assert "NameError" in str(data.get("error_type", ""))
        assert "get_object" in data.get("error_message", "")
