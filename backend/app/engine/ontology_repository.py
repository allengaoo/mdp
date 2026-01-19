"""
Ontology Repository - 解析对象类型到物理表的映射层
对标 Palantir Foundry 架构，实现动态表解析和属性映射
"""
from typing import Dict, Any, Optional, List, Tuple
from sqlmodel import Session, select, text
from sqlalchemy import inspect

from app.core.logger import logger


class OntologyRepository:
    """
    本体仓库 - 负责解析对象类型到物理存储的映射
    
    核心功能:
    1. 解析 object_type_id → 物理表名
    2. 获取属性到列的映射关系
    3. 序列化 JSON properties → 物理列值
    4. 反序列化 物理列值 → JSON properties (通常由视图处理)
    """
    
    def __init__(self, session: Session):
        self.session = session
        self._table_cache: Dict[str, str] = {}  # object_type_id -> table_name
        self._mapping_cache: Dict[str, Dict[str, str]] = {}  # object_type_id -> {api_name: column_name}
    
    def resolve_physical_table(self, object_type_id: str) -> Optional[str]:
        """
        解析对象类型到物理表名
        
        Args:
            object_type_id: 对象类型ID (如 'obj-fighter')
            
        Returns:
            物理表名 (如 'data_fighter') 或 None
        """
        # 检查缓存
        if object_type_id in self._table_cache:
            return self._table_cache[object_type_id]
        
        try:
            # 查询: ont_object_type -> sys_dataset -> storage_location
            query = text("""
                SELECT ds.storage_location
                FROM ont_object_type ot
                JOIN sys_dataset ds ON ot.backing_dataset_id = ds.id
                WHERE ot.id = :object_type_id
            """)
            
            result = self.session.execute(query, {"object_type_id": object_type_id})
            row = result.fetchone()
            
            if row:
                table_name = row[0]
                self._table_cache[object_type_id] = table_name
                logger.debug(f"Resolved {object_type_id} -> {table_name}")
                return table_name
            else:
                logger.warning(f"Object type not found or has no backing dataset: {object_type_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error resolving physical table for {object_type_id}: {e}")
            return None
    
    def get_property_mappings(self, object_type_id: str) -> Dict[str, str]:
        """
        获取属性到物理列的映射
        
        Args:
            object_type_id: 对象类型ID
            
        Returns:
            映射字典: { property_api_name: physical_column_name }
            例如: { "callsign": "callsign", "fuel": "fuel" }
        """
        # 检查缓存
        if object_type_id in self._mapping_cache:
            return self._mapping_cache[object_type_id]
        
        try:
            # 查询: ont_object_property -> sys_dataset_column
            query = text("""
                SELECT 
                    op.api_name as property_name,
                    dc.column_name as column_name
                FROM ont_object_property op
                JOIN sys_dataset_column dc ON op.mapped_column_id = dc.id
                WHERE op.object_type_id = :object_type_id
            """)
            
            result = self.session.execute(query, {"object_type_id": object_type_id})
            mappings = {}
            
            for row in result:
                mappings[row[0]] = row[1]
            
            self._mapping_cache[object_type_id] = mappings
            logger.debug(f"Mappings for {object_type_id}: {mappings}")
            return mappings
            
        except Exception as e:
            logger.error(f"Error getting property mappings for {object_type_id}: {e}")
            return {}
    
    def serialize_to_physical_row(
        self, 
        properties: Dict[str, Any], 
        object_type_id: str,
        instance_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        将 JSON properties 序列化为物理表的列值
        
        Args:
            properties: JSON 属性字典 (如 {"callsign": "Ghost-1", "fuel": 90})
            object_type_id: 对象类型ID
            instance_id: 实例ID（如果提供）
            
        Returns:
            物理行数据字典: { column_name: value }
        """
        mappings = self.get_property_mappings(object_type_id)
        physical_row = {}
        
        # 添加 ID（如果提供）
        if instance_id:
            physical_row['id'] = instance_id
        
        # 映射每个属性到物理列
        for prop_name, prop_value in properties.items():
            column_name = mappings.get(prop_name)
            if column_name:
                physical_row[column_name] = prop_value
            else:
                logger.warning(f"Property '{prop_name}' not mapped for {object_type_id}, skipping")
        
        return physical_row
    
    def build_insert_sql(
        self,
        object_type_id: str,
        properties: Dict[str, Any],
        instance_id: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        构建 INSERT SQL 语句
        
        Args:
            object_type_id: 对象类型ID
            properties: JSON 属性
            instance_id: 实例ID
            
        Returns:
            (SQL语句, 参数字典)
        """
        table_name = self.resolve_physical_table(object_type_id)
        if not table_name:
            raise ValueError(f"Cannot resolve physical table for {object_type_id}")
        
        physical_row = self.serialize_to_physical_row(properties, object_type_id, instance_id)
        
        # 构建 INSERT 语句
        columns = list(physical_row.keys())
        placeholders = [f":{col}" for col in columns]
        
        sql = f"INSERT INTO `{table_name}` (`{'`, `'.join(columns)}`) VALUES ({', '.join(placeholders)})"
        
        return sql, physical_row
    
    def build_update_sql(
        self,
        object_type_id: str,
        instance_id: str,
        properties_patch: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        构建 UPDATE SQL 语句
        
        Args:
            object_type_id: 对象类型ID
            instance_id: 实例ID
            properties_patch: 要更新的属性
            
        Returns:
            (SQL语句, 参数字典)
        """
        table_name = self.resolve_physical_table(object_type_id)
        if not table_name:
            raise ValueError(f"Cannot resolve physical table for {object_type_id}")
        
        physical_row = self.serialize_to_physical_row(properties_patch, object_type_id)
        
        # 移除 ID（不应该在 SET 子句中）
        physical_row.pop('id', None)
        
        if not physical_row:
            raise ValueError("No properties to update")
        
        # 构建 UPDATE 语句
        set_clauses = [f"`{col}` = :{col}" for col in physical_row.keys()]
        sql = f"UPDATE `{table_name}` SET {', '.join(set_clauses)} WHERE `id` = :instance_id"
        
        # 添加 instance_id 到参数
        physical_row['instance_id'] = instance_id
        
        return sql, physical_row
    
    def build_delete_sql(
        self,
        object_type_id: str,
        instance_id: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        构建 DELETE SQL 语句
        
        Args:
            object_type_id: 对象类型ID
            instance_id: 实例ID
            
        Returns:
            (SQL语句, 参数字典)
        """
        table_name = self.resolve_physical_table(object_type_id)
        if not table_name:
            raise ValueError(f"Cannot resolve physical table for {object_type_id}")
        
        sql = f"DELETE FROM `{table_name}` WHERE `id` = :instance_id"
        params = {"instance_id": instance_id}
        
        return sql, params
    
    def clear_cache(self):
        """清除缓存（用于测试或重新加载）"""
        self._table_cache.clear()
        self._mapping_cache.clear()
        logger.debug("OntologyRepository cache cleared")

