"""
单元测试: Action Runner 动作执行引擎
测试动作执行和验证逻辑
"""
import pytest
from app.engine.action_runner import execute_action, validate_action


class TestExecuteAction:
    """execute_action 函数测试"""
    
    @pytest.mark.asyncio
    async def test_execute_strike_action(self):
        """应该执行 strike 动作"""
        result = await execute_action(
            action_id="strike_001",
            target_id="target-123",
            parameters={"target_name": "Enemy Base"}
        )
        
        assert result["success"] is True
        assert result["action_id"] == "strike_001"
        assert result["target"] == "Enemy Base"
        assert result["damage"] == 100
        assert "Strike executed" in result["message"]
    
    @pytest.mark.asyncio
    async def test_execute_strike_action_default_target(self):
        """没有目标名称时应该使用默认值"""
        result = await execute_action(
            action_id="strike_002",
            parameters={}
        )
        
        assert result["success"] is True
        assert result["target"] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_execute_refuel_action(self):
        """应该执行 refuel 动作"""
        result = await execute_action(
            action_id="refuel_001",
            parameters={
                "fighter_id": "F-16-001",
                "fuel_amount": 500
            }
        )
        
        assert result["success"] is True
        assert result["action_id"] == "refuel_001"
        assert result["fighter_id"] == "F-16-001"
        assert result["fuel_added"] == 500
        assert "Refueled" in result["message"]
    
    @pytest.mark.asyncio
    async def test_execute_refuel_action_default_values(self):
        """refuel 动作应该有默认值"""
        result = await execute_action(
            action_id="refuel_002"
        )
        
        assert result["success"] is True
        assert result["fighter_id"] == "Unknown"
        assert result["fuel_added"] == 0
    
    @pytest.mark.asyncio
    async def test_execute_unknown_action(self):
        """未知动作应该返回失败"""
        result = await execute_action(
            action_id="unknown_action",
            parameters={"key": "value"}
        )
        
        assert result["success"] is False
        assert "Unknown action type" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_action_without_parameters(self):
        """应该处理没有参数的情况"""
        result = await execute_action(
            action_id="strike_test",
            target_id=None,
            parameters=None
        )
        
        assert result["success"] is True
        assert result["target"] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_execute_action_with_target_id(self):
        """应该处理带 target_id 的请求"""
        result = await execute_action(
            action_id="strike_with_target",
            target_id="obj-target-001",
            parameters={"target_name": "Target Object"}
        )
        
        assert result["success"] is True


class TestValidateAction:
    """validate_action 函数测试"""
    
    @pytest.mark.asyncio
    async def test_validate_valid_action(self):
        """应该验证有效的动作"""
        is_valid = await validate_action(
            action_id="strike_001",
            parameters={"target": "enemy"}
        )
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_action_without_parameters(self):
        """应该验证没有参数的动作"""
        is_valid = await validate_action(
            action_id="simple_action"
        )
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_empty_action_id(self):
        """空的 action_id 应该验证失败"""
        is_valid = await validate_action(
            action_id="",
            parameters={}
        )
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_validate_none_action_id(self):
        """None action_id 应该验证失败"""
        is_valid = await validate_action(
            action_id=None,
            parameters={}
        )
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_validate_action_with_complex_parameters(self):
        """应该验证带复杂参数的动作"""
        is_valid = await validate_action(
            action_id="complex_action",
            parameters={
                "nested": {"key": "value"},
                "list": [1, 2, 3],
                "number": 42,
                "boolean": True
            }
        )
        
        assert is_valid is True


class TestActionRunnerIntegration:
    """动作执行器集成测试"""
    
    @pytest.mark.asyncio
    async def test_validate_then_execute(self):
        """应该先验证再执行"""
        action_id = "strike_integration"
        params = {"target_name": "Test Target"}
        
        # 先验证
        is_valid = await validate_action(action_id, params)
        assert is_valid is True
        
        # 再执行
        result = await execute_action(action_id, parameters=params)
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_invalid_action_should_fail_validation(self):
        """无效动作应该验证失败"""
        is_valid = await validate_action("", {})
        assert is_valid is False
        
        # 如果验证失败，不应该执行
        # (在实际应用中，验证失败后不会调用 execute_action)
    
    @pytest.mark.asyncio
    async def test_multiple_action_executions(self):
        """应该支持多次动作执行"""
        # 执行第一个动作
        result1 = await execute_action(
            "strike_1",
            parameters={"target_name": "Target 1"}
        )
        
        # 执行第二个动作
        result2 = await execute_action(
            "strike_2",
            parameters={"target_name": "Target 2"}
        )
        
        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["target"] == "Target 1"
        assert result2["target"] == "Target 2"
