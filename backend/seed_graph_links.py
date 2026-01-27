"""
Seed Script: Generate Graph Links for Maritime Scenario
MDP Platform V3.1 - Graph Analysis Module

Creates sys_link_instance records for testing graph analysis features.
"""
import os
import sys
import uuid
from datetime import datetime, timedelta
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


# Sample Maritime Data for Graph Testing
SAMPLE_LINKS = [
    # ==========================================
    # Target Detection Chain
    # ==========================================
    # Radar detects targets
    ("radar-001", "tgt-001", "sensor", "target", "DETECTED", {"confidence": 0.92, "method": "RADAR"}),
    ("radar-001", "tgt-002", "sensor", "target", "DETECTED", {"confidence": 0.88, "method": "RADAR"}),
    ("radar-002", "tgt-003", "sensor", "target", "DETECTED", {"confidence": 0.95, "method": "RADAR"}),
    
    # Satellite imagery confirms targets
    ("sat-img-001", "tgt-001", "recon_image", "target", "CONFIRMS", {"confidence": 0.98, "resolution": "HIGH"}),
    ("sat-img-002", "tgt-002", "recon_image", "target", "CONFIRMS", {"confidence": 0.85, "resolution": "MEDIUM"}),
    
    # ==========================================
    # Mission Assignments
    # ==========================================
    # Missions assigned to targets
    ("mission-001", "tgt-001", "mission", "target", "TARGETS", {"priority": "HIGH", "status": "ACTIVE"}),
    ("mission-002", "tgt-002", "mission", "target", "TARGETS", {"priority": "MEDIUM", "status": "PLANNED"}),
    ("mission-003", "tgt-003", "mission", "target", "TARGETS", {"priority": "HIGH", "status": "COMPLETED"}),
    
    # Aircraft assigned to missions
    ("jet-001", "mission-001", "aircraft", "mission", "ASSIGNED_TO", {"role": "STRIKE", "status": "AIRBORNE"}),
    ("jet-002", "mission-001", "aircraft", "mission", "ASSIGNED_TO", {"role": "ESCORT", "status": "AIRBORNE"}),
    ("jet-003", "mission-002", "aircraft", "mission", "ASSIGNED_TO", {"role": "RECON", "status": "STANDBY"}),
    ("jet-004", "mission-003", "aircraft", "mission", "ASSIGNED_TO", {"role": "STRIKE", "status": "RETURNED"}),
    
    # ==========================================
    # Vessel Tracking
    # ==========================================
    # Vessels at ports
    ("vessel-001", "port-001", "vessel", "port", "DOCKED_AT", {"berth": "A3", "arrival": "2024-01-15T08:00:00"}),
    ("vessel-002", "port-001", "vessel", "port", "DEPARTED_FROM", {"departure": "2024-01-14T16:00:00"}),
    ("vessel-003", "port-002", "vessel", "port", "APPROACHING", {"eta": "2024-01-16T12:00:00"}),
    
    # Vessels and targets
    ("vessel-004", "tgt-001", "vessel", "target", "IDENTIFIED_AS", {"certainty": 0.75}),
    ("vessel-005", "tgt-003", "vessel", "target", "SUSPECTED_AS", {"certainty": 0.45}),
    
    # ==========================================
    # Intelligence Network
    # ==========================================
    # Intel reports reference objects
    ("intel-001", "tgt-001", "intel_report", "target", "REFERENCES", {"section": "2.1", "classification": "SECRET"}),
    ("intel-001", "vessel-004", "intel_report", "vessel", "MENTIONS", {"section": "3.4"}),
    ("intel-002", "tgt-002", "intel_report", "target", "ANALYZES", {"depth": "DETAILED"}),
    ("intel-002", "mission-001", "intel_report", "mission", "SUPPORTS", {}),
    
    # Intel sources
    ("source-001", "intel-001", "source", "intel_report", "PROVIDED", {"reliability": "A", "credibility": "1"}),
    ("source-002", "intel-002", "source", "intel_report", "PROVIDED", {"reliability": "B", "credibility": "2"}),
    
    # ==========================================
    # Command & Control
    # ==========================================
    # Units under command
    ("command-001", "jet-001", "command_unit", "aircraft", "CONTROLS", {}),
    ("command-001", "jet-002", "command_unit", "aircraft", "CONTROLS", {}),
    ("command-001", "radar-001", "command_unit", "sensor", "OPERATES", {}),
    ("command-002", "jet-003", "command_unit", "aircraft", "CONTROLS", {}),
    ("command-002", "jet-004", "command_unit", "aircraft", "CONTROLS", {}),
]


def seed_graph_links():
    """Generate link instances for graph analysis testing."""
    import pymysql
    import json
    
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
            # Clear existing links
            print("\nClearing existing links...")
            cursor.execute("DELETE FROM sys_link_instance")
            connection.commit()
            
            # Insert sample links
            print(f"\nCreating {len(SAMPLE_LINKS)} sample links...")
            
            base_time = datetime.now() - timedelta(hours=12)
            
            for idx, (source_id, target_id, source_type, target_type, role, props) in enumerate(SAMPLE_LINKS):
                link_id = str(uuid.uuid4())
                
                # Add role to properties
                properties = {**props, "role": role}
                
                # Generate temporal data (spread across 24 hours)
                valid_start = base_time + timedelta(minutes=idx * 30)
                valid_end = valid_start + timedelta(hours=2 + idx % 4)
                
                cursor.execute("""
                    INSERT INTO sys_link_instance 
                    (id, link_type_id, source_instance_id, target_instance_id, source_object_type, target_object_type,
                     valid_start, valid_end, properties, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    link_id,
                    None,  # link_type_id - will be set when we have schema
                    source_id,
                    target_id,
                    source_type,
                    target_type,
                    valid_start,
                    valid_end,
                    json.dumps(properties),
                    datetime.now()
                ))
            
            connection.commit()
            
            # Summary
            print(f"\n=== Summary ===")
            print(f"Total links created: {len(SAMPLE_LINKS)}")
            
            cursor.execute("""
                SELECT source_object_type, target_object_type, COUNT(*) as cnt
                FROM sys_link_instance
                GROUP BY source_object_type, target_object_type
                ORDER BY cnt DESC
            """)
            
            print("\nLink distribution by type:")
            for row in cursor.fetchall():
                print(f"  {row[0]} -> {row[1]}: {row[2]} links")
            
            # Show unique nodes
            cursor.execute("""
                SELECT DISTINCT source_instance_id, source_object_type FROM sys_link_instance
                UNION
                SELECT DISTINCT target_instance_id, target_object_type FROM sys_link_instance
            """)
            
            nodes = cursor.fetchall()
            print(f"\nUnique nodes: {len(nodes)}")
            
            # Group nodes by type
            node_types = {}
            for node_id, node_type in nodes:
                if node_type not in node_types:
                    node_types[node_type] = []
                node_types[node_type].append(node_id)
            
            print("\nNodes by type:")
            for node_type, node_ids in sorted(node_types.items()):
                print(f"  {node_type}: {len(node_ids)} ({', '.join(node_ids[:3])}{'...' if len(node_ids) > 3 else ''})")
                
    finally:
        connection.close()
    
    print("\n✓ Graph link seeding completed!")


if __name__ == "__main__":
    seed_graph_links()
