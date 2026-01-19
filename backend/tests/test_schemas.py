"""
单元测试: API Schema 验证
测试 Pydantic 模型的验证逻辑
"""
import pytest
from pydantic import ValidationError
from app.schemas.api_payloads import (
    PropertyDef,
    LinkMappingConfig,
    ActionParamDef,
    ObjectTypeRequest,
    LinkTypeRequest,
    ActionRunRequest,
    ProjectResponse,
)


class TestPropertyDef:
    """PropertyDef 模型测试"""
    
    def test_valid_property_def(self):
        """应该创建有效的属性定义"""
        prop = PropertyDef(
            key="fuel",
            label="燃油",
            type="INTEGER",
            required=True
        )
        assert prop.key == "fuel"
        assert prop.label == "燃油"
        assert prop.type == "INTEGER"
        assert prop.required is True
        assert prop.shared_property_id is None
    
    def test_property_def_with_shared_property(self):
        """应该支持关联共享属性"""
        prop = PropertyDef(
            key="location",
            label="位置",
            type="STRING",
            shared_property_id="sp-123"
        )
        assert prop.shared_property_id == "sp-123"
    
    def test_property_def_default_required(self):
        """required 默认应该为 False"""
        prop = PropertyDef(key="name", label="Name", type="STRING")
        assert prop.required is False
    
    def test_property_def_missing_required_fields(self):
        """缺少必填字段应该报错"""
        with pytest.raises(ValidationError):
            PropertyDef(key="test")  # 缺少 label 和 type


class TestLinkMappingConfig:
    """LinkMappingConfig 模型测试"""
    
    def test_valid_mapping_config(self):
        """应该创建有效的映射配置"""
        config = LinkMappingConfig(
            join_table_id="tbl_link",
            source_fk="source_id",
            target_fk="target_id"
        )
        assert config.join_table_id == "tbl_link"
        assert config.source_fk == "source_id"
        assert config.target_fk == "target_id"
    
    def test_empty_mapping_config(self):
        """应该允许空的映射配置"""
        config = LinkMappingConfig()
        assert config.join_table_id is None
        assert config.source_fk is None
        assert config.target_fk is None
    
    def test_mapping_config_extra_fields(self):
        """应该允许额外字段（向后兼容）"""
        config = LinkMappingConfig(
            join_table_id="tbl_link",
            custom_field="custom_value"
        )
        assert config.join_table_id == "tbl_link"


class TestObjectTypeRequest:
    """ObjectTypeRequest 模型测试"""
    
    def test_valid_object_type_request(self):
        """应该创建有效的对象类型请求"""
        req = ObjectTypeRequest(
            api_name="fighter",
            display_name="战斗机",
            project_id="proj-001",
            property_schema=[
                {"key": "fuel", "label": "燃油", "type": "INTEGER", "required": True}
            ],
            description="战斗机类型"
        )
        assert req.api_name == "fighter"
        assert req.display_name == "战斗机"
        assert req.project_id == "proj-001"
        assert len(req.property_schema) == 1
        assert req.description == "战斗机类型"
    
    def test_object_type_request_minimal(self):
        """应该创建最小的对象类型请求"""
        req = ObjectTypeRequest(
            api_name="unit",
            display_name="Unit"
        )
        assert req.api_name == "unit"
        assert req.display_name == "Unit"
        assert req.project_id is None
        assert req.property_schema == []
        assert req.description is None
    
    def test_object_type_request_missing_api_name(self):
        """缺少 api_name 应该报错"""
        with pytest.raises(ValidationError):
            ObjectTypeRequest(display_name="Test")
    
    def test_object_type_request_missing_display_name(self):
        """缺少 display_name 应该报错"""
        with pytest.raises(ValidationError):
            ObjectTypeRequest(api_name="test")


class TestLinkTypeRequest:
    """LinkTypeRequest 模型测试"""
    
    def test_valid_link_type_request(self):
        """应该创建有效的链接类型请求"""
        req = LinkTypeRequest(
            api_name="belongs_to",
            display_name="属于",
            source_type_id="obj-001",
            target_type_id="obj-002",
            cardinality="MANY_TO_ONE"
        )
        assert req.api_name == "belongs_to"
        assert req.display_name == "属于"
        assert req.source_type_id == "obj-001"
        assert req.target_type_id == "obj-002"
        assert req.cardinality == "MANY_TO_ONE"
    
    def test_link_type_request_with_mapping(self):
        """应该支持映射配置"""
        req = LinkTypeRequest(
            api_name="participation",
            source_type_id="fighter",
            target_type_id="mission",
            cardinality="MANY_TO_MANY",
            mapping_config={"join_table_id": "tbl_link"}
        )
        assert req.mapping_config is not None
        assert req.mapping_config.join_table_id == "tbl_link"
    
    def test_link_type_request_missing_required(self):
        """缺少必填字段应该报错"""
        with pytest.raises(ValidationError):
            LinkTypeRequest(
                api_name="test",
                source_type_id="obj-001"
                # 缺少 target_type_id 和 cardinality
            )


class TestActionRunRequest:
    """ActionRunRequest 模型测试"""
    
    def test_valid_action_run_request(self):
        """应该创建有效的动作执行请求"""
        req = ActionRunRequest(
            action_api_name="strike",
            source_object_id="obj-123",
            params={"weapon": "missile"}
        )
        assert req.action_api_name == "strike"
        assert req.source_object_id == "obj-123"
        assert req.params == {"weapon": "missile"}
    
    def test_action_run_request_backward_compatibility(self):
        """应该支持 source_id 向后兼容"""
        req = ActionRunRequest(
            action_api_name="refuel",
            source_id="obj-456"
        )
        assert req.source_id == "obj-456"
        assert req.source_object_id == "obj-456"
        assert req.effective_source_id == "obj-456"
    
    def test_action_run_request_source_object_id_priority(self):
        """source_object_id 应该优先于 source_id"""
        req = ActionRunRequest(
            action_api_name="test",
            source_object_id="obj-new",
            source_id="obj-old"
        )
        # source_object_id 优先
        assert req.effective_source_id == "obj-new"
    
    def test_action_run_request_minimal(self):
        """应该创建最小的动作执行请求"""
        req = ActionRunRequest(action_api_name="ping")
        assert req.action_api_name == "ping"
        assert req.source_object_id is None
        assert req.source_id is None
        assert req.params == {}
    
    def test_action_run_request_missing_action_name(self):
        """缺少 action_api_name 应该报错"""
        with pytest.raises(ValidationError):
            ActionRunRequest(source_object_id="obj-123")


class TestProjectResponse:
    """ProjectResponse 模型测试"""
    
    def test_valid_project_response(self):
        """应该创建有效的项目响应"""
        resp = ProjectResponse(
            id="proj-001",
            title="Battlefield",
            description="战场系统",
            tags=["军事", "演示"],
            objectCount=10,
            linkCount=5,
            updatedAt="2024-01-15T14:30:00"
        )
        assert resp.id == "proj-001"
        assert resp.title == "Battlefield"
        assert resp.description == "战场系统"
        assert resp.tags == ["军事", "演示"]
        assert resp.objectCount == 10
        assert resp.linkCount == 5
    
    def test_project_response_minimal(self):
        """应该创建最小的项目响应"""
        resp = ProjectResponse(
            id="proj-001",
            title="Test",
            objectCount=0,
            linkCount=0
        )
        assert resp.id == "proj-001"
        assert resp.title == "Test"
        assert resp.description is None
        assert resp.tags == []
        assert resp.updatedAt is None
    
    def test_project_response_missing_required(self):
        """缺少必填字段应该报错"""
        with pytest.raises(ValidationError):
            ProjectResponse(
                id="proj-001",
                title="Test"
                # 缺少 objectCount 和 linkCount
            )
