"""
Test Script: Index sample objects and test search
MDP Platform V3.1 - Global Search Module
"""
import sys
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv()

# Sample objects for testing
SAMPLE_OBJECTS = [
    {
        "id": "obj-001",
        "object_type": "target",
        "object_type_display": "目标",
        "display_name": "敌方雷达站 Alpha",
        "properties": {
            "status_kwd": "ACTIVE",
            "threat_level_kwd": "HIGH",
            "description_txt": "位于北部山区的雷达监测站，具有远程预警能力",
            "type_kwd": "RADAR"
        }
    },
    {
        "id": "obj-002",
        "object_type": "target",
        "object_type_display": "目标",
        "display_name": "导弹发射基地 Beta",
        "properties": {
            "status_kwd": "ACTIVE",
            "threat_level_kwd": "CRITICAL",
            "description_txt": "战略导弹发射设施，需要密切监控",
            "type_kwd": "MISSILE_BASE"
        }
    },
    {
        "id": "obj-003",
        "object_type": "vessel",
        "object_type_display": "舰船",
        "display_name": "货轮 东方之星",
        "properties": {
            "status_kwd": "ACTIVE",
            "flag_kwd": "CN",
            "description_txt": "大型集装箱货轮，载重量5万吨",
            "vessel_type_kwd": "CARGO"
        }
    },
    {
        "id": "obj-004",
        "object_type": "vessel",
        "object_type_display": "舰船",
        "display_name": "驱逐舰 DDG-52",
        "properties": {
            "status_kwd": "PATROL",
            "flag_kwd": "US",
            "description_txt": "阿利伯克级驱逐舰，正在进行巡逻任务",
            "vessel_type_kwd": "DESTROYER"
        }
    },
    {
        "id": "obj-005",
        "object_type": "intel_report",
        "object_type_display": "情报报告",
        "display_name": "卫星图像分析报告 #2024-001",
        "properties": {
            "classification_kwd": "SECRET",
            "source_kwd": "SATELLITE",
            "content_txt": "根据最新卫星图像分析，目标区域发现异常活动，建议提高警戒等级",
            "status_kwd": "PENDING_REVIEW"
        }
    }
]


def index_sample_objects():
    """Index sample objects using the ES bulk API."""
    from app.core.elastic_store import bulk_index_objects, ensure_objects_index
    
    print("Ensuring index exists...")
    ensure_objects_index()
    
    print(f"Indexing {len(SAMPLE_OBJECTS)} sample objects...")
    count = bulk_index_objects(SAMPLE_OBJECTS)
    print(f"Indexed {count} objects successfully")
    return count


def test_search(query: str):
    """Test search using internal module."""
    from app.core.elastic_store import search_objects
    
    print(f"\n=== Testing search: '{query}' ===")
    
    result = search_objects(query_text=query, size=10)
    
    print(f"Total results: {result['total']}")
    print(f"Aggregations: {list(result['aggregations'].keys())}")
    
    for hit in result['hits']:
        print(f"  - [{hit.get('object_type', 'N/A')}] {hit.get('display_name', 'N/A')} (score: {hit.get('score', 0):.2f})")
        if hit.get('highlights'):
            for field, highlights in hit['highlights'].items():
                if highlights:
                    print(f"    Highlight ({field}): {highlights[0][:80]}...")


def test_facets():
    """Test facets using internal module."""
    from app.core.elastic_store import get_object_facets
    
    print("\n=== Testing facets ===")
    
    field_names = ["object_type", "properties.status_kwd", "properties.type_kwd"]
    facets = get_object_facets(field_names)
    
    for field, buckets in facets.items():
        print(f"  {field}:")
        for bucket in buckets[:5]:
            print(f"    - {bucket['key']}: {bucket['count']}")


if __name__ == "__main__":
    # Index sample data
    index_sample_objects()
    
    import time
    print("\nWaiting for ES to index...")
    time.sleep(2)
    
    # Test searches
    test_search("雷达")
    test_search("导弹")
    test_search("卫星")
    test_search("驱逐舰")
    
    # Test facets
    test_facets()
