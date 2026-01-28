"""
测试同步任务元数据验证功能
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:3000/api/v3"

def print_response(title: str, response: requests.Response):
    """打印响应信息"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")


def test_create_sync_job_scenario_1():
    """场景1：创建新同步任务（无映射冲突）"""
    print("\n🔍 测试场景1：创建新同步任务（无映射冲突）")
    
    payload = {
        "connection_id": "test_conn_1",  # 需要替换为实际存在的连接ID
        "name": "Test Sync Job 1",
        "source_config": {"table": "test_table"},
        "target_table": "raw_test_table_1",
        "sync_mode": "FULL_OVERWRITE",
        "is_enabled": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/sync-jobs",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print_response("场景1 - 创建同步任务", response)
        
        if response.status_code == 201:
            data = response.json()
            warnings = data.get("warnings", {})
            print(f"✅ 同步任务创建成功")
            print(f"   任务ID: {data['job']['id']}")
            print(f"   警告信息:")
            print(f"   - 映射存在: {warnings.get('mapping_exists', False)}")
            print(f"   - 表名不匹配: {warnings.get('mapping_table_mismatch', 'None')}")
            print(f"   - 表已存在: {warnings.get('table_exists', False)}")
        else:
            print(f"❌ 创建失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_create_sync_job_scenario_2():
    """场景2：创建同步任务（存在映射但表名不同）"""
    print("\n🔍 测试场景2：创建同步任务（存在映射但表名不同）")
    
    # 首先需要创建一个映射
    print("步骤1: 创建测试映射...")
    mapping_payload = {
        "object_def_id": "test_obj_1",  # 需要替换为实际存在的对象类型ID
        "source_connection_id": "test_conn_1",
        "source_table_name": "raw_old_table",
        "mapping_spec": {
            "nodes": [],
            "edges": []
        }
    }
    
    try:
        mapping_response = requests.post(
            f"{BASE_URL}/mappings",
            json=mapping_payload,
            headers={"Content-Type": "application/json"}
        )
        if mapping_response.status_code == 201:
            print("✅ 测试映射创建成功")
        else:
            print(f"⚠️  映射可能已存在或创建失败: {mapping_response.status_code}")
    except Exception as e:
        print(f"⚠️  创建映射失败（可能已存在）: {e}")
    
    # 然后创建同步任务，使用不同的表名
    print("\n步骤2: 创建同步任务（使用新表名）...")
    payload = {
        "connection_id": "test_conn_1",
        "name": "Test Sync Job 2",
        "source_config": {"table": "test_table"},
        "target_table": "raw_new_table",  # 新表名，与映射中的不同
        "sync_mode": "FULL_OVERWRITE",
        "is_enabled": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/sync-jobs",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print_response("场景2 - 创建同步任务（表名不匹配）", response)
        
        if response.status_code == 201:
            data = response.json()
            warnings = data.get("warnings", {})
            print(f"✅ 同步任务创建成功")
            print(f"   任务ID: {data['job']['id']}")
            print(f"   警告信息:")
            print(f"   - 映射存在: {warnings.get('mapping_exists', False)}")
            print(f"   - 表名不匹配: {warnings.get('mapping_table_mismatch', 'None')}")
            print(f"   - 表已存在: {warnings.get('table_exists', False)}")
            
            if warnings.get("mapping_table_mismatch"):
                print(f"\n⚠️  检测到映射表名不匹配！")
                print(f"   现有映射表名: {warnings['mapping_table_mismatch']}")
                print(f"   新同步任务表名: {payload['target_table']}")
        else:
            print(f"❌ 创建失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_table_existence_check():
    """测试表存在性检查"""
    print("\n🔍 测试场景3：表存在性检查")
    
    # 测试不存在的表
    payload = {
        "connection_id": "test_conn_1",
        "name": "Test Sync Job 3",
        "source_config": {"table": "test_table"},
        "target_table": "raw_nonexistent_table_12345",
        "sync_mode": "FULL_OVERWRITE",
        "is_enabled": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/sync-jobs",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print_response("场景3 - 表存在性检查", response)
        
        if response.status_code == 201:
            data = response.json()
            warnings = data.get("warnings", {})
            print(f"✅ 同步任务创建成功")
            print(f"   表存在性: {warnings.get('table_exists', False)}")
            if not warnings.get('table_exists'):
                print(f"   ℹ️  表不存在（正常，会在首次同步时创建）")
        else:
            print(f"❌ 创建失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_list_connections():
    """列出所有连接，用于获取真实的连接ID"""
    print("\n🔍 获取可用连接...")
    try:
        response = requests.get(f"{BASE_URL}/connectors")
        if response.status_code == 200:
            connections = response.json()
            print(f"✅ 找到 {len(connections)} 个连接")
            if connections:
                print("可用连接ID:")
                for conn in connections[:5]:  # 只显示前5个
                    print(f"   - {conn.get('id', 'N/A')}: {conn.get('name', 'N/A')}")
                return connections[0].get('id') if connections else None
        else:
            print(f"⚠️  获取连接失败: {response.status_code}")
    except Exception as e:
        print(f"⚠️  获取连接失败: {e}")
    return None


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("同步任务元数据验证功能测试")
    print("="*60)
    
    # 检查服务是否运行
    try:
        health_response = requests.get(f"{BASE_URL.replace('/api/v3', '')}/health", timeout=2)
        print(f"✅ 服务运行正常")
    except:
        print(f"❌ 无法连接到服务，请确保后端服务运行在 http://localhost:3000")
        print(f"   启动命令: cd backend && uvicorn app.main:app --reload --port 3000")
        return
    
    # 获取真实连接ID
    real_conn_id = test_list_connections()
    
    if real_conn_id:
        print(f"\n使用连接ID: {real_conn_id}")
        # 更新测试数据中的连接ID
        # 这里可以修改测试函数使用真实ID
    else:
        print(f"\n⚠️  未找到可用连接，测试可能失败")
        print(f"   请先创建至少一个连接器")
    
    # 运行测试
    test_create_sync_job_scenario_1()
    test_create_sync_job_scenario_2()
    test_table_existence_check()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    main()
