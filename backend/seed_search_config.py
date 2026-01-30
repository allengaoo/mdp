"""
Seed Script: Configure Search Flags for Maritime Ontology
MDP Platform V3.1 - Global Search Module

Updates rel_object_ver_property to enable search capabilities for specific properties.

Configuration:
- Target: status (Filter), type (Filter), threat_level (Filter+Sort), description (Search)
- IntelReport: content (Search), classification (Filter)
- Vessel: name (Search+Title), status (Filter), vessel_type (Filter)
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()


def parse_database_url(url: str) -> dict:
    """Parse DATABASE_URL into connection parameters."""
    import re
    pattern = r"mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)"
    match = re.match(pattern, url)
    if not match:
        raise ValueError(f"Invalid DATABASE_URL format: {url}")
    return {
        "user": match.group(1),
        "password": match.group(2),
        "host": match.group(3),
        "port": int(match.group(4)),
        "database": match.group(5),
    }


# Search configuration mapping
# Format: { object_api_name: { property_api_name: {is_searchable, is_filterable, is_sortable} } }
SEARCH_CONFIG = {
    # Target object type
    "target": {
        "name": {"is_searchable": True, "is_filterable": False, "is_sortable": True},
        "description": {"is_searchable": True, "is_filterable": False, "is_sortable": False},
        "status": {"is_searchable": False, "is_filterable": True, "is_sortable": False},
        "target_type": {"is_searchable": False, "is_filterable": True, "is_sortable": False},
        "threat_level": {"is_searchable": False, "is_filterable": True, "is_sortable": True},
    },
    # Vessel object type
    "vessel": {
        "name": {"is_searchable": True, "is_filterable": False, "is_sortable": True},
        "description": {"is_searchable": True, "is_filterable": False, "is_sortable": False},
        "status": {"is_searchable": False, "is_filterable": True, "is_sortable": False},
        "vessel_type": {"is_searchable": False, "is_filterable": True, "is_sortable": False},
        "flag": {"is_searchable": False, "is_filterable": True, "is_sortable": False},
    },
    # IntelReport object type
    "intel_report": {
        "title": {"is_searchable": True, "is_filterable": False, "is_sortable": True},
        "content": {"is_searchable": True, "is_filterable": False, "is_sortable": False},
        "classification": {"is_searchable": False, "is_filterable": True, "is_sortable": False},
        "source": {"is_searchable": False, "is_filterable": True, "is_sortable": False},
        "status": {"is_searchable": False, "is_filterable": True, "is_sortable": False},
    },
    # Aircraft object type
    "aircraft": {
        "name": {"is_searchable": True, "is_filterable": False, "is_sortable": True},
        "description": {"is_searchable": True, "is_filterable": False, "is_sortable": False},
        "status": {"is_searchable": False, "is_filterable": True, "is_sortable": False},
        "aircraft_type": {"is_searchable": False, "is_filterable": True, "is_sortable": False},
    },
    # Sensor object type
    "sensor": {
        "name": {"is_searchable": True, "is_filterable": False, "is_sortable": True},
        "description": {"is_searchable": True, "is_filterable": False, "is_sortable": False},
        "sensor_type": {"is_searchable": False, "is_filterable": True, "is_sortable": False},
        "status": {"is_searchable": False, "is_filterable": True, "is_sortable": False},
    },
}


def seed_search_config():
    """Update search configuration for Maritime Ontology properties."""
    import pymysql
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    db_params = parse_database_url(database_url)
    print(f"Connecting to {db_params['host']}:{db_params['port']}/{db_params['database']}...")
    
    connection = pymysql.connect(
        host=db_params["host"],
        port=db_params["port"],
        user=db_params["user"],
        password=db_params["password"],
        database=db_params["database"],
        charset="utf8mb4",
    )
    
    try:
        with connection.cursor() as cursor:
            updated_count = 0
            
            for object_api_name, properties in SEARCH_CONFIG.items():
                print(f"\nConfiguring object type: {object_api_name}")
                
                # Get object type def ID
                cursor.execute("""
                    SELECT id, current_version_id 
                    FROM meta_object_type_def 
                    WHERE api_name = %s
                """, (object_api_name,))
                
                obj_result = cursor.fetchone()
                if not obj_result:
                    print(f"  WARNING: Object type '{object_api_name}' not found, skipping...")
                    continue
                
                obj_def_id, obj_ver_id = obj_result
                
                if not obj_ver_id:
                    print(f"  WARNING: Object type '{object_api_name}' has no current version, skipping...")
                    continue
                
                for prop_api_name, config in properties.items():
                    # Get property def ID
                    cursor.execute("""
                        SELECT id FROM meta_shared_property_def WHERE api_name = %s
                    """, (prop_api_name,))
                    
                    prop_result = cursor.fetchone()
                    if not prop_result:
                        print(f"  WARNING: Property '{prop_api_name}' not found, skipping...")
                        continue
                    
                    prop_def_id = prop_result[0]
                    
                    # Update the property binding
                    cursor.execute("""
                        UPDATE rel_object_ver_property
                        SET is_searchable = %s, is_filterable = %s, is_sortable = %s
                        WHERE object_ver_id = %s AND property_def_id = %s
                    """, (
                        config["is_searchable"],
                        config["is_filterable"],
                        config["is_sortable"],
                        obj_ver_id,
                        prop_def_id,
                    ))
                    
                    if cursor.rowcount > 0:
                        flags = []
                        if config["is_searchable"]: flags.append("SEARCH")
                        if config["is_filterable"]: flags.append("FILTER")
                        if config["is_sortable"]: flags.append("SORT")
                        print(f"  Updated: {prop_api_name} -> [{', '.join(flags) or 'NONE'}]")
                        updated_count += cursor.rowcount
                    else:
                        print(f"  Binding not found: {prop_api_name}")
            
            connection.commit()
            print(f"\n=== Search configuration completed: {updated_count} property bindings updated ===")
            
            # Summary query
            print("\n=== Searchable Properties Summary ===")
            cursor.execute("""
                SELECT 
                    otd.api_name AS object_type,
                    spd.api_name AS property,
                    ovp.is_searchable,
                    ovp.is_filterable,
                    ovp.is_sortable
                FROM rel_object_ver_property ovp
                JOIN meta_object_type_ver otv ON ovp.object_ver_id = otv.id
                JOIN meta_object_type_def otd ON otv.def_id = otd.id
                JOIN meta_shared_property_def spd ON ovp.property_def_id = spd.id
                WHERE ovp.is_searchable = 1 OR ovp.is_filterable = 1 OR ovp.is_sortable = 1
                ORDER BY otd.api_name, spd.api_name
            """)
            
            for row in cursor.fetchall():
                flags = []
                if row[2]: flags.append("S")  # Searchable
                if row[3]: flags.append("F")  # Filterable
                if row[4]: flags.append("O")  # sOrtable
                print(f"  {row[0]}.{row[1]} [{'/'.join(flags)}]")
                
    finally:
        connection.close()


if __name__ == "__main__":
    seed_search_config()
