"""
CRUD operations for meta models (ObjectType, LinkType, FunctionDefinition, ActionDefinition).
"""
from typing import List, Optional, Dict
from datetime import datetime
import uuid
import json
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError, OperationalError

from app.core.logger import logger
from app.models.meta import (
    Project, ProjectCreate, ProjectRead,
    ObjectType, ObjectTypeCreate, ObjectTypeUpdate, ObjectTypeRead,
    LinkType, LinkTypeCreate, LinkTypeUpdate, LinkTypeRead,
    FunctionDefinition, FunctionDefinitionCreate, FunctionDefinitionUpdate, FunctionDefinitionRead,
    ActionDefinition, ActionDefinitionCreate, ActionDefinitionUpdate, ActionDefinitionRead,
    SharedProperty, SharedPropertyCreate, SharedPropertyUpdate, SharedPropertyRead,
    OntObjectType, OntLinkType,  # 底层表模型
    # V3 DTOs for Actions & Logic page
    ActionDefWithFunction,
    FunctionDefForList,
)
from sqlalchemy import text


# ==========================================
# ObjectType CRUD
# ==========================================

def _check_table_exists(session: Session, table_name: str) -> bool:
    """检查表是否存在（区分表和视图）。"""
    try:
        result = session.exec(text(
            "SELECT TABLE_TYPE FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = :table_name"
        ), params={"table_name": table_name})
        row = result.first()
        return row is not None and row[0] == 'BASE TABLE'
    except Exception:
        return False


def _use_ont_tables(session: Session) -> bool:
    """检查是否应该使用 ont_* 底层表（新架构）。"""
    return _check_table_exists(session, "ont_object_type")


def _parse_json_field(value) -> Optional[Dict]:
    """解析可能是 JSON 字符串或已解析字典的字段。"""
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
    return None


def create_object_type(session: Session, obj_in: ObjectTypeCreate) -> ObjectType:
    """Create a new ObjectType.
    
    如果底层表 ont_object_type 存在，则写入该表；
    否则写入 meta_object_type 表（旧架构）。
    """
    logger.info(f"Creating ObjectType: {obj_in.api_name}")
    
    try:
        obj_data = obj_in.model_dump()
        now = datetime.now()
        obj_id = str(uuid.uuid4())
        
        # 检查是否使用新架构
        if _use_ont_tables(session):
            logger.info("Using new architecture: writing to ont_object_type")
            
            # 新架构需要 backing_dataset_id，如果没有则创建一个虚拟的
            # 先检查是否有对应的 dataset
            dataset_id = f"ds-{obj_in.api_name}"
            
            # 检查 dataset 是否存在，不存在则创建
            existing_ds = session.exec(text(
                "SELECT id FROM sys_dataset WHERE id = :id"
            ), params={"id": dataset_id}).first()
            
            if not existing_ds:
                # 创建虚拟 dataset
                session.exec(text(
                    "INSERT INTO sys_dataset (id, api_name, display_name, storage_type, storage_location) "
                    "VALUES (:id, :api_name, :display_name, 'VIRTUAL', :storage_location)"
                ), params={
                    "id": dataset_id,
                    "api_name": f"dataset_{obj_in.api_name}",
                    "display_name": f"Dataset for {obj_in.display_name}",
                    "storage_location": f"virtual_{obj_in.api_name}"
                })
            
            # 写入 ont_object_type
            session.exec(text(
                "INSERT INTO ont_object_type (id, api_name, display_name, description, backing_dataset_id, created_at) "
                "VALUES (:id, :api_name, :display_name, :description, :backing_dataset_id, :created_at)"
            ), params={
                "id": obj_id,
                "api_name": obj_in.api_name,
                "display_name": obj_in.display_name,
                "description": obj_data.get('description'),
                "backing_dataset_id": dataset_id,
                "created_at": now
            })
            
            session.commit()
            
            # 从视图读取返回（保持兼容）
            result = session.exec(text(
                "SELECT id, api_name, display_name, description, project_id, created_at, updated_at, property_schema "
                "FROM meta_object_type WHERE id = :id"
            ), params={"id": obj_id}).first()
            
            if result:
                return ObjectType(
                    id=result[0],
                    api_name=result[1],
                    display_name=result[2],
                    description=result[3],
                    project_id=result[4],
                    created_at=result[5],
                    updated_at=result[6],
                    property_schema=_parse_json_field(result[7])
                )
        else:
            # 旧架构：直接写入 meta_object_type 表
            logger.info("Using old architecture: writing to meta_object_type")
            if 'created_at' not in obj_data or obj_data['created_at'] is None:
                obj_data['created_at'] = now
            if 'updated_at' not in obj_data or obj_data['updated_at'] is None:
                obj_data['updated_at'] = now
            db_obj = ObjectType(**obj_data)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            logger.info(f"ObjectType created successfully: {obj_in.api_name} (ID: {db_obj.id})")
            return db_obj
            
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create ObjectType {obj_in.api_name}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create ObjectType {obj_in.api_name}: {str(e)}")
        raise


def get_object_type(session: Session, obj_id: str) -> Optional[ObjectType]:
    """Get ObjectType by ID."""
    return session.get(ObjectType, obj_id)


def get_object_type_by_name(session: Session, api_name: str) -> Optional[ObjectType]:
    """Get ObjectType by api_name."""
    statement = select(ObjectType).where(ObjectType.api_name == api_name)
    result = session.exec(statement).first()
    return result


def list_object_types(session: Session, skip: int = 0, limit: int = 100) -> List[ObjectType]:
    """List all ObjectTypes with pagination."""
    statement = select(ObjectType).offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())


def update_object_type(
    session: Session,
    obj_id: str,
    obj_in: ObjectTypeUpdate
) -> Optional[ObjectType]:
    """Update an existing ObjectType.
    
    如果底层表 ont_object_type 存在，则更新该表；
    否则更新 meta_object_type 表（旧架构）。
    """
    logger.info(f"Updating ObjectType: {obj_id}")
    
    try:
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if _use_ont_tables(session):
            logger.info("Using new architecture: updating ont_object_type")
            
            # 检查记录是否存在
            existing = session.exec(text(
                "SELECT id FROM ont_object_type WHERE id = :id"
            ), params={"id": obj_id}).first()
            
            if not existing:
                logger.warning(f"ObjectType not found in ont_object_type: {obj_id}")
                return None
            
            # 构建更新语句
            set_clauses = []
            params = {"id": obj_id}
            
            if 'display_name' in update_data:
                set_clauses.append("display_name = :display_name")
                params["display_name"] = update_data['display_name']
            if 'description' in update_data:
                set_clauses.append("description = :description")
                params["description"] = update_data['description']
            
            if set_clauses:
                sql = f"UPDATE ont_object_type SET {', '.join(set_clauses)} WHERE id = :id"
                session.exec(text(sql), params=params)
                session.commit()
            
            # 从视图读取返回
            result = session.exec(text(
                "SELECT id, api_name, display_name, description, project_id, created_at, updated_at, property_schema "
                "FROM meta_object_type WHERE id = :id"
            ), params={"id": obj_id}).first()
            
            if result:
                logger.info(f"ObjectType updated successfully: {obj_id}")
                return ObjectType(
                    id=result[0],
                    api_name=result[1],
                    display_name=result[2],
                    description=result[3],
                    project_id=result[4],
                    created_at=result[5],
                    updated_at=result[6],
                    property_schema=_parse_json_field(result[7])
                )
            return None
        else:
            # 旧架构
            db_obj = session.get(ObjectType, obj_id)
            if not db_obj:
                logger.warning(f"ObjectType not found: {obj_id}")
                return None
            
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            logger.info(f"ObjectType updated successfully: {obj_id}")
            return db_obj
            
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to update ObjectType {obj_id}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update ObjectType {obj_id}: {str(e)}")
        raise


def delete_object_type(session: Session, obj_id: str) -> bool:
    """Delete ObjectType by ID.
    
    如果底层表 ont_object_type 存在，则从该表删除；
    否则从 meta_object_type 表删除（旧架构）。
    """
    logger.info(f"Deleting ObjectType: {obj_id}")
    
    try:
        if _use_ont_tables(session):
            logger.info("Using new architecture: deleting from ont_object_type")
            
            # 检查记录是否存在
            existing = session.exec(text(
                "SELECT id FROM ont_object_type WHERE id = :id"
            ), params={"id": obj_id}).first()
            
            if not existing:
                logger.warning(f"ObjectType not found in ont_object_type: {obj_id}")
                return False
            
            # 同时删除关联的 dataset
            session.exec(text(
                "DELETE FROM sys_dataset WHERE id = :ds_id"
            ), params={"ds_id": f"ds-{obj_id}"})
            
            # 删除 object type
            session.exec(text(
                "DELETE FROM ont_object_type WHERE id = :id"
            ), params={"id": obj_id})
            
            session.commit()
            logger.info(f"ObjectType deleted successfully: {obj_id}")
            return True
        else:
            db_obj = session.get(ObjectType, obj_id)
            if not db_obj:
                logger.warning(f"ObjectType not found: {obj_id}")
                return False
            
            session.delete(db_obj)
            session.commit()
            logger.info(f"ObjectType deleted successfully: {obj_id}")
            return True
            
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete ObjectType {obj_id}: {str(e)}")
        raise


# ==========================================
# LinkType CRUD
# ==========================================

def _use_ont_link_tables(session: Session) -> bool:
    """检查是否应该使用 ont_link_type 底层表（新架构）。"""
    return _check_table_exists(session, "ont_link_type")


def create_link_type(session: Session, obj_in: LinkTypeCreate) -> LinkType:
    """Create a new LinkType.
    
    如果底层表 ont_link_type 存在，则写入该表；
    否则写入 meta_link_type 表（旧架构）。
    """
    logger.info(f"Creating LinkType: {obj_in.api_name}")
    
    try:
        obj_id = str(uuid.uuid4())
        
        if _use_ont_link_tables(session):
            logger.info("Using new architecture: writing to ont_link_type")
            
            # 写入 ont_link_type（注意字段名映射）
            session.exec(text(
                "INSERT INTO ont_link_type (id, api_name, display_name, source_object_type_id, target_object_type_id, cardinality) "
                "VALUES (:id, :api_name, :display_name, :source_type_id, :target_type_id, :cardinality)"
            ), params={
                "id": obj_id,
                "api_name": obj_in.api_name,
                "display_name": obj_in.display_name,
                "source_type_id": obj_in.source_type_id,
                "target_type_id": obj_in.target_type_id,
                "cardinality": obj_in.cardinality
            })
            
            session.commit()
            
            # 从视图读取返回（保持兼容）
            result = session.exec(text(
                "SELECT id, api_name, display_name, source_type_id, target_type_id, cardinality "
                "FROM meta_link_type WHERE id = :id"
            ), params={"id": obj_id}).first()
            
            if result:
                return LinkType(
                    id=result[0],
                    api_name=result[1],
                    display_name=result[2],
                    source_type_id=result[3],
                    target_type_id=result[4],
                    cardinality=result[5]
                )
        else:
            # 旧架构
            logger.info("Using old architecture: writing to meta_link_type")
            db_obj = LinkType(**obj_in.model_dump())
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            logger.info(f"LinkType created successfully: {obj_in.api_name} (ID: {db_obj.id})")
            return db_obj
            
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create LinkType {obj_in.api_name}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create LinkType {obj_in.api_name}: {str(e)}")
        raise


def get_link_type(session: Session, obj_id: str) -> Optional[LinkType]:
    """Get LinkType by ID."""
    return session.get(LinkType, obj_id)


def list_link_types(session: Session, skip: int = 0, limit: int = 100) -> List[LinkType]:
    """List all LinkTypes with pagination."""
    statement = select(LinkType).offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())


def update_link_type(
    session: Session,
    obj_id: str,
    obj_in: LinkTypeUpdate
) -> Optional[LinkType]:
    """Update an existing LinkType.
    
    如果底层表 ont_link_type 存在，则更新该表；
    否则更新 meta_link_type 表（旧架构）。
    """
    logger.info(f"Updating LinkType: {obj_id}")
    
    try:
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if _use_ont_link_tables(session):
            logger.info("Using new architecture: updating ont_link_type")
            
            # 检查记录是否存在
            existing = session.exec(text(
                "SELECT id FROM ont_link_type WHERE id = :id"
            ), params={"id": obj_id}).first()
            
            if not existing:
                logger.warning(f"LinkType not found in ont_link_type: {obj_id}")
                return None
            
            # 构建更新语句（注意字段名映射）
            set_clauses = []
            params = {"id": obj_id}
            
            if 'display_name' in update_data:
                set_clauses.append("display_name = :display_name")
                params["display_name"] = update_data['display_name']
            if 'source_type_id' in update_data:
                set_clauses.append("source_object_type_id = :source_type_id")
                params["source_type_id"] = update_data['source_type_id']
            if 'target_type_id' in update_data:
                set_clauses.append("target_object_type_id = :target_type_id")
                params["target_type_id"] = update_data['target_type_id']
            if 'cardinality' in update_data:
                set_clauses.append("cardinality = :cardinality")
                params["cardinality"] = update_data['cardinality']
            
            if set_clauses:
                sql = f"UPDATE ont_link_type SET {', '.join(set_clauses)} WHERE id = :id"
                session.exec(text(sql), params=params)
                session.commit()
            
            # 从视图读取返回
            result = session.exec(text(
                "SELECT id, api_name, display_name, source_type_id, target_type_id, cardinality "
                "FROM meta_link_type WHERE id = :id"
            ), params={"id": obj_id}).first()
            
            if result:
                logger.info(f"LinkType updated successfully: {obj_id}")
                return LinkType(
                    id=result[0],
                    api_name=result[1],
                    display_name=result[2],
                    source_type_id=result[3],
                    target_type_id=result[4],
                    cardinality=result[5]
                )
            return None
        else:
            # 旧架构
            db_obj = session.get(LinkType, obj_id)
            if not db_obj:
                logger.warning(f"LinkType not found: {obj_id}")
                return None
            
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            logger.info(f"LinkType updated successfully: {obj_id}")
            return db_obj
            
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to update LinkType {obj_id}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update LinkType {obj_id}: {str(e)}")
        raise


def delete_link_type(session: Session, obj_id: str) -> bool:
    """Delete LinkType by ID.
    
    如果底层表 ont_link_type 存在，则从该表删除；
    否则从 meta_link_type 表删除（旧架构）。
    """
    logger.info(f"Deleting LinkType: {obj_id}")
    
    try:
        if _use_ont_link_tables(session):
            logger.info("Using new architecture: deleting from ont_link_type")
            
            # 检查记录是否存在
            existing = session.exec(text(
                "SELECT id FROM ont_link_type WHERE id = :id"
            ), params={"id": obj_id}).first()
            
            if not existing:
                logger.warning(f"LinkType not found in ont_link_type: {obj_id}")
                return False
            
            # 删除 link type
            session.exec(text(
                "DELETE FROM ont_link_type WHERE id = :id"
            ), params={"id": obj_id})
            
            session.commit()
            logger.info(f"LinkType deleted successfully: {obj_id}")
            return True
        else:
            db_obj = session.get(LinkType, obj_id)
            if not db_obj:
                logger.warning(f"LinkType not found: {obj_id}")
                return False
            
            session.delete(db_obj)
            session.commit()
            logger.info(f"LinkType deleted successfully: {obj_id}")
            return True
            
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete LinkType {obj_id}: {str(e)}")
        raise


# ==========================================
# FunctionDefinition CRUD
# ==========================================

def create_function_definition(session: Session, obj_in: FunctionDefinitionCreate) -> FunctionDefinition:
    """Create a new FunctionDefinition."""
    logger.info(f"Creating FunctionDefinition: {obj_in.api_name}")
    
    try:
        db_obj = FunctionDefinition(**obj_in.model_dump())
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"FunctionDefinition created successfully: {obj_in.api_name} (ID: {db_obj.id})")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create FunctionDefinition {obj_in.api_name}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create FunctionDefinition {obj_in.api_name}: {str(e)}")
        raise


def get_function_definition(session: Session, obj_id: str) -> Optional[FunctionDefinition]:
    """Get FunctionDefinition by ID."""
    return session.get(FunctionDefinition, obj_id)


def list_function_definitions(session: Session, skip: int = 0, limit: int = 100) -> List[FunctionDefinition]:
    """List all FunctionDefinitions with pagination."""
    statement = select(FunctionDefinition).offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())


def update_function_definition(session: Session, obj_id: str, obj_in: FunctionDefinitionUpdate) -> Optional[FunctionDefinition]:
    """Update an existing FunctionDefinition."""
    logger.info(f"Updating FunctionDefinition: {obj_id}")
    
    try:
        db_obj = session.get(FunctionDefinition, obj_id)
        if not db_obj:
            return None
        
        # Update only provided fields
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"FunctionDefinition updated successfully: {obj_id}")
        return db_obj
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update FunctionDefinition {obj_id}: {str(e)}")
        raise


def delete_function_definition(session: Session, obj_id: str) -> bool:
    """Delete FunctionDefinition by ID."""
    logger.info(f"Deleting FunctionDefinition: {obj_id}")
    
    try:
        db_obj = session.get(FunctionDefinition, obj_id)
        if not db_obj:
            logger.warning(f"FunctionDefinition not found: {obj_id}")
            return False
        
        session.delete(db_obj)
        session.commit()
        logger.info(f"FunctionDefinition deleted successfully: {obj_id}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete FunctionDefinition {obj_id}: {str(e)}")
        raise


# ==========================================
# ActionDefinition CRUD
# ==========================================

def create_action_definition(session: Session, obj_in: ActionDefinitionCreate) -> ActionDefinition:
    """Create a new ActionDefinition."""
    logger.info(f"Creating ActionDefinition: {obj_in.api_name}")
    
    try:
        db_obj = ActionDefinition(**obj_in.model_dump())
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"ActionDefinition created successfully: {obj_in.api_name} (ID: {db_obj.id})")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create ActionDefinition {obj_in.api_name}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create ActionDefinition {obj_in.api_name}: {str(e)}")
        raise


def get_action_definition(session: Session, obj_id: str) -> Optional[ActionDefinition]:
    """Get ActionDefinition by ID."""
    return session.get(ActionDefinition, obj_id)


def get_action_definition_by_name(session: Session, api_name: str) -> Optional[ActionDefinition]:
    """Get ActionDefinition by api_name."""
    statement = select(ActionDefinition).where(ActionDefinition.api_name == api_name)
    result = session.exec(statement).first()
    return result


def list_action_definitions(session: Session, skip: int = 0, limit: int = 100) -> List[ActionDefinition]:
    """List all ActionDefinitions with pagination."""
    from sqlalchemy import text
    from sqlalchemy.exc import ProgrammingError
    
    try:
        statement = select(ActionDefinition).offset(skip).limit(limit)
        results = session.exec(statement)
        return list(results.all())
    except ProgrammingError as e:
        # 表不存在，尝试创建
        if "1146" in str(e):
            logger.warning("Table meta_action_def does not exist, creating...")
            
            # 检查 meta_function_def 表是否存在
            check_func_sql = text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = DATABASE() AND table_name = 'meta_function_def'
            """)
            func_exists = session.execute(check_func_sql).scalar()
            
            if not func_exists:
                # 先创建 meta_function_def 表
                create_func_sql = text("""
                    CREATE TABLE IF NOT EXISTS `meta_function_def` (
                      `id` varchar(36) NOT NULL,
                      `api_name` varchar(100) NOT NULL,
                      `display_name` varchar(200) NOT NULL,
                      `code_content` longtext COMMENT 'Python Code Content',
                      `bound_object_type_id` varchar(36) DEFAULT NULL,
                      `description` varchar(500),
                      `input_params_schema` json,
                      `output_type` varchar(50) DEFAULT 'VOID',
                      PRIMARY KEY (`id`),
                      UNIQUE KEY `ix_meta_function_def_api_name` (`api_name`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)
                session.execute(create_func_sql)
                session.commit()
                logger.info("Table meta_function_def created successfully")
            
            # 创建 meta_action_def 表
            create_action_sql = text("""
                CREATE TABLE IF NOT EXISTS `meta_action_def` (
                  `id` varchar(36) NOT NULL,
                  `api_name` varchar(100) NOT NULL,
                  `display_name` varchar(200) NOT NULL,
                  `backing_function_id` varchar(36) NOT NULL,
                  PRIMARY KEY (`id`),
                  UNIQUE KEY `ix_meta_action_def_api_name` (`api_name`),
                  KEY `fk_action_backing_function` (`backing_function_id`),
                  CONSTRAINT `fk_action_backing_function` FOREIGN KEY (`backing_function_id`) REFERENCES `meta_function_def` (`id`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            session.execute(create_action_sql)
            session.commit()
            logger.info("Table meta_action_def created successfully")
            
            # 重试查询
            statement = select(ActionDefinition).offset(skip).limit(limit)
            results = session.exec(statement)
            return list(results.all())
        else:
            raise


def update_action_definition(
    session: Session,
    obj_id: str,
    obj_in: ActionDefinitionUpdate
) -> Optional[ActionDefinition]:
    """Update an existing ActionDefinition."""
    logger.info(f"Updating ActionDefinition: {obj_id}")
    
    try:
        db_obj = session.get(ActionDefinition, obj_id)
        if not db_obj:
            logger.warning(f"ActionDefinition not found: {obj_id}")
            return None
        
        # Update fields if provided
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(db_obj, key, value)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"ActionDefinition updated successfully: {obj_id}")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to update ActionDefinition {obj_id}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update ActionDefinition {obj_id}: {str(e)}")
        raise


def delete_action_definition(session: Session, obj_id: str) -> bool:
    """Delete ActionDefinition by ID."""
    logger.info(f"Deleting ActionDefinition: {obj_id}")
    
    try:
        db_obj = session.get(ActionDefinition, obj_id)
        if not db_obj:
            logger.warning(f"ActionDefinition not found: {obj_id}")
            return False
        
        session.delete(db_obj)
        session.commit()
        logger.info(f"ActionDefinition deleted successfully: {obj_id}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete ActionDefinition {obj_id}: {str(e)}")
        raise


# ==========================================
# SharedProperty CRUD
# ==========================================

def create_shared_property(session: Session, obj_in: SharedPropertyCreate) -> SharedProperty:
    """
    Create a new SharedProperty.
    
    直接写入底层表 ont_shared_property_type（因为  是视图，只读）。
    创建后从视图读取返回以保持兼容性。
    """
    logger.info(f"Creating SharedProperty: {obj_in.api_name}")
    
    from sqlalchemy import text
    
    # 直接写入底层表 ont_shared_property_type
    new_id = str(uuid.uuid4())
    insert_sql = text("""
        INSERT INTO ont_shared_property_type (id, api_name, display_name, data_type, formatter, description, created_at)
        VALUES (:id, :api_name, :display_name, :data_type, :formatter, :description, :created_at)
    """)
    
    try:
        # Set created_at to current time if not provided
        created_at = datetime.now()
        
        session.execute(insert_sql, {
            'id': new_id,
            'api_name': obj_in.api_name,
            'display_name': obj_in.display_name,
            'data_type': obj_in.data_type,
            'formatter': obj_in.formatter,
            'description': obj_in.description,
            'created_at': created_at
        })
        session.commit()
        
        # 从视图读取返回（保持兼容）
        db_obj = get_shared_property(session, new_id)
        if db_obj:
            logger.info(f"SharedProperty created successfully: {obj_in.api_name} (ID: {new_id})")
            return db_obj
        else:
            raise ValueError(f"Failed to retrieve created SharedProperty: {new_id}")
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create SharedProperty {obj_in.api_name}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create SharedProperty {obj_in.api_name}: {str(e)}")
        raise


def get_shared_property(session: Session, obj_id: str) -> Optional[SharedProperty]:
    """Get SharedProperty by ID."""
    from sqlalchemy import text
    
    # 使用原始 SQL 查询，显式指定列名（不包含 project_id）
    query = text("""
        SELECT id, api_name, display_name, data_type, formatter, description, created_at
        FROM meta_shared_property
        WHERE id = :id
    """)
    
    result = session.execute(query, {'id': obj_id})
    row = result.fetchone()
    
    if row:
        return SharedProperty(
            id=row[0],
            api_name=row[1],
            display_name=row[2],
            data_type=row[3],
            formatter=row[4],
            description=row[5],
            created_at=row[6]
        )
    return None


def get_shared_property_by_name(session: Session, api_name: str) -> Optional[SharedProperty]:
    """Get SharedProperty by api_name."""
    from sqlalchemy import text
    
    # 使用原始 SQL 查询，显式指定列名（不包含 project_id）
    query = text("""
        SELECT id, api_name, display_name, data_type, formatter, description, created_at
        FROM meta_shared_property
        WHERE api_name = :api_name
        LIMIT 1
    """)
    
    result = session.execute(query, {'api_name': api_name})
    row = result.fetchone()
    
    if row:
        return SharedProperty(
            id=row[0],
            api_name=row[1],
            display_name=row[2],
            data_type=row[3],
            formatter=row[4],
            description=row[5],
            created_at=row[6]
        )
    return None


def list_shared_properties(
    session: Session,
    skip: int = 0,
    limit: int = 100
) -> List[SharedProperty]:
    """
    List SharedProperties.
    
    查询 meta_shared_property 视图（映射自 ont_shared_property_type 表）。
    使用原始 SQL 查询以避免 SQLModel 的元数据缓存问题。
    """
    from sqlalchemy import text
    
    # 使用原始 SQL 查询，显式指定列名（不包含 project_id）
    query = text("""
        SELECT id, api_name, display_name, data_type, formatter, description, created_at
        FROM meta_shared_property
        LIMIT :limit OFFSET :offset
    """)
    
    result = session.execute(query, {'limit': limit, 'offset': skip})
    rows = result.fetchall()
    
    # 手动构建 SharedProperty 对象
    properties = []
    for row in rows:
        prop = SharedProperty(
            id=row[0],
            api_name=row[1],
            display_name=row[2],
            data_type=row[3],
            formatter=row[4],
            description=row[5],
            created_at=row[6]
        )
        properties.append(prop)
    
    return properties


def update_shared_property(
    session: Session,
    obj_id: str,
    obj_in: SharedPropertyUpdate
) -> Optional[SharedProperty]:
    """
    Update an existing SharedProperty.
    
    直接更新底层表 ont_shared_property_type（因为 meta_shared_property 是视图，只读）。
    更新后从视图读取返回以保持兼容性。
    """
    logger.info(f"Updating SharedProperty: {obj_id}")
    
    from sqlalchemy import text
    
    # 先检查记录是否存在（通过视图）
    db_obj = get_shared_property(session, obj_id)
    if not db_obj:
        logger.warning(f"SharedProperty not found: {obj_id}")
        return None
    
    # 准备更新数据（只更新允许的字段）
    update_data = obj_in.model_dump(exclude_unset=True)
    if not update_data:
        logger.info(f"No fields to update for SharedProperty: {obj_id}")
        return db_obj
    
    # 构建 UPDATE SQL（只更新底层表存在的字段）
    # ont_shared_property_type 表有：id, api_name, display_name, data_type, formatter, description, created_at
    # SharedPropertyUpdate DTO 可能有：display_name, data_type, formatter, description
    update_fields = []
    update_params = {'id': obj_id}
    
    if 'display_name' in update_data and update_data['display_name'] is not None:
        update_fields.append("display_name = :display_name")
        update_params['display_name'] = update_data['display_name']
    
    if 'data_type' in update_data and update_data['data_type'] is not None:
        update_fields.append("data_type = :data_type")
        update_params['data_type'] = update_data['data_type']
    
    if 'formatter' in update_data:
        # formatter 可以是 None，所以不检查 is not None
        update_fields.append("formatter = :formatter")
        update_params['formatter'] = update_data['formatter']
    
    if 'description' in update_data:
        # description 可以是 None，所以不检查 is not None
        update_fields.append("description = :description")
        update_params['description'] = update_data['description']
    
    if not update_fields:
        logger.info(f"No valid fields to update for SharedProperty: {obj_id}")
        return db_obj
    
    # 执行更新
    update_sql = text(f"""
        UPDATE ont_shared_property_type 
        SET {', '.join(update_fields)}
        WHERE id = :id
    """)
    
    try:
        result = session.execute(update_sql, update_params)
        session.commit()
        
        if result.rowcount == 0:
            logger.warning(f"SharedProperty update affected 0 rows: {obj_id}")
            return None
        
        # 从视图读取返回（保持兼容）
        updated_obj = get_shared_property(session, obj_id)
        if updated_obj:
            logger.info(f"SharedProperty updated successfully: {obj_id}")
            return updated_obj
        else:
            raise ValueError(f"Failed to retrieve updated SharedProperty: {obj_id}")
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to update SharedProperty {obj_id}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update SharedProperty {obj_id}: {str(e)}")
        raise


def delete_shared_property(session: Session, obj_id: str) -> bool:
    """
    Delete SharedProperty by ID.
    
    直接从底层表 ont_shared_property_type 删除（因为 meta_shared_property 是视图，只读）。
    """
    logger.info(f"Deleting SharedProperty: {obj_id}")
    
    from sqlalchemy import text
    
    # 先检查记录是否存在（通过视图）
    db_obj = get_shared_property(session, obj_id)
    if not db_obj:
        logger.warning(f"SharedProperty not found: {obj_id}")
        return False
    
    # 直接从底层表删除
    delete_sql = text("""
        DELETE FROM ont_shared_property_type 
        WHERE id = :id
    """)
    
    try:
        result = session.execute(delete_sql, {'id': obj_id})
        session.commit()
        
        if result.rowcount == 0:
            logger.warning(f"SharedProperty delete affected 0 rows: {obj_id}")
            return False
        
        logger.info(f"SharedProperty deleted successfully: {obj_id}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete SharedProperty {obj_id}: {str(e)}")
        raise


# ==========================================
# Project CRUD
# ==========================================

def _is_project_table(session: Session) -> bool:
    """检查 meta_project 是表还是视图。返回 True 表示是表（可写入）。"""
    return _check_table_exists(session, "meta_project")


def create_project(session: Session, obj_in: ProjectCreate) -> Project:
    """Create a new Project."""
    logger.info(f"Creating Project: {obj_in.name}")
    
    try:
        if not _is_project_table(session):
            raise ValueError("meta_project 是视图，不支持创建项目。请先运行 enable_multi_project.sql 脚本。")
        
        obj_data = obj_in.model_dump()
        now = datetime.now()
        if 'created_at' not in obj_data or obj_data.get('created_at') is None:
            obj_data['created_at'] = now
        
        db_obj = Project(**obj_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"Project created successfully: {obj_in.name} (ID: {db_obj.id})")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to create Project {obj_in.name}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create Project {obj_in.name}: {str(e)}")
        raise


def get_project(session: Session, obj_id: str) -> Optional[Project]:
    """Get Project by ID."""
    try:
        return session.get(Project, obj_id)
    except Exception as e:
        logger.warning(f"Failed to get Project {obj_id}: {str(e)}")
        return None


def list_projects(session: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    """List all Projects with pagination."""
    statement = select(Project).offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())


def update_project(
    session: Session,
    obj_id: str,
    obj_in: "ProjectCreate"
) -> Optional[Project]:
    """Update an existing Project."""
    logger.info(f"Updating Project: {obj_id}")
    
    try:
        if not _is_project_table(session):
            raise ValueError("meta_project 是视图，不支持更新项目。请先运行 enable_multi_project.sql 脚本。")
        
        db_obj = session.get(Project, obj_id)
        if not db_obj:
            logger.warning(f"Project not found: {obj_id}")
            return None
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        logger.info(f"Project updated successfully: {obj_id}")
        return db_obj
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Failed to update Project {obj_id}: Integrity error - {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update Project {obj_id}: {str(e)}")
        raise


def delete_project(session: Session, obj_id: str) -> bool:
    """Delete Project by ID."""
    logger.info(f"Deleting Project: {obj_id}")
    
    try:
        if not _is_project_table(session):
            raise ValueError("meta_project 是视图，不支持删除项目。请先运行 enable_multi_project.sql 脚本。")
        
        db_obj = session.get(Project, obj_id)
        if not db_obj:
            logger.warning(f"Project not found: {obj_id}")
            return False
        
        session.delete(db_obj)
        session.commit()
        logger.info(f"Project deleted successfully: {obj_id}")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete Project {obj_id}: {str(e)}")
        raise


def list_projects_with_stats(session: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
    """
    List all Projects with aggregated statistics (objectCount, linkCount).
    Returns a list of dictionaries with project data and counts.
    """
    from sqlmodel import func
    from sqlalchemy import or_
    
    # Get all projects
    projects = list_projects(session, skip=skip, limit=limit)
    
    result = []
    for project in projects:
        # Count object types for this project
        object_count_statement = select(func.count(ObjectType.id)).where(
            ObjectType.project_id == project.id
        )
        object_count = session.exec(object_count_statement).one() or 0
        
        # Count link types for this project
        # Link types don't have project_id directly, so we count links where
        # either source_type_id or target_type_id belongs to this project
        source_type_ids_statement = select(ObjectType.id).where(
            ObjectType.project_id == project.id
        )
        source_type_ids_result = session.exec(source_type_ids_statement).all()
        source_type_ids = list(source_type_ids_result) if source_type_ids_result else []
        
        link_count = 0
        if source_type_ids:
            link_count_statement = select(func.count(LinkType.id)).where(
                or_(
                    LinkType.source_type_id.in_(source_type_ids),
                    LinkType.target_type_id.in_(source_type_ids)
                )
            )
            link_count = session.exec(link_count_statement).one() or 0
        
        result.append({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "tags": [],  # Default empty, can be extended later
            "object_count": object_count,
            "link_count": link_count,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
        })
    
    return result


# ==========================================
# Actions & Logic Page - Extended Queries
# ==========================================

def list_actions_with_functions(
    session: Session,
    skip: int = 0,
    limit: int = 100
) -> List[ActionDefWithFunction]:
    """
    List all actions with resolved function details.
    
    SQL Logic:
    SELECT a.id, a.api_name, a.display_name, a.backing_function_id,
           f.api_name as function_api_name, f.display_name as function_display_name
    FROM meta_action_def a
    LEFT JOIN meta_function_def f ON a.backing_function_id = f.id
    """
    results: List[ActionDefWithFunction] = []
    
    # Get all actions
    actions = list_action_definitions(session, skip=skip, limit=limit)
    
    for action in actions:
        # Resolve function details
        function_api_name = None
        function_display_name = None
        
        if action.backing_function_id:
            func = get_function_definition(session, action.backing_function_id)
            if func:
                function_api_name = func.api_name
                function_display_name = func.display_name
        
        results.append(ActionDefWithFunction(
            id=action.id,
            api_name=action.api_name,
            display_name=action.display_name,
            backing_function_id=action.backing_function_id,
            function_api_name=function_api_name,
            function_display_name=function_display_name,
        ))
    
    return results


def list_functions_for_list(
    session: Session,
    skip: int = 0,
    limit: int = 100
) -> List[FunctionDefForList]:
    """
    List all functions for display in Actions & Logic page.
    
    SQL Logic:
    SELECT id, api_name, display_name, description, output_type, code_content
    FROM meta_function_def
    """
    functions = list_function_definitions(session, skip=skip, limit=limit)
    
    return [
        FunctionDefForList(
            id=func.id,
            api_name=func.api_name,
            display_name=func.display_name,
            description=func.description,
            output_type=func.output_type,
            code_content=func.code_content,
        )
        for func in functions
    ]
