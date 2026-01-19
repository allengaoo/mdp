"""
Tests for Code Execution Engine.
测试代码执行引擎的核心功能
"""
import pytest
from sqlmodel import Session

from app.engine.code_executor import (
    execute_code, try_function_code,
    CodeExecutionRequest, CodeExecutionResponse, ExecutorType,
    detect_imports, detect_database_api_usage, choose_executor
)
from app.engine.function_runner import (
    validate_syntax, execute_code_direct, ExecutionResult
)
from app.engine.subprocess_runner import execute_in_subprocess, SubprocessResult


class TestSyntaxValidation:
    """语法验证测试"""
    
    def test_valid_simple_syntax(self):
        """有效的简单语法应该通过验证"""
        code = "def main(ctx): return ctx.get('x', 0) * 2"
        is_valid, error = validate_syntax(code)
        assert is_valid is True
        assert error is None
        print("✅ Valid simple syntax passed")
    
    def test_valid_multiline_syntax(self):
        """有效的多行语法应该通过验证"""
        code = '''
def main(ctx):
    x = ctx.get('x', 0)
    y = ctx.get('y', 0)
    return x + y
'''
        is_valid, error = validate_syntax(code)
        assert is_valid is True
        assert error is None
        print("✅ Valid multiline syntax passed")
    
    def test_invalid_syntax_missing_colon(self):
        """缺少冒号的语法应该返回错误"""
        code = "def main(ctx)  return ctx"
        is_valid, error = validate_syntax(code)
        assert is_valid is False
        assert error is not None
        print(f"✅ Syntax error detected: {error[:50]}...")
    
    def test_invalid_syntax_indentation_error(self):
        """缩进错误应该返回错误"""
        code = '''
def main(ctx):
return ctx
'''
        is_valid, error = validate_syntax(code)
        assert is_valid is False
        print("✅ Indentation error detected")
    
    def test_empty_code(self):
        """空代码应该通过语法验证（但执行时会失败）"""
        is_valid, error = validate_syntax("")
        # 空代码在语法上是有效的
        assert is_valid is True
        print("✅ Empty code syntax validation passed")


class TestCodeExecutionDirect:
    """内置执行器 execute_code_direct 测试"""
    
    def test_simple_addition(self):
        """简单加法运算"""
        code = "def main(ctx): return ctx.get('x', 0) + ctx.get('y', 0)"
        result = execute_code_direct(code, {"x": 10, "y": 20})
        
        assert result.success is True
        assert result.result == 30
        assert result.execution_time_ms >= 0
        print(f"✅ Addition: 10 + 20 = {result.result}")
    
    def test_string_return(self):
        """返回字符串"""
        code = "def main(ctx): return 'Hello, ' + ctx.get('name', 'World')"
        result = execute_code_direct(code, {"name": "Test"})
        
        assert result.success is True
        assert result.result == "Hello, Test"
        print(f"✅ String return: {result.result}")
    
    def test_dict_return(self):
        """返回字典"""
        code = '''
def main(ctx):
    return {"status": "ok", "value": ctx.get("x", 0) * 2}
'''
        result = execute_code_direct(code, {"x": 5})
        
        assert result.success is True
        assert result.result == {"status": "ok", "value": 10}
        print("✅ Dict return passed")
    
    def test_list_return(self):
        """返回列表"""
        code = "def main(ctx): return [1, 2, 3, ctx.get('x', 0)]"
        result = execute_code_direct(code, {"x": 4})
        
        assert result.success is True
        assert result.result == [1, 2, 3, 4]
        print("✅ List return passed")
    
    def test_none_return(self):
        """返回 None"""
        code = "def main(ctx): pass"
        result = execute_code_direct(code, {})
        
        assert result.success is True
        assert result.result is None
        print("✅ None return passed")
    
    def test_print_captured(self):
        """print 输出应该被捕获"""
        code = '''
def main(ctx):
    print("Hello World")
    print("Line 2")
    return 42
'''
        result = execute_code_direct(code, {})
        
        assert result.success is True
        assert result.result == 42
        assert "Hello World" in result.stdout
        assert "Line 2" in result.stdout
        print(f"✅ Captured stdout: {result.stdout.strip()}")
    
    def test_missing_main_function(self):
        """缺少 main 函数应该报错"""
        code = "def other_func(): return 1"
        result = execute_code_direct(code, {})
        
        assert result.success is False
        assert "main" in result.error_message.lower()
        print(f"✅ Missing main detected: {result.error_message}")
    
    def test_main_not_callable(self):
        """main 不是函数应该报错"""
        code = "main = 42"
        result = execute_code_direct(code, {})
        
        assert result.success is False
        print(f"✅ Non-callable main detected: {result.error_message}")
    
    def test_runtime_error_division_by_zero(self):
        """除零错误应该被捕获"""
        code = '''
def main(ctx):
    return 1 / 0
'''
        result = execute_code_direct(code, {})
        
        assert result.success is False
        assert result.error_type == "ZeroDivisionError"
        assert result.traceback is not None
        print("✅ ZeroDivisionError captured")
    
    def test_runtime_error_key_error(self):
        """KeyError 应该被捕获"""
        code = '''
def main(ctx):
    d = {}
    return d["missing_key"]
'''
        result = execute_code_direct(code, {})
        
        assert result.success is False
        assert result.error_type == "KeyError"
        print("✅ KeyError captured")
    
    def test_runtime_error_type_error(self):
        """TypeError 应该被捕获"""
        code = '''
def main(ctx):
    return "string" + 42
'''
        result = execute_code_direct(code, {})
        
        assert result.success is False
        assert result.error_type == "TypeError"
        print("✅ TypeError captured")


class TestStdlibModules:
    """标准库模块可用性测试"""
    
    def test_math_module(self):
        """math 模块应该可用"""
        code = '''
import math
def main(ctx):
    return math.sqrt(16) + math.pi
'''
        result = execute_code_direct(code, {})
        
        assert result.success is True
        assert abs(result.result - (4.0 + 3.141592653589793)) < 0.0001
        print(f"✅ math module works: {result.result}")
    
    def test_json_module(self):
        """json 模块应该可用"""
        code = '''
import json
def main(ctx):
    data = {"a": 1, "b": 2}
    return json.dumps(data)
'''
        result = execute_code_direct(code, {})
        
        assert result.success is True
        assert '"a"' in result.result and '"b"' in result.result
        print("✅ json module works")
    
    def test_datetime_module(self):
        """datetime 模块应该可用"""
        code = '''
import datetime
def main(ctx):
    return datetime.date(2024, 1, 1).isoformat()
'''
        result = execute_code_direct(code, {})
        
        assert result.success is True
        assert result.result == "2024-01-01"
        print("✅ datetime module works")
    
    def test_random_module(self):
        """random 模块应该可用"""
        code = '''
import random
def main(ctx):
    random.seed(42)
    return random.randint(1, 100)
'''
        result = execute_code_direct(code, {})
        
        assert result.success is True
        assert isinstance(result.result, int)
        assert 1 <= result.result <= 100
        print(f"✅ random module works: {result.result}")
    
    def test_re_module(self):
        """re 模块应该可用"""
        code = '''
import re
def main(ctx):
    text = "Hello 123 World 456"
    numbers = re.findall(r"\\d+", text)
    return numbers
'''
        result = execute_code_direct(code, {})
        
        assert result.success is True
        assert result.result == ["123", "456"]
        print("✅ re module works")
    
    def test_collections_module(self):
        """collections 模块应该可用"""
        code = '''
import collections
def main(ctx):
    c = collections.Counter("abracadabra")
    return dict(c)
'''
        result = execute_code_direct(code, {})
        
        assert result.success is True
        assert result.result["a"] == 5
        print("✅ collections module works")


class TestRestrictedBuiltins:
    """受限内置函数测试"""
    
    def test_len_available(self):
        """len 应该可用"""
        code = "def main(ctx): return len([1,2,3,4,5])"
        result = execute_code_direct(code, {})
        assert result.success is True
        assert result.result == 5
        print("✅ len() works")
    
    def test_range_available(self):
        """range 应该可用"""
        code = "def main(ctx): return list(range(5))"
        result = execute_code_direct(code, {})
        assert result.success is True
        assert result.result == [0, 1, 2, 3, 4]
        print("✅ range() works")
    
    def test_enumerate_available(self):
        """enumerate 应该可用"""
        code = "def main(ctx): return list(enumerate(['a','b','c']))"
        result = execute_code_direct(code, {})
        assert result.success is True
        assert result.result == [(0, 'a'), (1, 'b'), (2, 'c')]
        print("✅ enumerate() works")
    
    def test_sorted_available(self):
        """sorted 应该可用"""
        code = "def main(ctx): return sorted([3,1,4,1,5,9,2,6])"
        result = execute_code_direct(code, {})
        assert result.success is True
        assert result.result == [1, 1, 2, 3, 4, 5, 6, 9]
        print("✅ sorted() works")
    
    def test_map_filter_available(self):
        """map 和 filter 应该可用"""
        code = '''
def main(ctx):
    nums = [1, 2, 3, 4, 5]
    doubled = list(map(lambda x: x * 2, nums))
    evens = list(filter(lambda x: x % 2 == 0, doubled))
    return evens
'''
        result = execute_code_direct(code, {})
        assert result.success is True
        assert result.result == [2, 4, 6, 8, 10]
        print("✅ map() and filter() work")


class TestImportDetection:
    """导入检测测试"""
    
    def test_detect_simple_import(self):
        """检测简单 import"""
        code = "import numpy"
        imports = detect_imports(code)
        assert "numpy" in imports
        print("✅ Simple import detected")
    
    def test_detect_from_import(self):
        """检测 from ... import"""
        code = "from pandas import DataFrame"
        imports = detect_imports(code)
        assert "pandas" in imports
        print("✅ From import detected")
    
    def test_detect_multiple_imports(self):
        """检测多个 import"""
        code = '''
import math
import json
from datetime import date
'''
        imports = detect_imports(code)
        assert "math" in imports
        assert "json" in imports
        assert "datetime" in imports
        print(f"✅ Multiple imports detected: {imports}")


class TestDatabaseApiDetection:
    """数据库 API 使用检测测试"""
    
    def test_detect_get_object(self):
        """检测 get_object 调用"""
        code = 'obj = get_object("id-123")'
        assert detect_database_api_usage(code) is True
        print("✅ get_object detected")
    
    def test_detect_update_object(self):
        """检测 update_object 调用"""
        code = 'update_object("id", {"status": "done"})'
        assert detect_database_api_usage(code) is True
        print("✅ update_object detected")
    
    def test_detect_query_objects(self):
        """检测 query_objects 调用"""
        code = 'objs = query_objects(type_api_name="fighter")'
        assert detect_database_api_usage(code) is True
        print("✅ query_objects detected")
    
    def test_no_database_api(self):
        """没有数据库 API 调用"""
        code = 'def main(ctx): return ctx.get("x", 0) * 2'
        assert detect_database_api_usage(code) is False
        print("✅ No database API usage detected correctly")


class TestExecutorSelection:
    """执行器自动选择测试"""
    
    def test_simple_code_uses_builtin(self):
        """简单代码应该使用 builtin 执行器"""
        code = "def main(ctx): return 1"
        executor = choose_executor(code, has_session=False)
        assert executor == ExecutorType.BUILTIN
        print("✅ Simple code uses builtin")
    
    def test_numpy_code_uses_subprocess(self):
        """numpy 代码应该使用 subprocess 执行器"""
        code = "import numpy as np\ndef main(ctx): return 1"
        executor = choose_executor(code, has_session=False)
        assert executor == ExecutorType.SUBPROCESS
        print("✅ numpy code uses subprocess")
    
    def test_pandas_code_uses_subprocess(self):
        """pandas 代码应该使用 subprocess 执行器"""
        code = "import pandas as pd\ndef main(ctx): return 1"
        executor = choose_executor(code, has_session=False)
        assert executor == ExecutorType.SUBPROCESS
        print("✅ pandas code uses subprocess")
    
    def test_db_api_with_session_uses_builtin(self):
        """有 session 的数据库 API 代码应该使用 builtin"""
        code = 'obj = get_object("id")\ndef main(ctx): return 1'
        executor = choose_executor(code, has_session=True)
        assert executor == ExecutorType.BUILTIN
        print("✅ db API with session uses builtin")


class TestCodeExecutionRequest:
    """CodeExecutionRequest 测试"""
    
    def test_execute_with_auto_executor(self):
        """使用 AUTO 执行器"""
        request = CodeExecutionRequest(
            code_content="def main(ctx): return ctx.get('x', 0) * 2",
            context={"x": 5},
            executor_type=ExecutorType.AUTO
        )
        result = execute_code(request)
        
        assert result.success is True
        assert result.result == 10
        assert result.executor_used == "builtin"
        print(f"✅ AUTO executor: result={result.result}, executor={result.executor_used}")
    
    def test_execute_with_builtin_executor(self):
        """强制使用 builtin 执行器"""
        request = CodeExecutionRequest(
            code_content="def main(ctx): return 42",
            context={},
            executor_type=ExecutorType.BUILTIN
        )
        result = execute_code(request)
        
        assert result.success is True
        assert result.result == 42
        assert result.executor_used == "builtin"
        print("✅ Builtin executor forced")
    
    def test_execute_with_subprocess_executor(self):
        """强制使用 subprocess 执行器"""
        request = CodeExecutionRequest(
            code_content="def main(ctx): return ctx.get('x', 0) + 1",
            context={"x": 10},
            executor_type=ExecutorType.SUBPROCESS
        )
        result = execute_code(request)
        
        assert result.success is True
        assert result.result == 11
        assert result.executor_used == "subprocess"
        print("✅ Subprocess executor forced")


class TestSubprocessRunner:
    """subprocess 执行器测试"""
    
    def test_simple_execution(self):
        """简单代码在子进程中执行"""
        result = execute_in_subprocess(
            code_content="def main(ctx): return ctx.get('x', 0) * 2",
            context={"x": 5},
            timeout_seconds=30
        )
        
        assert result.success is True
        assert result.result == 10
        print(f"✅ Subprocess simple execution: {result.result}")
    
    def test_print_captured(self):
        """子进程中的 print 应该被捕获"""
        result = execute_in_subprocess(
            code_content='''
def main(ctx):
    print("Hello from subprocess")
    return 42
''',
            context={},
            timeout_seconds=30
        )
        
        assert result.success is True
        assert result.result == 42
        assert "Hello from subprocess" in result.stdout
        print("✅ Subprocess stdout captured")
    
    def test_timeout(self):
        """超时应该被正确处理"""
        result = execute_in_subprocess(
            code_content='''
import time
def main(ctx):
    time.sleep(10)
    return 1
''',
            context={},
            timeout_seconds=2
        )
        
        assert result.success is False
        assert result.error_type == "TimeoutError"
        print("✅ Subprocess timeout handled")
    
    def test_syntax_error_in_subprocess(self):
        """子进程中的语法错误应该被捕获"""
        result = execute_in_subprocess(
            code_content="def main(ctx)  return 1",
            context={},
            timeout_seconds=30
        )
        
        assert result.success is False
        print("✅ Subprocess syntax error captured")


class TestTestFunctionCode:
    """try_function_code 函数测试"""
    
    def test_simple_test(self):
        """简单测试执行"""
        result = try_function_code(
            code_content="def main(ctx): return ctx.get('value', 0) ** 2",
            context={"value": 4}
        )
        
        assert result.success is True
        assert result.result == 16
        print(f"✅ try_function_code: 4^2 = {result.result}")
    
    def test_test_with_no_context(self):
        """无上下文测试"""
        result = try_function_code(
            code_content="def main(ctx): return 'Hello World'"
        )
        
        assert result.success is True
        assert result.result == "Hello World"
        print("✅ try_function_code with no context")
