#!/usr/bin/env python
"""
Master Seed Script for Integration Testing
MDP Platform V3.1 - Multimodal Data Governance

This script provides a "Clean Slate" approach to set up test data across:
- MySQL (Metadata in ontology_meta_new, Raw data in mdp_raw_store)
- Elasticsearch (mdp_objects index)
- ChromaDB (vector collections)

Usage:
    python scripts/seed_integration_test_data.py

After running, the following pages should show data:
- Global Search (/explore/search)
- Graph Analysis (/explore/graph)  
- Object 360 View (/explore/object360)
"""
import os
import sys
import uuid
import random
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymysql
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# ==========================================
# Configuration
# ==========================================

META_DB_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:Ga0binGB@localhost:3306/ontology_meta_new"
)
RAW_DB_URL = os.getenv(
    "RAW_STORE_DATABASE_URL",
    "mysql+pymysql://root:Ga0binGB@localhost:3306/mdp_raw_store"
)
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "http://127.0.0.1:9200")
ES_OBJECTS_INDEX = os.getenv("ELASTICSEARCH_OBJECTS_INDEX", "mdp_objects")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "data/chroma_vector_store")

# Vector dimension (for mock embeddings)
VECTOR_DIM = 768

# Project ID for testing
PROJECT_ID = "proj-integration-test-001"
PROJECT_NAME = "Maritime Intelligence"

# ==========================================
# Object Type Definitions
# ==========================================

OBJECT_TYPES = [
    {
        "id": "objtype-target-001",
        "api_name": "Target",
        "display_name": "海上目标",
        "stereotype": "ENTITY",
        "description": "Maritime vessel/target tracking data",
        "color": "#1890ff",
        "icon": "AimOutlined",
        "properties": [
            {"api_name": "mmsi", "display_name": "MMSI", "data_type": "STRING", "is_primary_key": True, "is_filterable": True},
            {"api_name": "name", "display_name": "船名", "data_type": "STRING", "is_title": True, "is_searchable": True},
            {"api_name": "vessel_type", "display_name": "船型", "data_type": "STRING", "is_filterable": True},
            {"api_name": "flag", "display_name": "船旗国", "data_type": "STRING", "is_filterable": True},
            {"api_name": "length", "display_name": "船长(m)", "data_type": "DOUBLE", "is_sortable": True},
            {"api_name": "lat", "display_name": "纬度", "data_type": "DOUBLE"},
            {"api_name": "lon", "display_name": "经度", "data_type": "DOUBLE"},
            {"api_name": "speed", "display_name": "航速(节)", "data_type": "DOUBLE", "is_sortable": True},
            {"api_name": "heading", "display_name": "航向", "data_type": "INT"},
            {"api_name": "last_seen", "display_name": "最后发现", "data_type": "DATETIME", "is_sortable": True},
        ]
    },
    {
        "id": "objtype-intel-report-001",
        "api_name": "IntelReport",
        "display_name": "情报报告",
        "stereotype": "DOCUMENT",
        "description": "Intelligence reports and analysis documents",
        "color": "#52c41a",
        "icon": "FileTextOutlined",
        "properties": [
            {"api_name": "report_id", "display_name": "报告编号", "data_type": "STRING", "is_primary_key": True, "is_filterable": True},
            {"api_name": "title", "display_name": "标题", "data_type": "STRING", "is_title": True, "is_searchable": True},
            {"api_name": "content", "display_name": "内容摘要", "data_type": "STRING", "is_searchable": True},
            {"api_name": "classification", "display_name": "密级", "data_type": "STRING", "is_filterable": True},
            {"api_name": "source", "display_name": "来源", "data_type": "STRING", "is_filterable": True},
            {"api_name": "region", "display_name": "区域", "data_type": "STRING", "is_filterable": True},
            {"api_name": "created_at", "display_name": "创建时间", "data_type": "DATETIME", "is_sortable": True},
        ]
    },
    {
        "id": "objtype-recon-image-001",
        "api_name": "ReconImage",
        "display_name": "侦察图像",
        "stereotype": "MEDIA",
        "description": "Reconnaissance and satellite imagery",
        "color": "#722ed1",
        "icon": "CameraOutlined",
        "properties": [
            {"api_name": "image_id", "display_name": "图像ID", "data_type": "STRING", "is_primary_key": True},
            {"api_name": "filename", "display_name": "文件名", "data_type": "STRING", "is_title": True, "is_searchable": True},
            {"api_name": "capture_time", "display_name": "拍摄时间", "data_type": "DATETIME", "is_sortable": True},
            {"api_name": "sensor_type", "display_name": "传感器类型", "data_type": "STRING", "is_filterable": True},
            {"api_name": "resolution", "display_name": "分辨率", "data_type": "STRING", "is_filterable": True},
            {"api_name": "location", "display_name": "位置描述", "data_type": "STRING", "is_searchable": True},
            {"api_name": "file_path", "display_name": "文件路径", "data_type": "STRING"},
        ]
    }
]

# Link types for relationships
LINK_TYPES = [
    {
        "id": "linktype-target-report-001",
        "api_name": "target_mentioned_in_report",
        "display_name": "目标在报告中提及",
        "source_object_def_id": "objtype-target-001",
        "target_object_def_id": "objtype-intel-report-001",
        "cardinality": "MANY_TO_MANY"
    },
    {
        "id": "linktype-target-image-001",
        "api_name": "target_captured_in_image",
        "display_name": "目标在图像中出现",
        "source_object_def_id": "objtype-target-001",
        "target_object_def_id": "objtype-recon-image-001",
        "cardinality": "MANY_TO_MANY"
    },
    {
        "id": "linktype-report-image-001",
        "api_name": "report_references_image",
        "display_name": "报告引用图像",
        "source_object_def_id": "objtype-intel-report-001",
        "target_object_def_id": "objtype-recon-image-001",
        "cardinality": "MANY_TO_MANY"
    }
]

# ==========================================
# Sample Data Generators
# ==========================================

VESSEL_NAMES = [
    "东方之星", "海上勇士", "太平洋探索者", "北极光号", "南海巡航者",
    "Golden Dragon", "Pacific Mariner", "Arctic Explorer", "Blue Horizon", "Ocean Pioneer",
    "远航号", "海鹰", "Storm Rider", "Ocean Queen", "Silver Wave"
]

VESSEL_TYPES = ["货船", "油轮", "集装箱船", "渔船", "客轮", "军舰", "科考船", "拖船"]
FLAGS = ["中国", "巴拿马", "利比里亚", "马绍尔群岛", "新加坡", "日本", "韩国", "美国"]
CLASSIFICATIONS = ["公开", "内部", "秘密", "机密"]
SOURCES = ["AIS监测", "卫星侦察", "人工情报", "开源情报", "技术侦察"]
REGIONS = ["南海", "东海", "黄海", "渤海", "西太平洋", "马六甲海峡", "印度洋"]
SENSOR_TYPES = ["光学卫星", "SAR雷达", "红外传感器", "无人机", "侦察机"]
RESOLUTIONS = ["0.5m", "1m", "3m", "5m", "10m"]


def generate_targets(count: int = 10):
    """Generate sample maritime target data."""
    targets = []
    base_time = datetime.now()
    
    for i in range(count):
        mmsi = f"{random.randint(100000000, 999999999)}"
        targets.append({
            "id": f"target-{str(uuid.uuid4())[:8]}",
            "mmsi": mmsi,
            "name": random.choice(VESSEL_NAMES),
            "vessel_type": random.choice(VESSEL_TYPES),
            "flag": random.choice(FLAGS),
            "length": round(random.uniform(50, 350), 1),
            "lat": round(random.uniform(18, 35), 6),
            "lon": round(random.uniform(105, 130), 6),
            "speed": round(random.uniform(0, 25), 1),
            "heading": random.randint(0, 359),
            "last_seen": (base_time - timedelta(hours=random.randint(0, 72))).isoformat(),
        })
    return targets


def generate_reports(count: int = 5, target_refs: list = None):
    """Generate sample intelligence reports."""
    reports = []
    base_time = datetime.now()
    
    report_templates = [
        ("南海舰队动态分析报告", "本报告分析了近期南海区域的舰船活动模式，发现多艘{vessel_type}频繁出入相关海域。"),
        ("可疑船只跟踪报告", "监测到一艘悬挂{flag}国旗的船只在{region}海域进行非正常活动。"),
        ("海上态势综合评估", "综合各类情报源，对{region}海域当前态势进行全面评估。"),
        ("重点目标监视报告", "对编号为{mmsi}的目标进行持续监视，记录其航行轨迹和停靠港口。"),
        ("异常活动预警通报", "在{region}海域发现异常船舶聚集现象，需要进一步关注。"),
    ]
    
    for i in range(count):
        template = random.choice(report_templates)
        target_ref = random.choice(target_refs) if target_refs else None
        
        content = template[1].format(
            vessel_type=random.choice(VESSEL_TYPES),
            flag=random.choice(FLAGS),
            region=random.choice(REGIONS),
            mmsi=target_ref["mmsi"] if target_ref else "XXXXXXXXX"
        )
        
        reports.append({
            "id": f"report-{str(uuid.uuid4())[:8]}",
            "report_id": f"RPT-{random.randint(2024001, 2024999)}",
            "title": template[0],
            "content": content,
            "classification": random.choice(CLASSIFICATIONS),
            "source": random.choice(SOURCES),
            "region": random.choice(REGIONS),
            "created_at": (base_time - timedelta(days=random.randint(0, 30))).isoformat(),
        })
    return reports


def generate_images(count: int = 5):
    """Generate sample reconnaissance images."""
    images = []
    base_time = datetime.now()
    
    for i in range(count):
        images.append({
            "id": f"image-{str(uuid.uuid4())[:8]}",
            "image_id": f"IMG-{random.randint(100000, 999999)}",
            "filename": f"recon_{random.randint(1000, 9999)}_{random.choice(['opt', 'sar', 'ir'])}.tif",
            "capture_time": (base_time - timedelta(hours=random.randint(0, 168))).isoformat(),
            "sensor_type": random.choice(SENSOR_TYPES),
            "resolution": random.choice(RESOLUTIONS),
            "location": f"{random.choice(REGIONS)} ({round(random.uniform(18, 35), 2)}°N, {round(random.uniform(105, 130), 2)}°E)",
            "file_path": f"/data/imagery/{random.randint(2024, 2026)}/{random.randint(1, 12):02d}/recon_{random.randint(1000, 9999)}.tif",
        })
    return images


def generate_mock_vector():
    """Generate a random mock vector for testing."""
    return [round(random.uniform(-1, 1), 6) for _ in range(VECTOR_DIM)]


# ==========================================
# Database Operations
# ==========================================

def get_mysql_connection(db_url: str):
    """Parse SQLAlchemy URL and return pymysql connection."""
    # Format: mysql+pymysql://user:password@host:port/database
    url = db_url.replace("mysql+pymysql://", "")
    user_pass, host_db = url.split("@")
    user, password = user_pass.split(":")
    host_port, database = host_db.split("/")
    
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 3306
    
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )


def clean_mysql_metadata():
    """Clean metadata tables in ontology_meta_new."""
    print("\n[1/6] Cleaning MySQL Metadata...")
    
    conn = get_mysql_connection(META_DB_URL)
    cursor = conn.cursor()
    
    # Tables to clean (order matters for FK constraints)
    tables_to_clean = [
        "ctx_object_instance_lineage",
        "rel_link_ver_property",
        "rel_object_ver_property",
        "ctx_project_object_binding",
        "sys_link_instance",
        "meta_link_type_ver",
        "meta_link_type_def",
        "meta_object_type_ver",
        "meta_object_type_def",
        "meta_shared_property_def",
        "sys_project",
    ]
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    for table in tables_to_clean:
        try:
            cursor.execute(f"TRUNCATE TABLE `{table}`")
            print(f"  Truncated: {table}")
        except pymysql.Error as e:
            print(f"  Skipped (not exists): {table}")
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    cursor.close()
    conn.close()
    
    print("  MySQL metadata cleaned.")


def clean_mysql_raw_store():
    """Clean raw data tables in mdp_raw_store."""
    print("\n[2/6] Cleaning MySQL Raw Store...")
    
    conn = get_mysql_connection(RAW_DB_URL)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    for table in tables:
        if table.startswith("raw_") or table.startswith("obj_instance_"):
            try:
                cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                print(f"  Dropped: {table}")
            except pymysql.Error as e:
                print(f"  Error dropping {table}: {e}")
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    cursor.close()
    conn.close()
    
    print("  MySQL raw store cleaned.")


def clean_elasticsearch():
    """Delete Elasticsearch indices."""
    print("\n[3/6] Cleaning Elasticsearch...")
    
    try:
        from elasticsearch import Elasticsearch
        
        es = Elasticsearch(hosts=[ES_HOST], verify_certs=False)
        
        # Delete objects index
        if es.indices.exists(index=ES_OBJECTS_INDEX):
            es.indices.delete(index=ES_OBJECTS_INDEX)
            print(f"  Deleted index: {ES_OBJECTS_INDEX}")
        else:
            print(f"  Index not exists: {ES_OBJECTS_INDEX}")
        
        # Also delete text documents index
        if es.indices.exists(index="mdp_text_documents"):
            es.indices.delete(index="mdp_text_documents")
            print(f"  Deleted index: mdp_text_documents")
        
        print("  Elasticsearch cleaned.")
        
    except ImportError:
        print("  WARNING: elasticsearch package not installed, skipping...")
    except Exception as e:
        print(f"  WARNING: ES cleanup failed: {e}")


def clean_chromadb():
    """Delete ChromaDB collections."""
    print("\n[4/6] Cleaning ChromaDB...")
    
    try:
        import chromadb
        import shutil
        
        # Delete the entire ChromaDB directory
        db_path = Path(CHROMA_DB_PATH)
        if db_path.exists():
            shutil.rmtree(db_path)
            print(f"  Deleted: {db_path}")
        else:
            print(f"  Directory not exists: {db_path}")
        
        print("  ChromaDB cleaned.")
        
    except ImportError:
        print("  WARNING: chromadb package not installed, skipping...")
    except Exception as e:
        print(f"  WARNING: ChromaDB cleanup failed: {e}")


def seed_metadata():
    """Seed metadata tables with object types, properties, and link types."""
    print("\n[5/6] Seeding Metadata...")
    
    conn = get_mysql_connection(META_DB_URL)
    cursor = conn.cursor()
    
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Create Project
    cursor.execute("""
        INSERT INTO sys_project (id, name, description, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (PROJECT_ID, PROJECT_NAME, "Integration testing project for maritime intelligence", now, now))
    print(f"  Created project: {PROJECT_NAME}")
    
    # 2. Create Shared Properties (collect all unique properties)
    property_map = {}  # api_name -> id
    
    for obj_type in OBJECT_TYPES:
        for prop in obj_type["properties"]:
            if prop["api_name"] not in property_map:
                prop_id = f"prop-{str(uuid.uuid4())[:8]}"
                property_map[prop["api_name"]] = prop_id
                
                cursor.execute("""
                    INSERT INTO meta_shared_property_def (id, api_name, display_name, data_type, description, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (prop_id, prop["api_name"], prop["display_name"], prop["data_type"], None, now))
    
    print(f"  Created {len(property_map)} shared properties")
    
    # 3. Create Object Type Definitions and Versions
    for obj_type in OBJECT_TYPES:
        obj_def_id = obj_type["id"]
        version_id = f"ver-{str(uuid.uuid4())[:8]}"
        
        # Create definition
        cursor.execute("""
            INSERT INTO meta_object_type_def (id, api_name, stereotype, current_version_id, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (obj_def_id, obj_type["api_name"], obj_type["stereotype"], version_id, now))
        
        # Create version
        cursor.execute("""
            INSERT INTO meta_object_type_ver (id, def_id, version_number, display_name, description, icon, color, status, 
                enable_global_search, enable_geo_index, enable_vector_index, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (version_id, obj_def_id, "1.0", obj_type["display_name"], obj_type["description"],
              obj_type["icon"], obj_type["color"], "PUBLISHED", True, True, True, now))
        
        # Bind properties
        for prop in obj_type["properties"]:
            prop_def_id = property_map[prop["api_name"]]
            cursor.execute("""
                INSERT INTO rel_object_ver_property 
                (object_ver_id, property_def_id, is_primary_key, is_required, is_title, is_searchable, is_filterable, is_sortable)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (version_id, prop_def_id, 
                  prop.get("is_primary_key", False), prop.get("is_required", False), prop.get("is_title", False),
                  prop.get("is_searchable", False), prop.get("is_filterable", False), prop.get("is_sortable", False)))
        
        # Create project binding
        cursor.execute("""
            INSERT INTO ctx_project_object_binding (project_id, object_def_id, used_version_id, is_visible)
            VALUES (%s, %s, %s, %s)
        """, (PROJECT_ID, obj_def_id, version_id, True))
        
        print(f"  Created object type: {obj_type['api_name']} with {len(obj_type['properties'])} properties")
    
    # 4. Create Link Type Definitions and Versions
    for link_type in LINK_TYPES:
        link_def_id = link_type["id"]
        link_ver_id = f"linkver-{str(uuid.uuid4())[:8]}"
        
        # Create definition
        cursor.execute("""
            INSERT INTO meta_link_type_def (id, api_name, current_version_id, created_at)
            VALUES (%s, %s, %s, %s)
        """, (link_def_id, link_type["api_name"], link_ver_id, now))
        
        # Create version
        cursor.execute("""
            INSERT INTO meta_link_type_ver (id, def_id, version_number, display_name, 
                source_object_def_id, target_object_def_id, cardinality, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (link_ver_id, link_def_id, "1.0", link_type["display_name"],
              link_type["source_object_def_id"], link_type["target_object_def_id"],
              link_type["cardinality"], "PUBLISHED", now))
        
        print(f"  Created link type: {link_type['api_name']}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("  Metadata seeded.")


def seed_raw_data_and_index():
    """Seed raw data and index to ES/ChromaDB."""
    print("\n[6/6] Seeding Raw Data & Indexing...")
    
    # Generate test data
    targets = generate_targets(count=10)
    reports = generate_reports(count=5, target_refs=targets)
    images = generate_images(count=5)
    
    print(f"  Generated: {len(targets)} targets, {len(reports)} reports, {len(images)} images")
    
    # Store to MySQL raw store
    _store_raw_data(targets, reports, images)
    
    # Index to Elasticsearch
    _index_to_elasticsearch(targets, reports, images)
    
    # Index to ChromaDB
    _index_to_chromadb(targets, reports, images)
    
    # Create link instances
    _create_link_instances(targets, reports, images)
    
    print("  Raw data seeded and indexed.")


def _store_raw_data(targets, reports, images):
    """Store raw data to MySQL raw store."""
    engine = create_engine(RAW_DB_URL)
    
    # Create and populate targets table
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS raw_targets (
                id VARCHAR(36) PRIMARY KEY,
                mmsi VARCHAR(20),
                name VARCHAR(100),
                vessel_type VARCHAR(50),
                flag VARCHAR(50),
                length DOUBLE,
                lat DOUBLE,
                lon DOUBLE,
                speed DOUBLE,
                heading INT,
                last_seen DATETIME,
                _sync_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
        
        for t in targets:
            conn.execute(text("""
                INSERT INTO raw_targets (id, mmsi, name, vessel_type, flag, length, lat, lon, speed, heading, last_seen)
                VALUES (:id, :mmsi, :name, :vessel_type, :flag, :length, :lat, :lon, :speed, :heading, :last_seen)
            """), t)
        conn.commit()
        
        # Create and populate reports table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS raw_intel_reports (
                id VARCHAR(36) PRIMARY KEY,
                report_id VARCHAR(50),
                title VARCHAR(200),
                content TEXT,
                classification VARCHAR(20),
                source VARCHAR(50),
                region VARCHAR(50),
                created_at DATETIME,
                _sync_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
        
        for r in reports:
            conn.execute(text("""
                INSERT INTO raw_intel_reports (id, report_id, title, content, classification, source, region, created_at)
                VALUES (:id, :report_id, :title, :content, :classification, :source, :region, :created_at)
            """), r)
        conn.commit()
        
        # Create and populate images table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS raw_recon_images (
                id VARCHAR(36) PRIMARY KEY,
                image_id VARCHAR(50),
                filename VARCHAR(200),
                capture_time DATETIME,
                sensor_type VARCHAR(50),
                resolution VARCHAR(20),
                location VARCHAR(200),
                file_path VARCHAR(500),
                _sync_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
        
        for img in images:
            conn.execute(text("""
                INSERT INTO raw_recon_images (id, image_id, filename, capture_time, sensor_type, resolution, location, file_path)
                VALUES (:id, :image_id, :filename, :capture_time, :sensor_type, :resolution, :location, :file_path)
            """), img)
        conn.commit()
    
    engine.dispose()
    print(f"    Stored raw data to MySQL")


def _index_to_elasticsearch(targets, reports, images):
    """Index data to Elasticsearch."""
    try:
        from elasticsearch import Elasticsearch
        from elasticsearch.helpers import bulk
        
        es = Elasticsearch(hosts=[ES_HOST], verify_certs=False)
        
        # Create index with mappings
        if not es.indices.exists(index=ES_OBJECTS_INDEX):
            index_config = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "analysis": {
                        "analyzer": {
                            "text_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": ["lowercase", "asciifolding"]
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "object_type": {"type": "keyword"},
                        "object_type_display": {"type": "keyword"},
                        "display_name": {
                            "type": "text",
                            "analyzer": "text_analyzer",
                            "fields": {"keyword": {"type": "keyword"}}
                        },
                        "properties": {"type": "object", "dynamic": True},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"},
                        "project_id": {"type": "keyword"},
                        # Dynamic templates for typed fields
                        "vessel_type_kwd": {"type": "keyword"},
                        "flag_kwd": {"type": "keyword"},
                        "classification_kwd": {"type": "keyword"},
                        "source_kwd": {"type": "keyword"},
                        "region_kwd": {"type": "keyword"},
                        "sensor_type_kwd": {"type": "keyword"},
                        "content_txt": {"type": "text", "analyzer": "text_analyzer"},
                        "name_txt": {"type": "text", "analyzer": "text_analyzer"},
                    }
                }
            }
            es.indices.create(index=ES_OBJECTS_INDEX, body=index_config)
        
        now = datetime.utcnow().isoformat()
        
        # Build bulk actions
        actions = []
        
        # Index targets
        for t in targets:
            actions.append({
                "_index": ES_OBJECTS_INDEX,
                "_id": t["id"],
                "_source": {
                    "id": t["id"],
                    "object_type": "Target",
                    "object_type_display": "海上目标",
                    "display_name": t["name"],
                    "properties": t,
                    "project_id": PROJECT_ID,
                    "created_at": now,
                    "updated_at": now,
                    # Typed fields for facets
                    "vessel_type_kwd": t["vessel_type"],
                    "flag_kwd": t["flag"],
                    "name_txt": t["name"],
                }
            })
        
        # Index reports
        for r in reports:
            actions.append({
                "_index": ES_OBJECTS_INDEX,
                "_id": r["id"],
                "_source": {
                    "id": r["id"],
                    "object_type": "IntelReport",
                    "object_type_display": "情报报告",
                    "display_name": r["title"],
                    "properties": r,
                    "project_id": PROJECT_ID,
                    "created_at": now,
                    "updated_at": now,
                    # Typed fields for facets
                    "classification_kwd": r["classification"],
                    "source_kwd": r["source"],
                    "region_kwd": r["region"],
                    "content_txt": r["content"],
                }
            })
        
        # Index images
        for img in images:
            actions.append({
                "_index": ES_OBJECTS_INDEX,
                "_id": img["id"],
                "_source": {
                    "id": img["id"],
                    "object_type": "ReconImage",
                    "object_type_display": "侦察图像",
                    "display_name": img["filename"],
                    "properties": img,
                    "project_id": PROJECT_ID,
                    "created_at": now,
                    "updated_at": now,
                    # Typed fields for facets
                    "sensor_type_kwd": img["sensor_type"],
                }
            })
        
        success, _ = bulk(es, actions, stats_only=True)
        print(f"    Indexed {success} objects to Elasticsearch")
        
    except ImportError:
        print("    WARNING: elasticsearch package not installed, skipping...")
    except Exception as e:
        print(f"    WARNING: ES indexing failed: {e}")


def _index_to_chromadb(targets, reports, images):
    """Index vector embeddings to ChromaDB."""
    try:
        import chromadb
        
        # Create persistent client
        db_path = Path(CHROMA_DB_PATH)
        db_path.mkdir(parents=True, exist_ok=True)
        
        client = chromadb.PersistentClient(path=str(db_path))
        
        # Create collection for each object type and insert vectors
        collections = [
            ("obj_target", targets, "Target"),
            ("obj_intel_report", reports, "IntelReport"),
            ("obj_recon_image", images, "ReconImage"),
        ]
        
        total_vectors = 0
        
        for coll_name, items, obj_type in collections:
            # Get or create collection
            collection = client.get_or_create_collection(
                name=coll_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Prepare data
            ids = [item["id"] for item in items]
            embeddings = [generate_mock_vector() for _ in items]
            metadatas = [{"object_type": obj_type, "display_name": item.get("name", item.get("title", item.get("filename", "")))} for item in items]
            
            # Add vectors
            collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas
            )
            total_vectors += len(ids)
        
        print(f"    Indexed {total_vectors} vectors to ChromaDB")
        
    except ImportError:
        print("    WARNING: chromadb package not installed, skipping...")
    except Exception as e:
        print(f"    WARNING: ChromaDB indexing failed: {e}")


def _create_link_instances(targets, reports, images):
    """Create link instances connecting objects."""
    conn = get_mysql_connection(META_DB_URL)
    cursor = conn.cursor()
    
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    link_count = 0
    
    # Create sys_link_instance table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sys_link_instance (
            id VARCHAR(36) PRIMARY KEY,
            link_type_id VARCHAR(36),
            source_instance_id VARCHAR(36),
            target_instance_id VARCHAR(36),
            properties JSON,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_link_type (link_type_id),
            INDEX idx_source (source_instance_id),
            INDEX idx_target (target_instance_id)
        )
    """)
    conn.commit()
    
    # Link some targets to reports
    for i, target in enumerate(targets[:5]):  # First 5 targets
        report = reports[i % len(reports)]
        link_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO sys_link_instance (id, link_type_id, source_instance_id, target_instance_id, properties, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (link_id, "linktype-target-report-001", target["id"], report["id"], "{}", now))
        link_count += 1
    
    # Link some targets to images
    for i, target in enumerate(targets[3:7]):  # Targets 3-6
        image = images[i % len(images)]
        link_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO sys_link_instance (id, link_type_id, source_instance_id, target_instance_id, properties, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (link_id, "linktype-target-image-001", target["id"], image["id"], "{}", now))
        link_count += 1
    
    # Link some reports to images
    for i, report in enumerate(reports[:3]):
        image = images[i % len(images)]
        link_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO sys_link_instance (id, link_type_id, source_instance_id, target_instance_id, properties, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (link_id, "linktype-report-image-001", report["id"], image["id"], "{}", now))
        link_count += 1
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"    Created {link_count} link instances")


# ==========================================
# Main Entry Point
# ==========================================

def main():
    """Run the complete seed process."""
    print("=" * 60)
    print("MDP Platform - Integration Test Data Seeding")
    print("=" * 60)
    print(f"\nTarget databases:")
    print(f"  - Metadata: {META_DB_URL.split('@')[1] if '@' in META_DB_URL else META_DB_URL}")
    print(f"  - Raw Store: {RAW_DB_URL.split('@')[1] if '@' in RAW_DB_URL else RAW_DB_URL}")
    print(f"  - Elasticsearch: {ES_HOST}")
    print(f"  - ChromaDB: {CHROMA_DB_PATH}")
    
    try:
        # Phase 1: Clean slate
        clean_mysql_metadata()
        clean_mysql_raw_store()
        clean_elasticsearch()
        clean_chromadb()
        
        # Phase 2: Seed data
        seed_metadata()
        seed_raw_data_and_index()
        
        print("\n" + "=" * 60)
        print("Seeding completed successfully!")
        print("=" * 60)
        print("\nYou can now test the following pages:")
        print("  - Global Search: /explore/search")
        print("  - Graph Analysis: /explore/graph")
        print("  - Object 360: /explore/object360/{object_id}")
        print(f"\nProject ID: {PROJECT_ID}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
