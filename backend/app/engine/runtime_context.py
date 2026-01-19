"""
Runtime Context API - 为用户代码提供数据操作接口

提供给用户 Python 代码调用的运行时 API，包括：
- get_object: 获取对象实例
- update_object: 更新对象属性
- create_object: 创建新对象
- delete_object: 删除对象
- get_linked_objects: 获取关联对象
- create_link: 创建关联
- query_objects: 查询对象列表
"""
from typing import Dict, Any, List, Optional, Callable
from sqlmodel import Session

from app.core.logger import logger
from app.engine import instance_crud, meta_crud


class RuntimeContext:
    """
    运行时上下文类 - 封装数据操作 API
    
    为用户代码提供一个安全的、受控的数据库访问接口。
    所有操作都通过 instance_crud 执行，确保数据一致性。
    """
    
    def __init__(self, session: Session, source_context: Optional[Dict[str, Any]] = None):
        """
        初始化运行时上下文
        
        Args:
            session: 数据库会话
            source_context: 源对象上下文（包含触发 action 的对象信息）
        """
        self._session = session
        self._source_context = source_context or {}
        self._execution_log: List[Dict[str, Any]] = []
        
    def _log_operation(self, operation: str, params: Dict[str, Any], result: Any):
        """记录操作日志"""
        self._execution_log.append({
            "operation": operation,
            "params": params,
            "result": result if not isinstance(result, Exception) else str(result)
        })
        
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """获取操作日志"""
        return self._execution_log.copy()

    # ==========================================
    # 对象操作 API
    # ==========================================
    
    def get_object(self, obj_id: str) -> Optional[Dict[str, Any]]:
        """
        获取对象实例
        
        Args:
            obj_id: 对象实例 ID
            
        Returns:
            对象数据字典，包含 id, object_type_id, properties
            如果对象不存在返回 None
            
        Example:
            fighter = ctx.get_object("50000000-0000-0000-0000-000000000001")
            if fighter:
                print(fighter["properties"]["callsign"])
        """
        logger.debug(f"RuntimeContext.get_object: {obj_id}")
        try:
            obj = instance_crud.get_object(self._session, obj_id)
            if obj:
                result = {
                    "id": obj.id,
                    "object_type_id": obj.object_type_id,
                    "properties": obj.properties or {},
                    "created_at": obj.created_at.isoformat() if obj.created_at else None,
                    "updated_at": obj.updated_at.isoformat() if obj.updated_at else None
                }
                self._log_operation("get_object", {"obj_id": obj_id}, result)
                return result
            else:
                self._log_operation("get_object", {"obj_id": obj_id}, None)
                return None
        except Exception as e:
            logger.error(f"RuntimeContext.get_object failed: {e}")
            self._log_operation("get_object", {"obj_id": obj_id}, e)
            raise
    
    def update_object(self, obj_id: str, properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        更新对象属性（增量更新）
        
        Args:
            obj_id: 对象实例 ID
            properties: 要更新的属性字典（与现有属性合并）
            
        Returns:
            更新后的对象数据字典，如果对象不存在返回 None
            
        Example:
            ctx.update_object(fighter_id, {"fuel": 50, "status": "Low Fuel"})
        """
        logger.debug(f"RuntimeContext.update_object: {obj_id}, properties={properties}")
        try:
            obj = instance_crud.update_object(self._session, obj_id, properties)
            if obj:
                result = {
                    "id": obj.id,
                    "object_type_id": obj.object_type_id,
                    "properties": obj.properties or {},
                    "updated_at": obj.updated_at.isoformat() if obj.updated_at else None
                }
                self._log_operation("update_object", {"obj_id": obj_id, "properties": properties}, result)
                return result
            else:
                self._log_operation("update_object", {"obj_id": obj_id, "properties": properties}, None)
                return None
        except Exception as e:
            logger.error(f"RuntimeContext.update_object failed: {e}")
            self._log_operation("update_object", {"obj_id": obj_id, "properties": properties}, e)
            raise
    
    def create_object(self, type_id: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        创建新对象实例
        
        Args:
            type_id: 对象类型 ID（如 "10000000-0000-0000-0000-000000000001"）
            properties: 对象属性字典
            
        Returns:
            创建的对象数据字典
            
        Example:
            new_fighter = ctx.create_object(
                "10000000-0000-0000-0000-000000000001",
                {"callsign": "Phoenix-1", "fuel": 100, "status": "Ready"}
            )
        """
        logger.debug(f"RuntimeContext.create_object: type_id={type_id}, properties={properties}")
        try:
            obj = instance_crud.create_object(self._session, type_id, properties)
            result = {
                "id": obj.id,
                "object_type_id": obj.object_type_id,
                "properties": obj.properties or {},
                "created_at": obj.created_at.isoformat() if obj.created_at else None
            }
            self._log_operation("create_object", {"type_id": type_id, "properties": properties}, result)
            return result
        except Exception as e:
            logger.error(f"RuntimeContext.create_object failed: {e}")
            self._log_operation("create_object", {"type_id": type_id, "properties": properties}, e)
            raise
    
    def delete_object(self, obj_id: str) -> bool:
        """
        删除对象实例
        
        Args:
            obj_id: 对象实例 ID
            
        Returns:
            是否删除成功
            
        Example:
            success = ctx.delete_object(target_id)
        """
        logger.debug(f"RuntimeContext.delete_object: {obj_id}")
        try:
            result = instance_crud.delete_object(self._session, obj_id)
            self._log_operation("delete_object", {"obj_id": obj_id}, result)
            return result
        except Exception as e:
            logger.error(f"RuntimeContext.delete_object failed: {e}")
            self._log_operation("delete_object", {"obj_id": obj_id}, e)
            raise

    # ==========================================
    # 查询操作 API
    # ==========================================
    
    def query_objects(
        self,
        type_id: Optional[str] = None,
        type_api_name: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        查询对象列表
        
        Args:
            type_id: 对象类型 ID（与 type_api_name 二选一）
            type_api_name: 对象类型 API 名称（如 "fighter"）
            filters: 属性过滤条件，如 {"status": "Ready", "fuel": 80}
            limit: 返回数量限制
            
        Returns:
            对象数据字典列表
            
        Example:
            ready_fighters = ctx.query_objects(
                type_api_name="fighter",
                filters={"status": "Ready"},
                limit=10
            )
        """
        logger.debug(f"RuntimeContext.query_objects: type_id={type_id}, type_api_name={type_api_name}, filters={filters}")
        try:
            # 如果提供了 type_api_name，先解析为 type_id
            resolved_type_id = type_id
            if type_api_name and not type_id:
                obj_type = meta_crud.get_object_type_by_name(self._session, type_api_name)
                if obj_type:
                    resolved_type_id = obj_type.id
                else:
                    logger.warning(f"ObjectType not found: {type_api_name}")
                    return []
            
            objects = instance_crud.list_objects(
                self._session,
                type_id=resolved_type_id,
                filter_criteria=filters,
                skip=0,
                limit=limit
            )
            
            result = []
            for obj in objects:
                result.append({
                    "id": obj.id,
                    "object_type_id": obj.object_type_id,
                    "properties": obj.properties or {}
                })
            
            self._log_operation("query_objects", {
                "type_id": resolved_type_id,
                "type_api_name": type_api_name,
                "filters": filters,
                "limit": limit
            }, f"Found {len(result)} objects")
            
            return result
        except Exception as e:
            logger.error(f"RuntimeContext.query_objects failed: {e}")
            self._log_operation("query_objects", {
                "type_id": type_id,
                "type_api_name": type_api_name,
                "filters": filters
            }, e)
            raise

    # ==========================================
    # 关联操作 API
    # ==========================================
    
    def get_linked_objects(
        self,
        obj_id: str,
        link_type_api_name: Optional[str] = None,
        link_type_id: Optional[str] = None,
        direction: str = "outgoing"
    ) -> List[Dict[str, Any]]:
        """
        获取关联对象
        
        Args:
            obj_id: 起始对象 ID
            link_type_api_name: 关联类型 API 名称（如 "participation"）
            link_type_id: 关联类型 ID（与 link_type_api_name 二选一）
            direction: 关联方向，"outgoing"（出边）或 "incoming"（入边）或 "both"
            
        Returns:
            关联的对象数据字典列表
            
        Example:
            # 获取战斗机参与的所有任务
            missions = ctx.get_linked_objects(
                fighter_id,
                link_type_api_name="participation",
                direction="outgoing"
            )
        """
        logger.debug(f"RuntimeContext.get_linked_objects: obj_id={obj_id}, link_type={link_type_api_name or link_type_id}, direction={direction}")
        try:
            # 解析 link_type_id
            resolved_link_type_id = link_type_id
            if link_type_api_name and not link_type_id:
                link_type = meta_crud.get_link_type_by_name(self._session, link_type_api_name)
                if link_type:
                    resolved_link_type_id = link_type.id
            
            # 获取关联
            links = []
            if direction in ("outgoing", "both"):
                links.extend(instance_crud.get_outgoing_links(
                    self._session, obj_id, resolved_link_type_id
                ))
            if direction in ("incoming", "both"):
                links.extend(instance_crud.get_incoming_links(
                    self._session, obj_id, resolved_link_type_id
                ))
            
            # 获取关联对象的详细信息
            result = []
            seen_ids = set()
            for link in links:
                # 确定关联的目标对象 ID
                target_obj_id = link.target_instance_id if direction == "outgoing" else link.source_instance_id
                if direction == "both":
                    target_obj_id = link.target_instance_id if link.source_instance_id == obj_id else link.source_instance_id
                
                if target_obj_id not in seen_ids:
                    seen_ids.add(target_obj_id)
                    target_obj = instance_crud.get_object(self._session, target_obj_id)
                    if target_obj:
                        result.append({
                            "id": target_obj.id,
                            "object_type_id": target_obj.object_type_id,
                            "properties": target_obj.properties or {},
                            "link_id": link.id,
                            "link_properties": link.properties or {}
                        })
            
            self._log_operation("get_linked_objects", {
                "obj_id": obj_id,
                "link_type": link_type_api_name or link_type_id,
                "direction": direction
            }, f"Found {len(result)} linked objects")
            
            return result
        except Exception as e:
            logger.error(f"RuntimeContext.get_linked_objects failed: {e}")
            self._log_operation("get_linked_objects", {
                "obj_id": obj_id,
                "link_type": link_type_api_name or link_type_id
            }, e)
            raise
    
    def create_link(
        self,
        link_type_api_name: Optional[str] = None,
        link_type_id: Optional[str] = None,
        source_id: str = None,
        target_id: str = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建对象关联
        
        Args:
            link_type_api_name: 关联类型 API 名称
            link_type_id: 关联类型 ID
            source_id: 源对象 ID
            target_id: 目标对象 ID
            properties: 关联属性
            
        Returns:
            创建的关联数据字典
            
        Example:
            ctx.create_link(
                link_type_api_name="participation",
                source_id=fighter_id,
                target_id=mission_id
            )
        """
        logger.debug(f"RuntimeContext.create_link: {source_id} -> {target_id}")
        try:
            # 解析 link_type_id
            resolved_link_type_id = link_type_id
            if link_type_api_name and not link_type_id:
                link_type = meta_crud.get_link_type_by_name(self._session, link_type_api_name)
                if link_type:
                    resolved_link_type_id = link_type.id
                else:
                    raise ValueError(f"LinkType not found: {link_type_api_name}")
            
            if not resolved_link_type_id:
                raise ValueError("link_type_id or link_type_api_name is required")
            
            link = instance_crud.create_link(
                self._session,
                resolved_link_type_id,
                source_id,
                target_id,
                properties
            )
            
            result = {
                "id": link.id,
                "link_type_id": link.link_type_id,
                "source_instance_id": link.source_instance_id,
                "target_instance_id": link.target_instance_id,
                "properties": link.properties or {}
            }
            
            self._log_operation("create_link", {
                "link_type": link_type_api_name or link_type_id,
                "source_id": source_id,
                "target_id": target_id
            }, result)
            
            return result
        except Exception as e:
            logger.error(f"RuntimeContext.create_link failed: {e}")
            self._log_operation("create_link", {
                "link_type": link_type_api_name or link_type_id,
                "source_id": source_id,
                "target_id": target_id
            }, e)
            raise
    
    def delete_link(self, link_id: str) -> bool:
        """
        删除关联
        
        Args:
            link_id: 关联 ID
            
        Returns:
            是否删除成功
        """
        logger.debug(f"RuntimeContext.delete_link: {link_id}")
        try:
            result = instance_crud.delete_link(self._session, link_id)
            self._log_operation("delete_link", {"link_id": link_id}, result)
            return result
        except Exception as e:
            logger.error(f"RuntimeContext.delete_link failed: {e}")
            self._log_operation("delete_link", {"link_id": link_id}, e)
            raise

    # ==========================================
    # 辅助方法
    # ==========================================
    
    def get_source(self) -> Dict[str, Any]:
        """
        获取触发 Action 的源对象信息
        
        Returns:
            源对象上下文字典
        """
        return self._source_context.copy()
    
    def get_object_type(self, type_id: Optional[str] = None, api_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取对象类型定义
        
        Args:
            type_id: 类型 ID
            api_name: 类型 API 名称
            
        Returns:
            对象类型定义字典
        """
        try:
            obj_type = None
            if type_id:
                obj_type = meta_crud.get_object_type(self._session, type_id)
            elif api_name:
                obj_type = meta_crud.get_object_type_by_name(self._session, api_name)
            
            if obj_type:
                return {
                    "id": obj_type.id,
                    "api_name": obj_type.api_name,
                    "display_name": obj_type.display_name,
                    "property_schema": obj_type.property_schema
                }
            return None
        except Exception as e:
            logger.error(f"RuntimeContext.get_object_type failed: {e}")
            raise


def build_runtime_api(session: Session, source_context: Optional[Dict[str, Any]] = None) -> Dict[str, Callable]:
    """
    构建运行时 API 字典，供用户代码使用
    
    Args:
        session: 数据库会话
        source_context: 源对象上下文
        
    Returns:
        包含所有运行时 API 函数的字典
        
    Example:
        api = build_runtime_api(session, context)
        globals_dict.update(api)
        exec(user_code, globals_dict, locals_dict)
    """
    ctx = RuntimeContext(session, source_context)
    
    return {
        # 对象操作
        "get_object": ctx.get_object,
        "update_object": ctx.update_object,
        "create_object": ctx.create_object,
        "delete_object": ctx.delete_object,
        "query_objects": ctx.query_objects,
        
        # 关联操作
        "get_linked_objects": ctx.get_linked_objects,
        "create_link": ctx.create_link,
        "delete_link": ctx.delete_link,
        
        # 辅助方法
        "get_source": ctx.get_source,
        "get_object_type": ctx.get_object_type,
        
        # 上下文对象本身（高级用法）
        "_ctx": ctx
    }
