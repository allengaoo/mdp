"""
Tests for Runtime Context API.
测试运行时上下文 API - 用户代码数据操作接口
"""
import pytest
from sqlmodel import Session
import uuid

from app.engine.runtime_context import RuntimeContext, build_runtime_api
from app.engine import instance_crud, meta_crud


class TestRuntimeContextInit:
    """RuntimeContext 初始化测试"""
    
    def test_init_without_source_context(self, db_session: Session):
        """无源上下文初始化"""
        ctx = RuntimeContext(db_session)
        
        assert ctx._session == db_session
        assert ctx._source_context == {}
        assert ctx._execution_log == []
    
    def test_init_with_source_context(self, db_session: Session):
        """有源上下文初始化"""
        source = {"object_id": "test-123", "action": "strike"}
        ctx = RuntimeContext(db_session, source_context=source)
        
        assert ctx._source_context == source
    
    def test_get_source(self, db_session: Session):
        """获取源上下文"""
        source = {"object_id": "test-123", "type": "fighter"}
        ctx = RuntimeContext(db_session, source_context=source)
        
        result = ctx.get_source()
        assert result == source
        # 确保返回的是副本
        result["new_key"] = "new_value"
        assert "new_key" not in ctx._source_context


class TestRuntimeContextObjectOperations:
    """RuntimeContext 对象操作测试"""
    
    def test_get_object_not_found(self, db_session: Session):
        """获取不存在的对象应返回 None"""
        ctx = RuntimeContext(db_session)
        result = ctx.get_object("non-existent-id-12345")
        assert result is None
    
    def test_get_object_logs_operation(self, db_session: Session):
        """get_object 应该记录操作日志"""
        ctx = RuntimeContext(db_session)
        ctx.get_object("test-id")
        
        log = ctx.get_execution_log()
        assert len(log) == 1
        assert log[0]["operation"] == "get_object"
        assert log[0]["params"]["obj_id"] == "test-id"
    
    def test_get_object_returns_dict_format(self, db_session: Session):
        """获取对象应返回正确格式的字典"""
        ctx = RuntimeContext(db_session)
        
        # 先获取一个存在的对象类型
        object_types = meta_crud.list_object_types(db_session)
        if object_types:
            # 查询该类型的对象实例
            objects = instance_crud.list_objects(db_session, type_id=object_types[0].id, limit=1)
            if objects:
                obj = objects[0]
                result = ctx.get_object(obj.id)
                
                assert result is not None
                assert "id" in result
                assert "object_type_id" in result
                assert "properties" in result
                assert result["id"] == obj.id
                print(f"✅ Got object: {result['id']}")
            else:
                pytest.skip("No object instances available")
        else:
            pytest.skip("No object types available")
    
    def test_update_object_not_found(self, db_session: Session):
        """更新不存在的对象应返回 None"""
        ctx = RuntimeContext(db_session)
        result = ctx.update_object("non-existent-id", {"key": "value"})
        assert result is None


class TestRuntimeContextQueryOperations:
    """RuntimeContext 查询操作测试"""
    
    def test_query_objects_returns_list(self, db_session: Session):
        """查询对象应返回列表"""
        ctx = RuntimeContext(db_session)
        result = ctx.query_objects(limit=5)
        
        assert isinstance(result, list)
        assert len(result) <= 5
    
    def test_query_objects_by_type_api_name(self, db_session: Session):
        """通过类型 API 名称查询"""
        ctx = RuntimeContext(db_session)
        
        # 获取第一个对象类型的 api_name
        object_types = meta_crud.list_object_types(db_session)
        if object_types:
            api_name = object_types[0].api_name
            result = ctx.query_objects(type_api_name=api_name, limit=10)
            
            assert isinstance(result, list)
            # 验证返回的对象都是该类型
            for obj in result:
                assert obj["object_type_id"] == object_types[0].id
            print(f"✅ Found {len(result)} objects of type {api_name}")
        else:
            pytest.skip("No object types available")
    
    def test_query_objects_unknown_type_returns_empty(self, db_session: Session):
        """查询不存在的类型应返回空列表"""
        ctx = RuntimeContext(db_session)
        result = ctx.query_objects(type_api_name="non_existent_type_12345")
        
        assert result == []
    
    def test_query_objects_logs_operation(self, db_session: Session):
        """query_objects 应该记录操作日志"""
        ctx = RuntimeContext(db_session)
        ctx.query_objects(limit=5)
        
        log = ctx.get_execution_log()
        assert len(log) == 1
        assert log[0]["operation"] == "query_objects"


class TestRuntimeContextLinkOperations:
    """RuntimeContext 关联操作测试"""
    
    @pytest.mark.skip(reason="Requires sys_link_instance table/view which may not exist in all environments")
    def test_get_linked_objects_returns_list(self, db_session: Session):
        """获取关联对象应返回列表"""
        ctx = RuntimeContext(db_session)
        
        # 获取一个存在的对象
        object_types = meta_crud.list_object_types(db_session)
        if object_types:
            objects = instance_crud.list_objects(db_session, type_id=object_types[0].id, limit=1)
            if objects:
                result = ctx.get_linked_objects(objects[0].id)
                assert isinstance(result, list)
                print(f"✅ Found {len(result)} linked objects")
            else:
                pytest.skip("No object instances available")
        else:
            pytest.skip("No object types available")
    
    @pytest.mark.skip(reason="Requires sys_link_instance table/view which may not exist in all environments")
    def test_get_linked_objects_with_direction(self, db_session: Session):
        """获取指定方向的关联对象"""
        ctx = RuntimeContext(db_session)
        
        # 获取一个存在的对象
        object_types = meta_crud.list_object_types(db_session)
        if object_types:
            objects = instance_crud.list_objects(db_session, type_id=object_types[0].id, limit=1)
            if objects:
                obj_id = objects[0].id
                
                # 测试不同方向
                outgoing = ctx.get_linked_objects(obj_id, direction="outgoing")
                incoming = ctx.get_linked_objects(obj_id, direction="incoming")
                both = ctx.get_linked_objects(obj_id, direction="both")
                
                assert isinstance(outgoing, list)
                assert isinstance(incoming, list)
                assert isinstance(both, list)
                print(f"✅ Outgoing: {len(outgoing)}, Incoming: {len(incoming)}, Both: {len(both)}")
            else:
                pytest.skip("No object instances available")
        else:
            pytest.skip("No object types available")


class TestRuntimeContextMetaOperations:
    """RuntimeContext 元数据操作测试"""
    
    def test_get_object_type_by_id(self, db_session: Session):
        """通过 ID 获取对象类型"""
        ctx = RuntimeContext(db_session)
        
        object_types = meta_crud.list_object_types(db_session)
        if object_types:
            type_id = object_types[0].id
            result = ctx.get_object_type(type_id=type_id)
            
            assert result is not None
            assert result["id"] == type_id
            assert "api_name" in result
            assert "display_name" in result
            print(f"✅ Got object type: {result['display_name']}")
        else:
            pytest.skip("No object types available")
    
    def test_get_object_type_by_api_name(self, db_session: Session):
        """通过 API 名称获取对象类型"""
        ctx = RuntimeContext(db_session)
        
        object_types = meta_crud.list_object_types(db_session)
        if object_types:
            api_name = object_types[0].api_name
            result = ctx.get_object_type(api_name=api_name)
            
            assert result is not None
            assert result["api_name"] == api_name
            print(f"✅ Got object type by api_name: {api_name}")
        else:
            pytest.skip("No object types available")
    
    def test_get_object_type_not_found(self, db_session: Session):
        """获取不存在的对象类型应返回 None"""
        ctx = RuntimeContext(db_session)
        result = ctx.get_object_type(api_name="non_existent_type_12345")
        
        assert result is None


class TestBuildRuntimeApi:
    """build_runtime_api 函数测试"""
    
    def test_build_api_returns_dict(self, db_session: Session):
        """应该返回包含所有 API 函数的字典"""
        api = build_runtime_api(db_session)
        
        assert isinstance(api, dict)
        
        # 验证所有对象操作 API 存在
        assert "get_object" in api
        assert "update_object" in api
        assert "create_object" in api
        assert "delete_object" in api
        assert "query_objects" in api
        
        # 验证所有关联操作 API 存在
        assert "get_linked_objects" in api
        assert "create_link" in api
        assert "delete_link" in api
        
        # 验证辅助方法存在
        assert "get_source" in api
        assert "get_object_type" in api
        assert "_ctx" in api
        
        print(f"✅ API dict contains {len(api)} functions")
    
    def test_api_functions_are_callable(self, db_session: Session):
        """API 函数应该是可调用的"""
        api = build_runtime_api(db_session)
        
        assert callable(api["get_object"])
        assert callable(api["update_object"])
        assert callable(api["create_object"])
        assert callable(api["delete_object"])
        assert callable(api["query_objects"])
        assert callable(api["get_linked_objects"])
        assert callable(api["create_link"])
        assert callable(api["delete_link"])
        assert callable(api["get_source"])
        assert callable(api["get_object_type"])
    
    def test_api_with_source_context(self, db_session: Session):
        """带源上下文构建 API"""
        source = {"object_id": "source-123", "action": "test_action"}
        api = build_runtime_api(db_session, source_context=source)
        
        result = api["get_source"]()
        assert result == source
    
    def test_api_get_object_works(self, db_session: Session):
        """API get_object 函数可以工作"""
        api = build_runtime_api(db_session)
        
        # 调用 get_object（即使找不到对象也不应该抛异常）
        result = api["get_object"]("non-existent-id")
        assert result is None
    
    def test_api_query_objects_works(self, db_session: Session):
        """API query_objects 函数可以工作"""
        api = build_runtime_api(db_session)
        
        result = api["query_objects"](limit=5)
        assert isinstance(result, list)


class TestExecutionLog:
    """执行日志测试"""
    
    def test_log_accumulates(self, db_session: Session):
        """日志应该累积"""
        ctx = RuntimeContext(db_session)
        
        ctx.get_object("id-1")
        ctx.get_object("id-2")
        ctx.query_objects(limit=5)
        
        log = ctx.get_execution_log()
        assert len(log) == 3
        assert log[0]["operation"] == "get_object"
        assert log[1]["operation"] == "get_object"
        assert log[2]["operation"] == "query_objects"
    
    def test_log_returns_copy(self, db_session: Session):
        """获取日志应返回副本"""
        ctx = RuntimeContext(db_session)
        ctx.get_object("test-id")
        
        log1 = ctx.get_execution_log()
        log1.append({"fake": "entry"})
        
        log2 = ctx.get_execution_log()
        assert len(log2) == 1  # 原始日志不受影响
    
    def test_log_contains_params_and_result(self, db_session: Session):
        """日志应包含参数和结果"""
        ctx = RuntimeContext(db_session)
        ctx.get_object("test-object-id")
        
        log = ctx.get_execution_log()
        entry = log[0]
        
        assert "operation" in entry
        assert "params" in entry
        assert "result" in entry
        assert entry["params"]["obj_id"] == "test-object-id"


class TestRuntimeContextIntegration:
    """RuntimeContext 集成测试"""
    
    def test_create_and_get_object(self, db_session: Session):
        """创建对象后应该能获取到"""
        ctx = RuntimeContext(db_session)
        
        # 获取一个对象类型
        object_types = meta_crud.list_object_types(db_session)
        if not object_types:
            pytest.skip("No object types available")
        
        type_id = object_types[0].id
        # 使用空属性创建，因为属性列映射可能不存在
        properties = {}
        
        # 创建对象
        created = ctx.create_object(type_id, properties)
        assert created is not None
        assert created["id"] is not None
        
        # 获取对象
        fetched = ctx.get_object(created["id"])
        assert fetched is not None
        assert "id" in fetched
        assert "object_type_id" in fetched
        
        # 清理
        deleted = ctx.delete_object(created["id"])
        assert deleted is True
        
        # 验证已删除
        after_delete = ctx.get_object(created["id"])
        assert after_delete is None
        
        print(f"✅ Create-Get-Delete cycle completed")
    
    def test_update_object_properties(self, db_session: Session):
        """更新对象属性"""
        ctx = RuntimeContext(db_session)
        
        # 获取一个对象类型
        object_types = meta_crud.list_object_types(db_session)
        if not object_types:
            pytest.skip("No object types available")
        
        type_id = object_types[0].id
        
        # 创建对象
        created = ctx.create_object(type_id, {})
        
        # 更新属性 - 注意：只有已映射的属性列才能被更新
        # 这个测试验证更新操作本身能够工作
        updated = ctx.update_object(created["id"], {})
        assert updated is not None
        assert "id" in updated
        assert "properties" in updated
        
        # 清理
        ctx.delete_object(created["id"])
        
        print(f"✅ Update object properties completed")
    
    def test_multiple_operations_log(self, db_session: Session):
        """多个操作的日志记录"""
        ctx = RuntimeContext(db_session)
        
        # 执行多个操作
        ctx.get_object("id-1")
        ctx.query_objects(limit=2)
        ctx.get_object("id-2")
        
        log = ctx.get_execution_log()
        
        assert len(log) == 3
        assert log[0]["operation"] == "get_object"
        assert log[1]["operation"] == "query_objects"
        assert log[2]["operation"] == "get_object"
        
        print(f"✅ Multiple operations logged correctly")
