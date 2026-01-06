-- MDP Platform Demo - Battlefield Scenario Seed Data
-- Compatible with MySQL 8.0+
-- Execute after init.sql

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ==========================================
-- 0. Meta Layer: Projects
-- ==========================================

INSERT INTO `meta_project` (`id`, `name`, `description`, `created_at`) VALUES
('00000000-0000-0000-0000-000000000001', 'Battlefield System', 'Battlefield Demo Project - Military operations simulation', NOW());

-- ==========================================
-- 0.5 Meta Layer: Shared Properties
-- ==========================================

INSERT INTO `meta_shared_property` (`id`, `project_id`, `api_name`, `display_name`, `data_type`, `formatter`, `description`, `created_at`) VALUES
('70000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'location_lat', 'Latitude', 'Number', 'decimal:6', 'Geographic latitude coordinate', NOW()),
('70000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'location_lon', 'Longitude', 'Number', 'decimal:6', 'Geographic longitude coordinate', NOW()),
('70000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'status', 'Status', 'String', NULL, 'Current operational status', NOW()),
('70000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', 'name', 'Name', 'String', NULL, 'Display name or identifier', NOW()),
('70000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', 'priority', 'Priority', 'Integer', NULL, 'Priority level (1-10)', NOW()),
('70000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000001', 'created_time', 'Created Time', 'DateTime', 'iso8601', 'Creation timestamp', NOW());

-- ==========================================
-- 1. Meta Layer: Object Types
-- ==========================================

INSERT INTO `meta_object_type` (`id`, `api_name`, `display_name`, `description`, `property_schema`, `project_id`) VALUES
('10000000-0000-0000-0000-000000000001', 'fighter', 'Fighter Jet', 'Combat aircraft with weaponry and fuel systems', '{"fuel": "number", "callsign": "string", "status": "string", "lat": "number", "lon": "number", "altitude": "number", "weapons": "array"}', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000002', 'target', 'Target', 'Enemy target for mission objectives', '{"name": "string", "threat_level": "string", "lat": "number", "lon": "number", "type": "string", "priority": "number"}', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000003', 'mission', 'Mission', 'Military operation with objectives', '{"name": "string", "type": "string", "status": "string", "priority": "number", "start_time": "datetime", "end_time": "datetime"}', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000004', 'intel', 'Intelligence', 'Intelligence data on targets or situations', '{"source": "string", "classification": "string", "validity": "datetime", "confidence": "number", "content": "text"}', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000005', 'base', 'Military Base', 'Airbase or military installation', '{"name": "string", "location": "string", "lat": "number", "lon": "number", "capacity": "number", "status": "string"}', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000006', 'weapon', 'Weapon System', 'Weapon payload or system', '{"type": "string", "damage": "number", "range": "number", "count": "number"}', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000007', 'radar', 'Radar Station', 'Detection and tracking radar system', '{"range": "number", "frequency": "string", "status": "string", "lat": "number", "lon": "number"}', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000008', 'squadron', 'Squadron', 'Group of fighters operating together', '{"name": "string", "size": "number", "specialization": "string", "status": "string"}', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000009', 'command', 'Command Center', 'Command and control center', '{"name": "string", "level": "string", "lat": "number", "lon": "number", "capacity": "number"}', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000010', 'supply', 'Supply Depot', 'Military supply and logistics depot', '{"name": "string", "type": "string", "capacity": "number", "status": "string", "lat": "number", "lon": "number"}', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000011', 'weather', 'Weather Report', 'Weather conditions and forecasts', '{"visibility": "number", "wind_speed": "number", "cloud_cover": "number", "conditions": "string"}', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000012', 'alert', 'Alert Level', 'Threat alert or warning system', '{"level": "string", "type": "string", "description": "text", "expires": "datetime"}', '00000000-0000-0000-0000-000000000001');

-- ==========================================
-- 2. Meta Layer: Link Types
-- ==========================================

INSERT INTO `meta_link_type` (`id`, `api_name`, `display_name`, `source_type_id`, `target_type_id`, `cardinality`) VALUES
('20000000-0000-0000-0000-000000000001', 'participation', 'Fighter Participation', '10000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000003', 'MANY_TO_MANY'),
('20000000-0000-0000-0000-000000000002', 'targeting', 'Mission Targeting', '10000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000002', 'ONE_TO_MANY'),
('20000000-0000-0000-0000-000000000003', 'stationed_at', 'Stationed At Base', '10000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000005', 'MANY_TO_ONE'),
('20000000-0000-0000-0000-000000000004', 'intel_on', 'Intelligence On Target', '10000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000002', 'MANY_TO_MANY'),
('20000000-0000-0000-0000-000000000005', 'assigned_to', 'Mission Assigned To', '10000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000001', 'ONE_TO_MANY'),
('20000000-0000-0000-0000-000000000006', 'equipped_with', 'Fighter Equipped With', '10000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000006', 'MANY_TO_MANY'),
('20000000-0000-0000-0000-000000000007', 'detects', 'Radar Detects', '10000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000001', 'ONE_TO_MANY'),
('20000000-0000-0000-0000-000000000008', 'belongs_to', 'Fighter Belongs To Squadron', '10000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000008', 'MANY_TO_ONE'),
('20000000-0000-0000-0000-000000000009', 'commands', 'Command Center Commands', '10000000-0000-0000-0000-000000000009', '10000000-0000-0000-0000-000000000003', 'ONE_TO_MANY'),
('20000000-0000-0000-0000-000000000010', 'supplies', 'Base Supplies', '10000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000010', 'ONE_TO_MANY'),
('20000000-0000-0000-0000-000000000011', 'affects', 'Weather Affects Mission', '10000000-0000-0000-0000-000000000011', '10000000-0000-0000-0000-000000000003', 'ONE_TO_MANY'),
('20000000-0000-0000-0000-000000000012', 'triggers', 'Alert Triggers Response', '10000000-0000-0000-0000-000000000012', '10000000-0000-0000-0000-000000000003', 'ONE_TO_MANY');

-- ==========================================
-- 3. Meta Layer: Function Definitions
-- ==========================================

INSERT INTO `meta_function_def` (`id`, `api_name`, `display_name`, `code_content`, `bound_object_type_id`, `description`, `input_params_schema`, `output_type`) VALUES
('30000000-0000-0000-0000-000000000001', 'calc_strike', 'Calculate Strike Damage', 'def calc_strike(weapon_type, target_type):\n    damage_matrix = {\"missile\": 100, \"bomb\": 150, \"cannon\": 50}\n    return damage_matrix.get(weapon_type, 0) * target_type_multiplier(target_type)', '10000000-0000-0000-0000-000000000001', 'Calculate damage output based on weapon type and target characteristics', '[{"name": "weapon_type", "type": "string", "required": true}, {"name": "target_type", "type": "string", "required": true}]', 'INTEGER'),
('30000000-0000-0000-0000-000000000002', 'check_fuel', 'Check Fighter Fuel Level', 'def check_fuel(fighter_id):\n    fighter = get_object(fighter_id)\n    fuel = fighter.properties.get(\"fuel\", 0)\n    return {\"fuel\": fuel, \"status\": \"critical\" if fuel < 20 else \"low\" if fuel < 50 else \"ok\"}', '10000000-0000-0000-0000-000000000001', 'Check current fuel level and return status indicator', '[{"name": "fighter_id", "type": "string", "required": true}]', 'OBJECT'),
('30000000-0000-0000-0000-000000000003', 'assign_mission', 'Assign Fighter to Mission', 'def assign_mission(fighter_id, mission_id):\n    create_link(\"participation\", fighter_id, mission_id)\n    update_object(fighter_id, {\"status\": \"assigned\"})\n    return {\"success\": True}', NULL, 'Assign a fighter aircraft to a specific mission and create participation link', '[{"name": "fighter_id", "type": "string", "required": true}, {"name": "mission_id", "type": "string", "required": true}]', 'OBJECT'),
('30000000-0000-0000-0000-000000000004', 'report_damage', 'Report Target Damage', 'def report_damage(target_id, damage_amount):\n    target = get_object(target_id)\n    current_health = target.properties.get(\"health\", 100)\n    new_health = max(0, current_health - damage_amount)\n    update_object(target_id, {\"health\": new_health, \"status\": \"destroyed\" if new_health == 0 else \"damaged\"})\n    return new_health', '10000000-0000-0000-0000-000000000002', 'Apply damage to target and update health status', '[{"name": "target_id", "type": "string", "required": true}, {"name": "damage_amount", "type": "integer", "required": true}]', 'INTEGER'),
('30000000-0000-0000-0000-000000000005', 'calculate_range', 'Calculate Distance to Target', 'def calculate_range(fighter_lat, fighter_lon, target_lat, target_lon):\n    import math\n    dlat = math.radians(target_lat - fighter_lat)\n    dlon = math.radians(target_lon - fighter_lon)\n    a = math.sin(dlat/2)**2 + math.cos(math.radians(fighter_lat)) * math.cos(math.radians(target_lat)) * math.sin(dlon/2)**2\n    return 6371 * 2 * math.asin(math.sqrt(a))', NULL, 'Calculate distance between fighter and target using Haversine formula', '[{"name": "fighter_lat", "type": "number", "required": true}, {"name": "fighter_lon", "type": "number", "required": true}, {"name": "target_lat", "type": "number", "required": true}, {"name": "target_lon", "type": "number", "required": true}]', 'DOUBLE'),
('30000000-0000-0000-0000-000000000006', 'update_intel', 'Update Intelligence Data', 'def update_intel(intel_id, new_data):\n    intel = get_object(intel_id)\n    updated_content = intel.properties.get(\"content\", \"\") + \"\\n\" + new_data\n    update_object(intel_id, {\"content\": updated_content, \"updated\": datetime.now()})\n    return True', '10000000-0000-0000-0000-000000000004', 'Update intelligence content with new information', '[{"name": "intel_id", "type": "string", "required": true}, {"name": "new_data", "type": "string", "required": true}]', 'BOOLEAN'),
('30000000-0000-0000-0000-000000000007', 'refuel_fighter', 'Refuel Fighter Aircraft', 'def refuel_fighter(fighter_id, fuel_amount):\n    fighter = get_object(fighter_id)\n    current_fuel = fighter.properties.get(\"fuel\", 0)\n    max_fuel = 100\n    new_fuel = min(max_fuel, current_fuel + fuel_amount)\n    update_object(fighter_id, {\"fuel\": new_fuel})\n    return new_fuel', '10000000-0000-0000-0000-000000000001', 'Refuel fighter aircraft up to maximum capacity', '[{"name": "fighter_id", "type": "string", "required": true}, {"name": "fuel_amount", "type": "integer", "required": true}]', 'INTEGER'),
('30000000-0000-0000-0000-000000000008', 'check_mission_status', 'Check Mission Status', 'def check_mission_status(mission_id):\n    mission = get_object(mission_id)\n    participants = get_linked_objects(mission_id, \"participation\")\n    targets = get_linked_objects(mission_id, \"targeting\")\n    return {\"status\": mission.properties.get(\"status\"), \"participants\": len(participants), \"targets\": len(targets)}', '10000000-0000-0000-0000-000000000003', 'Get current mission status and participant/target counts', '[{"name": "mission_id", "type": "string", "required": true}]', 'OBJECT'),
('30000000-0000-0000-0000-000000000009', 'scramble_fighters', 'Scramble Fighters for Alert', 'def scramble_fighters(base_id, count):\n    fighters = get_fighters_at_base(base_id, status=\"ready\")\n    scrambled = fighters[:count]\n    for fighter in scrambled:\n        update_object(fighter.id, {\"status\": \"scrambled\", \"fuel\": 100})\n    return [f.id for f in scrambled]', NULL, 'Scramble specified number of ready fighters from a base for alert response', '[{"name": "base_id", "type": "string", "required": true}, {"name": "count", "type": "integer", "required": true}]', 'ARRAY'),
('30000000-0000-0000-0000-000000000010', 'assess_threat', 'Assess Target Threat Level', 'def assess_threat(target_id):\n    target = get_object(target_id)\n    base_threat = {\"high\": 3, \"medium\": 2, \"low\": 1}.get(target.properties.get(\"threat_level\", \"low\"), 1)\n    intel_count = len(get_linked_objects(target_id, \"intel_on\"))\n    return base_threat * (1 + intel_count * 0.2)', '10000000-0000-0000-0000-000000000002', 'Assess and calculate threat level score for a target', '[{"name": "target_id", "type": "string", "required": true}]', 'DOUBLE'),
('30000000-0000-0000-0000-000000000011', 'calculate_mission_priority', 'Calculate Mission Priority Score', 'def calculate_mission_priority(mission_id):\n    mission = get_object(mission_id)\n    base_priority = mission.properties.get(\"priority\", 1)\n    target_threats = [assess_threat(t.id) for t in get_linked_objects(mission_id, \"targeting\")]\n    return base_priority * max(target_threats, default=1)', '10000000-0000-0000-0000-000000000003', 'Calculate priority score for a mission based on base priority and target threats', '[{"name": "mission_id", "type": "string", "required": true}]', 'DOUBLE'),
('30000000-0000-0000-0000-000000000012', 'validate_mission', 'Validate Mission Feasibility', 'def validate_mission(mission_id):\n    mission = get_object(mission_id)\n    fighters = get_linked_objects(mission_id, \"participation\")\n    if len(fighters) == 0:\n        return {\"valid\": False, \"reason\": \"No fighters assigned\"}\n    all_fueled = all(f.properties.get(\"fuel\", 0) > 50 for f in fighters)\n    return {\"valid\": all_fueled, \"reason\": \"Insufficient fuel\" if not all_fueled else \"OK\"}', '10000000-0000-0000-0000-000000000003', 'Validate if mission is feasible based on assigned fighters and fuel levels', '[{"name": "mission_id", "type": "string", "required": true}]', 'OBJECT');

-- ==========================================
-- 4. Meta Layer: Action Definitions
-- ==========================================

INSERT INTO `meta_action_def` (`id`, `api_name`, `display_name`, `backing_function_id`) VALUES
('40000000-0000-0000-0000-000000000001', 'execute_strike', 'Execute Strike Action', '30000000-0000-0000-0000-000000000001'),
('40000000-0000-0000-0000-000000000002', 'refuel', 'Refuel Fighter', '30000000-0000-0000-0000-000000000007'),
('40000000-0000-0000-0000-000000000003', 'scramble', 'Scramble Fighters', '30000000-0000-0000-0000-000000000009'),
('40000000-0000-0000-0000-000000000004', 'update_intel', 'Update Intelligence', '30000000-0000-0000-0000-000000000006'),
('40000000-0000-0000-0000-000000000005', 'assign_to_mission', 'Assign to Mission', '30000000-0000-0000-0000-000000000003'),
('40000000-0000-0000-0000-000000000006', 'check_status', 'Check Fighter Status', '30000000-0000-0000-0000-000000000002'),
('40000000-0000-0000-0000-000000000007', 'report_target_damage', 'Report Target Damage', '30000000-0000-0000-0000-000000000004'),
('40000000-0000-0000-0000-000000000008', 'check_mission', 'Check Mission Status', '30000000-0000-0000-0000-000000000008'),
('40000000-0000-0000-0000-000000000009', 'calculate_range_to_target', 'Calculate Range', '30000000-0000-0000-0000-000000000005'),
('40000000-0000-0000-0000-000000000010', 'assess_target_threat', 'Assess Threat Level', '30000000-0000-0000-0000-000000000010'),
('40000000-0000-0000-0000-000000000011', 'prioritize_mission', 'Calculate Mission Priority', '30000000-0000-0000-0000-000000000011'),
('40000000-0000-0000-0000-000000000012', 'validate_mission_feasibility', 'Validate Mission', '30000000-0000-0000-0000-000000000012');

-- ==========================================
-- 5. Instance Layer: Object Instances
-- ==========================================

-- 5.1 Fighters (10+)
INSERT INTO `sys_object_instance` (`id`, `object_type_id`, `properties`) VALUES
('50000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', '{"callsign": "Ghost-1", "fuel": 90, "status": "Ready", "lat": 34.0522, "lon": 108.9451, "altitude": 10000, "weapons": ["missile", "cannon"]}'),
('50000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', '{"callsign": "Ghost-2", "fuel": 85, "status": "Ready", "lat": 34.0530, "lon": 108.9460, "altitude": 9500, "weapons": ["missile", "bomb"]}'),
('50000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000001', '{"callsign": "Dragon-1", "fuel": 75, "status": "In Flight", "lat": 35.1234, "lon": 110.5678, "altitude": 12000, "weapons": ["missile"]}'),
('50000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000001', '{"callsign": "Dragon-2", "fuel": 60, "status": "In Flight", "lat": 35.1240, "lon": 110.5680, "altitude": 11500, "weapons": ["missile", "cannon"]}'),
('50000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000001', '{"callsign": "Thunder-1", "fuel": 95, "status": "Ready", "lat": 34.0500, "lon": 108.9400, "altitude": 0, "weapons": ["missile", "bomb", "cannon"]}'),
('50000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000001', '{"callsign": "Thunder-2", "fuel": 45, "status": "Refueling", "lat": 34.0510, "lon": 108.9410, "altitude": 0, "weapons": ["missile"]}'),
('50000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000001', '{"callsign": "Eagle-1", "fuel": 80, "status": "Ready", "lat": 34.0540, "lon": 108.9470, "altitude": 0, "weapons": ["missile", "cannon"]}'),
('50000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000001', '{"callsign": "Eagle-2", "fuel": 70, "status": "Assigned", "lat": 34.0550, "lon": 108.9480, "altitude": 0, "weapons": ["missile", "bomb"]}'),
('50000000-0000-0000-0000-000000000009', '10000000-0000-0000-0000-000000000001', '{"callsign": "Falcon-1", "fuel": 88, "status": "Ready", "lat": 34.0560, "lon": 108.9490, "altitude": 0, "weapons": ["missile"]}'),
('50000000-0000-0000-0000-000000000010', '10000000-0000-0000-0000-000000000001', '{"callsign": "Falcon-2", "fuel": 92, "status": "Ready", "lat": 34.0570, "lon": 108.9500, "altitude": 0, "weapons": ["missile", "cannon"]}'),
('50000000-0000-0000-0000-000000000011', '10000000-0000-0000-0000-000000000001', '{"callsign": "Hawk-1", "fuel": 65, "status": "In Flight", "lat": 36.2000, "lon": 111.3000, "altitude": 8000, "weapons": ["missile", "bomb"]}'),
('50000000-0000-0000-0000-000000000012', '10000000-0000-0000-0000-000000000001', '{"callsign": "Hawk-2", "fuel": 55, "status": "Returning", "lat": 34.1000, "lon": 109.0000, "altitude": 5000, "weapons": ["missile"]}');

-- 5.2 Targets (10+)
INSERT INTO `sys_object_instance` (`id`, `object_type_id`, `properties`) VALUES
('51000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', '{"name": "Radar Station Alpha", "threat_level": "high", "lat": 35.5000, "lon": 111.5000, "type": "radar", "priority": 9, "health": 100}'),
('51000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', '{"name": "Bunker Complex Bravo", "threat_level": "high", "lat": 36.0000, "lon": 112.0000, "type": "bunker", "priority": 8, "health": 150}'),
('51000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000002', '{"name": "Convoy Charlie", "threat_level": "medium", "lat": 35.7500, "lon": 111.7500, "type": "convoy", "priority": 6, "health": 80}'),
('51000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000002', '{"name": "Command Post Delta", "threat_level": "high", "lat": 36.2500, "lon": 112.2500, "type": "command", "priority": 10, "health": 120}'),
('51000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000002', '{"name": "Supply Depot Echo", "threat_level": "medium", "lat": 35.3000, "lon": 111.3000, "type": "supply", "priority": 5, "health": 90}'),
('51000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000002', '{"name": "Airfield Foxtrot", "threat_level": "high", "lat": 36.5000, "lon": 112.5000, "type": "airfield", "priority": 9, "health": 200}'),
('51000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000002', '{"name": "Bridge Golf", "threat_level": "low", "lat": 35.1000, "lon": 111.1000, "type": "bridge", "priority": 4, "health": 60}'),
('51000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000002', '{"name": "SAM Site Hotel", "threat_level": "high", "lat": 36.7500, "lon": 112.7500, "type": "sam", "priority": 8, "health": 100}'),
('51000000-0000-0000-0000-000000000009', '10000000-0000-0000-0000-000000000002', '{"name": "Tank Column India", "threat_level": "medium", "lat": 35.6000, "lon": 111.6000, "type": "armor", "priority": 7, "health": 110}'),
('51000000-0000-0000-0000-000000000010', '10000000-0000-0000-0000-000000000002', '{"name": "Artillery Position Juliet", "threat_level": "medium", "lat": 36.1000, "lon": 112.1000, "type": "artillery", "priority": 6, "health": 70}'),
('51000000-0000-0000-0000-000000000011', '10000000-0000-0000-0000-000000000002', '{"name": "Communication Hub Kilo", "threat_level": "high", "lat": 35.9000, "lon": 111.9000, "type": "comm", "priority": 8, "health": 85}'),
('51000000-0000-0000-0000-000000000012', '10000000-0000-0000-0000-000000000002', '{"name": "Warehouse Lima", "threat_level": "low", "lat": 35.4000, "lon": 111.4000, "type": "warehouse", "priority": 3, "health": 50}');

-- 5.3 Missions (10+)
INSERT INTO `sys_object_instance` (`id`, `object_type_id`, `properties`) VALUES
('52000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000003', '{"name": "Operation Thunder Strike", "type": "strike", "status": "in_progress", "priority": 9, "start_time": "2024-01-01 10:00:00", "end_time": "2024-01-01 14:00:00"}'),
('52000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000003', '{"name": "Patrol Route Alpha", "type": "patrol", "status": "planned", "priority": 5, "start_time": "2024-01-01 15:00:00", "end_time": "2024-01-01 18:00:00"}'),
('52000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', '{"name": "Reconnaissance Mission Bravo", "type": "recon", "status": "completed", "priority": 7, "start_time": "2024-01-01 08:00:00", "end_time": "2024-01-01 10:00:00"}'),
('52000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000003', '{"name": "Air Defense Suppression", "type": "sead", "status": "planned", "priority": 8, "start_time": "2024-01-01 16:00:00", "end_time": "2024-01-01 20:00:00"}'),
('52000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000003', '{"name": "Close Air Support Charlie", "type": "cas", "status": "in_progress", "priority": 10, "start_time": "2024-01-01 12:00:00", "end_time": "2024-01-01 16:00:00"}'),
('52000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000003', '{"name": "Interdiction Mission Delta", "type": "interdiction", "status": "planned", "priority": 6, "start_time": "2024-01-02 06:00:00", "end_time": "2024-01-02 10:00:00"}'),
('52000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000003', '{"name": "Escort Mission Echo", "type": "escort", "status": "planned", "priority": 7, "start_time": "2024-01-02 08:00:00", "end_time": "2024-01-02 12:00:00"}'),
('52000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000003', '{"name": "Deep Strike Foxtrot", "type": "strike", "status": "planned", "priority": 9, "start_time": "2024-01-02 14:00:00", "end_time": "2024-01-02 18:00:00"}'),
('52000000-0000-0000-0000-000000000009', '10000000-0000-0000-0000-000000000003', '{"name": "Combat Air Patrol Golf", "type": "cap", "status": "in_progress", "priority": 6, "start_time": "2024-01-01 11:00:00", "end_time": "2024-01-01 15:00:00"}'),
('52000000-0000-0000-0000-000000000010', '10000000-0000-0000-0000-000000000003', '{"name": "Target Verification Hotel", "type": "recon", "status": "planned", "priority": 5, "start_time": "2024-01-02 10:00:00", "end_time": "2024-01-02 13:00:00"}'),
('52000000-0000-0000-0000-000000000011', '10000000-0000-0000-0000-000000000003', '{"name": "Strike Package India", "type": "strike", "status": "planned", "priority": 8, "start_time": "2024-01-03 08:00:00", "end_time": "2024-01-03 12:00:00"}'),
('52000000-0000-0000-0000-000000000012', '10000000-0000-0000-0000-000000000003', '{"name": "Quick Reaction Alert", "type": "qra", "status": "standby", "priority": 10, "start_time": null, "end_time": null}');

-- 5.4 Intelligence (10+)
INSERT INTO `sys_object_instance` (`id`, `object_type_id`, `properties`) VALUES
('53000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000004', '{"source": "satellite", "classification": "top_secret", "validity": "2024-01-10 00:00:00", "confidence": 0.95, "content": "Radar Station Alpha operational, 3 detection arrays active"}'),
('53000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000004', '{"source": "recon_mission", "classification": "secret", "validity": "2024-01-08 00:00:00", "confidence": 0.85, "content": "Bunker Complex Bravo heavily fortified, 12 entrances identified"}'),
('53000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000004', '{"source": "human_intel", "classification": "confidential", "validity": "2024-01-07 00:00:00", "confidence": 0.70, "content": "Convoy Charlie moving east, 15 vehicles, mixed cargo"}'),
('53000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000004', '{"source": "sigint", "classification": "top_secret", "validity": "2024-01-09 00:00:00", "confidence": 0.90, "content": "Command Post Delta coordinates verified, high command traffic"}'),
('53000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000004', '{"source": "satellite", "classification": "secret", "validity": "2024-01-06 00:00:00", "confidence": 0.80, "content": "Supply Depot Echo storage capacity 80% full"}'),
('53000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000004', '{"source": "recon_mission", "classification": "secret", "validity": "2024-01-05 00:00:00", "confidence": 0.88, "content": "Airfield Foxtrot: 8 aircraft on tarmac, 2 runways operational"}'),
('53000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000004', '{"source": "imagery", "classification": "confidential", "validity": "2024-01-04 00:00:00", "confidence": 0.75, "content": "Bridge Golf structural integrity questionable, supports visible"}'),
('53000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000004', '{"source": "sigint", "classification": "top_secret", "validity": "2024-01-08 00:00:00", "confidence": 0.92, "content": "SAM Site Hotel radar frequency 2.8GHz, 4 launchers active"}'),
('53000000-0000-0000-0000-000000000009', '10000000-0000-0000-0000-000000000004', '{"source": "human_intel", "classification": "secret", "validity": "2024-01-07 00:00:00", "confidence": 0.65, "content": "Tank Column India: 20 T-72s, heading northeast"}'),
('53000000-0000-0000-0000-000000000010', '10000000-0000-0000-0000-000000000004', '{"source": "recon_mission", "classification": "confidential", "validity": "2024-01-06 00:00:00", "confidence": 0.78, "content": "Artillery Position Juliet: 6 howitzers, ammunition stockpile nearby"}'),
('53000000-0000-0000-0000-000000000011', '10000000-0000-0000-0000-000000000004', '{"source": "satellite", "classification": "secret", "validity": "2024-01-09 00:00:00", "confidence": 0.86, "content": "Communication Hub Kilo: antenna array operational, high traffic"}'),
('53000000-0000-0000-0000-000000000012', '10000000-0000-0000-0000-000000000004', '{"source": "imagery", "classification": "confidential", "validity": "2024-01-05 00:00:00", "confidence": 0.72, "content": "Warehouse Lima: single building, appears abandoned"}');

-- 5.5 Bases (10+)
INSERT INTO `sys_object_instance` (`id`, `object_type_id`, `properties`) VALUES
('54000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000005', '{"name": "Base Alpha", "location": "Northwest Sector", "lat": 34.0522, "lon": 108.9451, "capacity": 24, "status": "operational"}'),
('54000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000005', '{"name": "Base Bravo", "location": "Eastern Sector", "lat": 34.5000, "lon": 109.5000, "capacity": 18, "status": "operational"}'),
('54000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000005', '{"name": "Forward Base Charlie", "location": "Frontline", "lat": 35.0000, "lon": 110.0000, "capacity": 12, "status": "operational"}'),
('54000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000005', '{"name": "Support Base Delta", "location": "Rear Area", "lat": 33.5000, "lon": 108.5000, "capacity": 30, "status": "operational"}'),
('54000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000005', '{"name": "Reserve Base Echo", "location": "Western Sector", "lat": 34.2000, "lon": 108.2000, "capacity": 20, "status": "operational"}'),
('54000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000005', '{"name": "Training Base Foxtrot", "location": "Southern Sector", "lat": 33.8000, "lon": 109.8000, "capacity": 16, "status": "limited"}'),
('54000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000005', '{"name": "Emergency Base Golf", "location": "Central Sector", "lat": 34.6000, "lon": 109.6000, "capacity": 8, "status": "standby"}'),
('54000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000005', '{"name": "Strategic Base Hotel", "location": "Deep Rear", "lat": 33.2000, "lon": 108.2000, "capacity": 40, "status": "operational"}'),
('54000000-0000-0000-0000-000000000009', '10000000-0000-0000-0000-000000000005', '{"name": "Tactical Base India", "location": "Forward Area", "lat": 35.2000, "lon": 110.2000, "capacity": 14, "status": "operational"}'),
('54000000-0000-0000-0000-000000000010', '10000000-0000-0000-0000-000000000005', '{"name": "Logistics Base Juliet", "location": "Supply Route", "lat": 34.3000, "lon": 109.3000, "capacity": 22, "status": "operational"}'),
('54000000-0000-0000-0000-000000000011', '10000000-0000-0000-0000-000000000005', '{"name": "Coastal Base Kilo", "location": "Coastline", "lat": 34.1000, "lon": 109.1000, "capacity": 26, "status": "operational"}'),
('54000000-0000-0000-0000-000000000012', '10000000-0000-0000-0000-000000000005', '{"name": "Mountain Base Lima", "location": "Mountain Region", "lat": 35.4000, "lon": 111.4000, "capacity": 10, "status": "operational"}');

-- ==========================================
-- 6. Instance Layer: Link Instances
-- ==========================================

-- 6.1 Fighter Participation in Missions
INSERT INTO `sys_link_instance` (`id`, `link_type_id`, `source_instance_id`, `target_instance_id`, `properties`) VALUES
('60000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000001', '52000000-0000-0000-0000-000000000001', '{"role": "leader", "status": "active"}'),
('60000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000002', '52000000-0000-0000-0000-000000000001', '{"role": "wingman", "status": "active"}'),
('60000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000003', '52000000-0000-0000-0000-000000000001', '{"role": "wingman", "status": "active"}'),
('60000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000004', '52000000-0000-0000-0000-000000000005', '{"role": "leader", "status": "active"}'),
('60000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000005', '52000000-0000-0000-0000-000000000005', '{"role": "wingman", "status": "active"}'),
('60000000-0000-0000-0000-000000000006', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000008', '52000000-0000-0000-0000-000000000002', '{"role": "leader", "status": "assigned"}'),
('60000000-0000-0000-0000-000000000007', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000009', '52000000-0000-0000-0000-000000000002', '{"role": "wingman", "status": "assigned"}'),
('60000000-0000-0000-0000-000000000008', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000010', '52000000-0000-0000-0000-000000000009', '{"role": "leader", "status": "active"}'),
('60000000-0000-0000-0000-000000000009', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000011', '52000000-0000-0000-0000-000000000009', '{"role": "wingman", "status": "active"}'),
('60000000-0000-0000-0000-000000000010', '20000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000007', '52000000-0000-0000-0000-000000000004', '{"role": "leader", "status": "assigned"}');

-- 6.2 Mission Targeting
INSERT INTO `sys_link_instance` (`id`, `link_type_id`, `source_instance_id`, `target_instance_id`, `properties`) VALUES
('61000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000002', '52000000-0000-0000-0000-000000000001', '51000000-0000-0000-0000-000000000001', '{"priority": "primary"}'),
('61000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000002', '52000000-0000-0000-0000-000000000001', '51000000-0000-0000-0000-000000000004', '{"priority": "secondary"}'),
('61000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000002', '52000000-0000-0000-0000-000000000005', '51000000-0000-0000-0000-000000000009', '{"priority": "primary"}'),
('61000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000002', '52000000-0000-0000-0000-000000000004', '51000000-0000-0000-0000-000000000008', '{"priority": "primary"}'),
('61000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000002', '52000000-0000-0000-0000-000000000008', '51000000-0000-0000-0000-000000000002', '{"priority": "primary"}'),
('61000000-0000-0000-0000-000000000006', '20000000-0000-0000-0000-000000000002', '52000000-0000-0000-0000-000000000008', '51000000-0000-0000-0000-000000000006', '{"priority": "secondary"}'),
('61000000-0000-0000-0000-000000000007', '20000000-0000-0000-0000-000000000002', '52000000-0000-0000-0000-000000000011', '51000000-0000-0000-0000-000000000001', '{"priority": "primary"}'),
('61000000-0000-0000-0000-000000000008', '20000000-0000-0000-0000-000000000002', '52000000-0000-0000-0000-000000000011', '51000000-0000-0000-0000-000000000011', '{"priority": "secondary"}'),
('61000000-0000-0000-0000-000000000009', '20000000-0000-0000-0000-000000000002', '52000000-0000-0000-0000-000000000006', '51000000-0000-0000-0000-000000000003', '{"priority": "primary"}'),
('61000000-0000-0000-0000-000000000010', '20000000-0000-0000-0000-000000000002', '52000000-0000-0000-0000-000000000007', '51000000-0000-0000-0000-000000000005', '{"priority": "primary"}');

-- 6.3 Fighter Stationed At Base
INSERT INTO `sys_link_instance` (`id`, `link_type_id`, `source_instance_id`, `target_instance_id`, `properties`) VALUES
('62000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000001', '54000000-0000-0000-0000-000000000001', '{"assigned_date": "2024-01-01"}'),
('62000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000002', '54000000-0000-0000-0000-000000000001', '{"assigned_date": "2024-01-01"}'),
('62000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000003', '54000000-0000-0000-0000-000000000003', '{"assigned_date": "2023-12-28"}'),
('62000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000004', '54000000-0000-0000-0000-000000000003', '{"assigned_date": "2023-12-28"}'),
('62000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000005', '54000000-0000-0000-0000-000000000001', '{"assigned_date": "2024-01-01"}'),
('62000000-0000-0000-0000-000000000006', '20000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000006', '54000000-0000-0000-0000-000000000001', '{"assigned_date": "2024-01-01"}'),
('62000000-0000-0000-0000-000000000007', '20000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000007', '54000000-0000-0000-0000-000000000002', '{"assigned_date": "2023-12-30"}'),
('62000000-0000-0000-0000-000000000008', '20000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000008', '54000000-0000-0000-0000-000000000002', '{"assigned_date": "2023-12-30"}'),
('62000000-0000-0000-0000-000000000009', '20000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000009', '54000000-0000-0000-0000-000000000004', '{"assigned_date": "2023-12-29"}'),
('62000000-0000-0000-0000-000000000010', '20000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000010', '54000000-0000-0000-0000-000000000004', '{"assigned_date": "2023-12-29"}'),
('62000000-0000-0000-0000-000000000011', '20000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000011', '54000000-0000-0000-0000-000000000003', '{"assigned_date": "2023-12-28"}'),
('62000000-0000-0000-0000-000000000012', '20000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000012', '54000000-0000-0000-0000-000000000005', '{"assigned_date": "2023-12-31"}');

-- 6.4 Intelligence On Target
INSERT INTO `sys_link_instance` (`id`, `link_type_id`, `source_instance_id`, `target_instance_id`, `properties`) VALUES
('63000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000004', '53000000-0000-0000-0000-000000000001', '51000000-0000-0000-0000-000000000001', '{"relevance": "high"}'),
('63000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000004', '53000000-0000-0000-0000-000000000002', '51000000-0000-0000-0000-000000000002', '{"relevance": "high"}'),
('63000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000004', '53000000-0000-0000-0000-000000000003', '51000000-0000-0000-0000-000000000003', '{"relevance": "medium"}'),
('63000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000004', '53000000-0000-0000-0000-000000000004', '51000000-0000-0000-0000-000000000004', '{"relevance": "high"}'),
('63000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000004', '53000000-0000-0000-0000-000000000005', '51000000-0000-0000-0000-000000000005', '{"relevance": "medium"}'),
('63000000-0000-0000-0000-000000000006', '20000000-0000-0000-0000-000000000004', '53000000-0000-0000-0000-000000000006', '51000000-0000-0000-0000-000000000006', '{"relevance": "high"}'),
('63000000-0000-0000-0000-000000000007', '20000000-0000-0000-0000-000000000004', '53000000-0000-0000-0000-000000000007', '51000000-0000-0000-0000-000000000007', '{"relevance": "low"}'),
('63000000-0000-0000-0000-000000000008', '20000000-0000-0000-0000-000000000004', '53000000-0000-0000-0000-000000000008', '51000000-0000-0000-0000-000000000008', '{"relevance": "high"}'),
('63000000-0000-0000-0000-000000000009', '20000000-0000-0000-0000-000000000004', '53000000-0000-0000-0000-000000000009', '51000000-0000-0000-0000-000000000009', '{"relevance": "medium"}'),
('63000000-0000-0000-0000-000000000010', '20000000-0000-0000-0000-000000000004', '53000000-0000-0000-0000-000000000010', '51000000-0000-0000-0000-000000000010', '{"relevance": "medium"}'),
('63000000-0000-0000-0000-000000000011', '20000000-0000-0000-0000-000000000004', '53000000-0000-0000-0000-000000000011', '51000000-0000-0000-0000-000000000011', '{"relevance": "high"}'),
('63000000-0000-0000-0000-000000000012', '20000000-0000-0000-0000-000000000004', '53000000-0000-0000-0000-000000000012', '51000000-0000-0000-0000-000000000012', '{"relevance": "low"}');

-- ==========================================
-- 6.5 Data Source Tables (Raw Data Sources)
-- ==========================================

INSERT INTO `sys_datasource_table` (`id`, `table_name`, `db_type`, `columns_schema`, `created_at`) VALUES
('d1000000-0000-0000-0000-000000000001', 'raw_fighter_data', 'MySQL', '[{"name": "f_id", "type": "varchar", "length": 36}, {"name": "f_model", "type": "varchar", "length": 50}, {"name": "current_fuel", "type": "int"}, {"name": "callsign", "type": "varchar", "length": 20}, {"name": "status", "type": "varchar", "length": 20}, {"name": "lat", "type": "decimal", "precision": 10, "scale": 6}, {"name": "lon", "type": "decimal", "precision": 10, "scale": 6}, {"name": "altitude", "type": "int"}, {"name": "weapons", "type": "json"}]', NOW()),
('d1000000-0000-0000-0000-000000000002', 'raw_target_data', 'MySQL', '[{"name": "t_id", "type": "varchar", "length": 36}, {"name": "name", "type": "varchar", "length": 100}, {"name": "threat_level", "type": "varchar", "length": 20}, {"name": "lat", "type": "decimal", "precision": 10, "scale": 6}, {"name": "lon", "type": "decimal", "precision": 10, "scale": 6}, {"name": "type", "type": "varchar", "length": 50}, {"name": "priority", "type": "int"}, {"name": "health", "type": "int"}]', NOW()),
('d1000000-0000-0000-0000-000000000003', 'raw_mission_log', 'MySQL', '[{"name": "m_code", "type": "varchar", "length": 50}, {"name": "name", "type": "varchar", "length": 100}, {"name": "type", "type": "varchar", "length": 50}, {"name": "status", "type": "varchar", "length": 20}, {"name": "priority", "type": "int"}, {"name": "start_time", "type": "datetime"}, {"name": "end_time", "type": "datetime"}]', NOW()),
('d1000000-0000-0000-0000-000000000004', 'raw_intelligence_data', 'MySQL', '[{"name": "i_id", "type": "varchar", "length": 36}, {"name": "source", "type": "varchar", "length": 50}, {"name": "classification", "type": "varchar", "length": 50}, {"name": "validity", "type": "datetime"}, {"name": "confidence", "type": "decimal", "precision": 3, "scale": 2}, {"name": "content", "type": "text"}]', NOW()),
('d1000000-0000-0000-0000-000000000005', 'raw_base_data', 'MySQL', '[{"name": "b_id", "type": "varchar", "length": 36}, {"name": "name", "type": "varchar", "length": 100}, {"name": "location", "type": "varchar", "length": 100}, {"name": "lat", "type": "decimal", "precision": 10, "scale": 6}, {"name": "lon", "type": "decimal", "precision": 10, "scale": 6}, {"name": "capacity", "type": "int"}, {"name": "status", "type": "varchar", "length": 20}]', NOW());

-- ==========================================
-- 7. Runtime & Testing Layer: Action Logs
-- ==========================================

INSERT INTO `sys_action_log` (`id`, `project_id`, `action_def_id`, `trigger_user_id`, `input_params`, `execution_status`, `error_message`, `duration_ms`, `created_at`) VALUES
('80000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', 'user-001', '{"source_id": "51000000-0000-0000-0000-000000000001", "params": {"weapon_type": "missile"}}', 'SUCCESS', NULL, 125, '2024-01-15 10:30:00'),
('80000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000002', 'user-001', '{"source_id": "50000000-0000-0000-0000-000000000001", "params": {"fuel_amount": 50}}', 'SUCCESS', NULL, 89, '2024-01-15 10:35:00'),
('80000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', 'user-002', '{"source_id": "51000000-0000-0000-0000-000000000002", "params": {"weapon_type": "bomb"}}', 'SUCCESS', NULL, 142, '2024-01-15 11:00:00'),
('80000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000003', 'user-001', '{"source_id": "54000000-0000-0000-0000-000000000001", "params": {"count": 4}}', 'SUCCESS', NULL, 203, '2024-01-15 11:15:00'),
('80000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', 'user-003', '{"source_id": "51000000-0000-0000-0000-000000000003", "params": {"weapon_type": "missile"}}', 'FAILED', 'Target not in range', 45, '2024-01-15 11:30:00'),
('80000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000004', 'user-002', '{"source_id": "53000000-0000-0000-0000-000000000001", "params": {"new_data": "Updated intelligence report"}}', 'SUCCESS', NULL, 67, '2024-01-15 12:00:00'),
('80000000-0000-0000-0000-000000000007', '00000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000005', 'user-001', '{"source_id": "52000000-0000-0000-0000-000000000001", "params": {"fighter_id": "50000000-0000-0000-0000-000000000001"}}', 'SUCCESS', NULL, 98, '2024-01-15 12:15:00'),
('80000000-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', 'user-003', '{"source_id": "51000000-0000-0000-0000-000000000004", "params": {"weapon_type": "cannon"}}', 'SUCCESS', NULL, 156, '2024-01-15 12:30:00');

-- ==========================================
-- 8. Runtime & Testing Layer: Test Scenarios
-- ==========================================

INSERT INTO `meta_test_scenario` (`id`, `project_id`, `name`, `steps_config`, `created_at`) VALUES
('90000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'Standard Strike Sequence', '[{"actionId": "40000000-0000-0000-0000-000000000001", "actionName": "execute_strike", "params": {"weapon_type": "missile"}, "sourceId": "51000000-0000-0000-0000-000000000001"}, {"actionId": "40000000-0000-0000-0000-000000000002", "actionName": "refuel", "params": {"fuel_amount": 50}, "sourceId": "50000000-0000-0000-0000-000000000001"}]', '2024-01-15 10:00:00'),
('90000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'Mission Assignment Flow', '[{"actionId": "40000000-0000-0000-0000-000000000005", "actionName": "assign_to_mission", "params": {}, "sourceId": "52000000-0000-0000-0000-000000000001"}, {"actionId": "40000000-0000-0000-0000-000000000008", "actionName": "check_mission", "params": {}, "sourceId": "52000000-0000-0000-0000-000000000001"}]', '2024-01-15 10:30:00'),
('90000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'Intelligence Update Sequence', '[{"actionId": "40000000-0000-0000-0000-000000000004", "actionName": "update_intel", "params": {"new_data": "Target coordinates verified"}, "sourceId": "53000000-0000-0000-0000-000000000001"}, {"actionId": "40000000-0000-0000-0000-000000000001", "actionName": "execute_strike", "params": {"weapon_type": "bomb"}, "sourceId": "51000000-0000-0000-0000-000000000002"}]', '2024-01-15 11:00:00'),
('90000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', 'Quick Reaction Alert', '[{"actionId": "40000000-0000-0000-0000-000000000003", "actionName": "scramble", "params": {"count": 4}, "sourceId": "54000000-0000-0000-0000-000000000001"}, {"actionId": "40000000-0000-0000-0000-000000000001", "actionName": "execute_strike", "params": {"weapon_type": "missile"}, "sourceId": "51000000-0000-0000-0000-000000000001"}]', '2024-01-15 11:30:00');

SET FOREIGN_KEY_CHECKS = 1;

