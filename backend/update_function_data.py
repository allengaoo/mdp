"""
Update existing function definitions with new fields.
Updates description, input_params_schema, and output_type for existing records.
"""
import pymysql
import sys
import io
import json

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Ga0binGB',
    'database': 'ontology',
    'charset': 'utf8mb4',
}

# Function data updates
FUNCTION_UPDATES = {
    '30000000-0000-0000-0000-000000000001': {
        'description': 'Calculate damage output based on weapon type and target characteristics',
        'input_params_schema': [{"name": "weapon_type", "type": "string", "required": True}, {"name": "target_type", "type": "string", "required": True}],
        'output_type': 'INTEGER'
    },
    '30000000-0000-0000-0000-000000000002': {
        'description': 'Check current fuel level and return status indicator',
        'input_params_schema': [{"name": "fighter_id", "type": "string", "required": True}],
        'output_type': 'OBJECT'
    },
    '30000000-0000-0000-0000-000000000003': {
        'description': 'Assign a fighter aircraft to a specific mission and create participation link',
        'input_params_schema': [{"name": "fighter_id", "type": "string", "required": True}, {"name": "mission_id", "type": "string", "required": True}],
        'output_type': 'OBJECT'
    },
    '30000000-0000-0000-0000-000000000004': {
        'description': 'Apply damage to target and update health status',
        'input_params_schema': [{"name": "target_id", "type": "string", "required": True}, {"name": "damage_amount", "type": "integer", "required": True}],
        'output_type': 'INTEGER'
    },
    '30000000-0000-0000-0000-000000000005': {
        'description': 'Calculate distance between fighter and target using Haversine formula',
        'input_params_schema': [{"name": "fighter_lat", "type": "number", "required": True}, {"name": "fighter_lon", "type": "number", "required": True}, {"name": "target_lat", "type": "number", "required": True}, {"name": "target_lon", "type": "number", "required": True}],
        'output_type': 'DOUBLE'
    },
    '30000000-0000-0000-0000-000000000006': {
        'description': 'Update intelligence content with new information',
        'input_params_schema': [{"name": "intel_id", "type": "string", "required": True}, {"name": "new_data", "type": "string", "required": True}],
        'output_type': 'BOOLEAN'
    },
    '30000000-0000-0000-0000-000000000007': {
        'description': 'Refuel fighter aircraft up to maximum capacity',
        'input_params_schema': [{"name": "fighter_id", "type": "string", "required": True}, {"name": "fuel_amount", "type": "integer", "required": True}],
        'output_type': 'INTEGER'
    },
    '30000000-0000-0000-0000-000000000008': {
        'description': 'Get current mission status and participant/target counts',
        'input_params_schema': [{"name": "mission_id", "type": "string", "required": True}],
        'output_type': 'OBJECT'
    },
    '30000000-0000-0000-0000-000000000009': {
        'description': 'Scramble specified number of ready fighters from a base for alert response',
        'input_params_schema': [{"name": "base_id", "type": "string", "required": True}, {"name": "count", "type": "integer", "required": True}],
        'output_type': 'ARRAY'
    },
    '30000000-0000-0000-0000-000000000010': {
        'description': 'Assess and calculate threat level score for a target',
        'input_params_schema': [{"name": "target_id", "type": "string", "required": True}],
        'output_type': 'DOUBLE'
    },
    '30000000-0000-0000-0000-000000000011': {
        'description': 'Calculate priority score for a mission based on base priority and target threats',
        'input_params_schema': [{"name": "mission_id", "type": "string", "required": True}],
        'output_type': 'DOUBLE'
    },
    '30000000-0000-0000-0000-000000000012': {
        'description': 'Validate if mission is feasible based on assigned fighters and fuel levels',
        'input_params_schema': [{"name": "mission_id", "type": "string", "required": True}],
        'output_type': 'OBJECT'
    },
}

def update_functions():
    """Update existing function definitions with new fields."""
    connection = None
    try:
        print("Connecting to database...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print(f"Updating {len(FUNCTION_UPDATES)} function definitions...")
        
        for func_id, data in FUNCTION_UPDATES.items():
            # Convert input_params_schema to JSON string
            params_json = json.dumps(data['input_params_schema'], ensure_ascii=False)
            
            update_sql = """
            UPDATE `meta_function_def`
            SET `description` = %s,
                `input_params_schema` = %s,
                `output_type` = %s
            WHERE `id` = %s
            """
            
            cursor.execute(update_sql, (
                data['description'],
                params_json,
                data['output_type'],
                func_id
            ))
            
            print(f"  Updated function {func_id}")
        
        connection.commit()
        print(f"\nSuccessfully updated {len(FUNCTION_UPDATES)} function definitions!")
        
    except pymysql.Error as e:
        print(f"Database error: {e}")
        if connection:
            connection.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if connection:
            connection.rollback()
        sys.exit(1)
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    update_functions()

