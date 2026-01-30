"""
简单的同步任务创建测试
使用 requests 库测试 API
"""
import sys
import json

try:
    import requests
except ImportError:
    print("❌ 需要安装 requests 库: pip install requests")
    sys.exit(1)

BASE_URL = "http://localhost:3000/api/v3"

def test_create_sync_job():
    """测试创建同步任务"""
    print("=" * 60)
    print("测试创建同步任务 API")
    print("=" * 60)
    
    # 首先获取一个连接ID
    print("\n1. 获取连接列表...")
    try:
        response = requests.get(f"{BASE_URL}/connectors", timeout=5)
        if response.status_code == 200:
            connections = response.json()
            if connections:
                conn_id = connections[0].get('id')
                conn_name = connections[0].get('name', 'N/A')
                print(f"   ✅ 找到连接: {conn_name} (ID: {conn_id})")
            else:
                print("   ⚠️  没有找到连接，使用测试ID")
                conn_id = "test_conn_1"
        else:
            print(f"   ⚠️  获取连接失败，使用测试ID")
            conn_id = "test_conn_1"
    except Exception as e:
        print(f"   ⚠️  无法连接到服务: {e}")
        print("   💡 请确保后端服务运行在 http://localhost:3000")
        return
    
    # 创建同步任务
    print(f"\n2. 创建同步任务...")
    payload = {
        "connection_id": conn_id,
        "name": "测试同步任务",
        "source_config": {"table": "test_table"},
        "target_table": "raw_test_table_123",
        "sync_mode": "FULL_OVERWRITE",
        "is_enabled": True
    }
    
    print(f"   请求数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/sync-jobs",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n   响应状态码: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"\n   ✅ 同步任务创建成功！")
            print(f"\n   响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 解析警告信息
            if "warnings" in data:
                warnings = data["warnings"]
                print(f"\n   📋 警告信息:")
                print(f"      - 映射存在: {warnings.get('mapping_exists', False)}")
                print(f"      - 表名不匹配: {warnings.get('mapping_table_mismatch', 'None')}")
                print(f"      - 表已存在: {warnings.get('table_exists', False)}")
                
                # 检查是否有警告
                if warnings.get('mapping_table_mismatch'):
                    print(f"\n   ⚠️  检测到映射表名不匹配！")
                    print(f"      现有映射表名: {warnings['mapping_table_mismatch']}")
                    print(f"      新同步任务表名: {payload['target_table']}")
                    print(f"      💡 建议：更新映射的表名以匹配新的同步任务")
            
            if "job" in data:
                job = data["job"]
                print(f"\n   📝 任务信息:")
                print(f"      - ID: {job.get('id')}")
                print(f"      - 名称: {job.get('name')}")
                print(f"      - 目标表: {job.get('target_table')}")
                print(f"      - 同步模式: {job.get('sync_mode')}")
        else:
            print(f"\n   ❌ 创建失败")
            try:
                error_data = response.json()
                print(f"   错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   错误信息: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print(f"\n   ❌ 无法连接到服务器")
        print(f"   💡 请确保后端服务运行在 http://localhost:3000")
        print(f"      启动命令: cd backend && uvicorn app.main:app --reload --port 3000")
    except Exception as e:
        print(f"\n   ❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_sync_job()
