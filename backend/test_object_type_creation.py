"""
Test script for object type creation with project binding
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_create_object_type_with_project():
    print("=" * 60)
    print("Testing Object Type Creation with Project Binding")
    print("=" * 60)
    
    # 1. Get a project ID (use first project)
    print("\n1. Getting projects...")
    r = requests.get(f"{BASE_URL}/v3/projects")
    if r.status_code != 200:
        print(f"   ERROR: Failed to get projects: {r.status_code}")
        return
    
    projects = r.json()
    if len(projects) == 0:
        print("   No projects available for testing")
        return
    
    project_id = projects[0]['id']
    project_name = projects[0]['name']
    print(f"   Using project: {project_name} ({project_id})")
    
    # 2. Create object type WITH project_id (simulating Studio creation)
    print(f"\n2. Creating object type WITH project_id (Studio scenario)...")
    payload = {
        "api_name": "test_studio_object",
        "display_name": "Test Studio Object",
        "description": "Created from Studio with project binding",
        "property_schema": [
            {
                "key": "id",
                "label": "ID",
                "type": "STRING",
                "required": True
            },
            {
                "key": "name",
                "label": "Name",
                "type": "STRING",
                "required": False
            }
        ],
        "project_id": project_id
    }
    
    r = requests.post(f"{BASE_URL}/v1/meta/object-types", json=payload)
    if r.status_code not in (200, 201):
        print(f"   ERROR: Failed to create object type: {r.status_code}")
        print(f"   Response: {r.text}")
        return
    
    created_obj = r.json()
    obj_id = created_obj.get('id')
    print(f"   Created object type: {obj_id}")
    
    # 3. Check if project binding was created
    print(f"\n3. Checking project binding...")
    r = requests.get(f"{BASE_URL}/v3/projects/{project_id}/object-types")
    if r.status_code != 200:
        print(f"   ERROR: Failed to get project object types: {r.status_code}")
        return
    
    project_objects = r.json()
    found = any(obj['id'] == obj_id for obj in project_objects)
    if found:
        print(f"   [OK] Object type found in project object types list")
    else:
        print(f"   [FAIL] Object type NOT found in project object types list")
        print(f"   Project has {len(project_objects)} object types")
    
    # 4. Create object type WITHOUT project_id (simulating Object Center creation)
    print(f"\n4. Creating object type WITHOUT project_id (Object Center scenario)...")
    payload2 = {
        "api_name": "test_center_object",
        "display_name": "Test Center Object",
        "description": "Created from Object Center without project binding",
        "property_schema": [
            {
                "key": "id",
                "label": "ID",
                "type": "STRING",
                "required": True
            }
        ],
        "project_id": None
    }
    
    r = requests.post(f"{BASE_URL}/v1/meta/object-types", json=payload2)
    if r.status_code != 200:
        print(f"   ERROR: Failed to create object type: {r.status_code}")
        print(f"   Response: {r.text}")
        return
    
    created_obj2 = r.json()
    obj_id2 = created_obj2.get('id')
    print(f"   Created object type: {obj_id2}")
    
    # 5. Verify it's NOT in project object types
    print(f"\n5. Verifying object type is NOT in project list...")
    r = requests.get(f"{BASE_URL}/v3/projects/{project_id}/object-types")
    project_objects2 = r.json()
    found2 = any(obj['id'] == obj_id2 for obj in project_objects2)
    if not found2:
        print(f"   [OK] Object type correctly NOT in project object types list")
    else:
        print(f"   [FAIL] Object type incorrectly found in project object types list")
    
    # 6. Check if it appears in global list (Object Center)
    print(f"\n6. Checking global object types list (Object Center)...")
    r = requests.get(f"{BASE_URL}/v3/ontology/object-types")
    if r.status_code != 200:
        print(f"   ERROR: Failed to get global object types: {r.status_code}")
        return
    
    global_objects = r.json()
    found_global = any(obj['id'] == obj_id2 for obj in global_objects)
    if found_global:
        print(f"   [OK] Object type found in global object types list")
    else:
        print(f"   [FAIL] Object type NOT found in global object types list")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_create_object_type_with_project()
