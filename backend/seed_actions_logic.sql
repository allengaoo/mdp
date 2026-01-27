-- ===========================================
-- Seed Data: Actions & Logic for Maritime Situational Awareness
-- Database: ontology_meta_new
-- ===========================================

-- ===========================================
-- Function 1: Intelligence Verification
-- ===========================================
INSERT INTO meta_function_def (
    id, api_name, display_name, description, 
    code_content, output_type, input_params_schema
) VALUES (
    'fn_intel_verify_01',
    'intel_verify',
    '情报验证',
    '验证情报报告，如验证通过则升级关联目标的威胁等级为HIGH',
    '# Intelligence Verification Function
# 验证情报报告，关联目标威胁等级升级

def main(context):
    """
    验证情报报告并更新关联目标的威胁等级
    
    Args:
        context: {
            "report_id": str,  # 情报报告ID
            "status": str      # 验证状态: VERIFIED / REJECTED
        }
    """
    report_id = context.get("report_id")
    status = context.get("status", "VERIFIED")
    
    if not report_id:
        return {"success": False, "message": "Missing report_id parameter"}
    
    print(f"[Intel Verify] Processing report: {report_id}")
    print(f"[Intel Verify] New status: {status}")
    
    # Simulate getting report object
    # In production: report = get_object("IntelReport", report_id)
    
    result_messages = [f"Report {report_id} status updated to {status}"]
    
    if status == "VERIFIED":
        # Simulate finding linked target and escalating threat level
        # In production: 
        # links = get_links(report_id, "corroborates_target")
        # target = get_object("Target", links[0]["target_id"])
        # update_object("Target", target_id, {"threat_level": "HIGH"})
        
        print("[Intel Verify] Escalating linked target to HIGH threat level")
        result_messages.append("Linked target escalated to HIGH threat level")
        
        return {
            "success": True,
            "report_id": report_id,
            "status": status,
            "threat_escalated": True,
            "message": " | ".join(result_messages)
        }
    
    return {
        "success": True,
        "report_id": report_id,
        "status": status,
        "threat_escalated": False,
        "message": " | ".join(result_messages)
    }
',
    'OBJECT',
    '[
        {"name": "report_id", "type": "string", "required": true, "description": "情报报告ID"},
        {"name": "status", "type": "string", "required": false, "default": "VERIFIED", "description": "验证状态 (VERIFIED/REJECTED)"}
    ]'
) ON DUPLICATE KEY UPDATE 
    display_name = VALUES(display_name),
    description = VALUES(description),
    code_content = VALUES(code_content),
    output_type = VALUES(output_type),
    input_params_schema = VALUES(input_params_schema);


-- ===========================================
-- Function 2: Auto-Assign Strike Mission
-- ===========================================
INSERT INTO meta_function_def (
    id, api_name, display_name, description, 
    code_content, output_type, input_params_schema
) VALUES (
    'fn_mission_assign_01',
    'mission_assign',
    '任务自动分配',
    '根据作战计划创建任务，查询可用J-20战机并分配到任务',
    '# Auto-Assign Strike Mission Function
# 自动分配打击任务

def main(context):
    """
    创建打击任务并分配可用战机
    
    Args:
        context: {
            "plan_id": str,       # 作战计划ID
            "mission_type": str,  # 任务类型
            "required_jets": int  # 需要的战机数量
        }
    """
    plan_id = context.get("plan_id")
    mission_type = context.get("mission_type", "Precision Strike")
    required_jets = context.get("required_jets", 2)
    
    if not plan_id:
        return {"success": False, "message": "Missing plan_id parameter"}
    
    print(f"[Mission Assign] Processing plan: {plan_id}")
    print(f"[Mission Assign] Mission type: {mission_type}")
    print(f"[Mission Assign] Required jets: {required_jets}")
    
    # Simulate creating mission
    mission_code = f"MSN-{plan_id[:8]}-ALPHA"
    print(f"[Mission Assign] Created mission: {mission_code}")
    
    # Simulate querying available J-20 fighters
    # In production:
    # available_jets = ontology.search("FighterJet")
    #     .filter(model="J-20", status="READY")
    #     .limit(required_jets)
    
    # Mock available jets
    available_jets = [
        {"id": "jet-001", "tail_number": "J20-1001", "status": "READY"},
        {"id": "jet-002", "tail_number": "J20-1002", "status": "READY"},
        {"id": "jet-003", "tail_number": "J20-1003", "status": "READY"},
    ][:required_jets]
    
    if len(available_jets) < required_jets:
        error_msg = f"Insufficient J-20 assets: need {required_jets}, found {len(available_jets)}"
        print(f"[Mission Assign] ERROR: {error_msg}")
        raise Exception(error_msg)
    
    # Assign jets to mission
    assigned_jets = []
    for jet in available_jets:
        # In production: 
        # mission.link("assigned_assets", jet)
        # jet.status = "ASSIGNED"
        # jet.save()
        assigned_jets.append(jet["tail_number"])
        print(f"[Mission Assign] Assigned jet: {jet[\"tail_number\"]}")
    
    return {
        "success": True,
        "mission_code": mission_code,
        "mission_type": mission_type,
        "assigned_jets": assigned_jets,
        "jet_count": len(assigned_jets),
        "message": f"Mission {mission_code} created with {len(assigned_jets)} jets assigned"
    }
',
    'OBJECT',
    '[
        {"name": "plan_id", "type": "string", "required": true, "description": "作战计划ID"},
        {"name": "mission_type", "type": "string", "required": false, "default": "Precision Strike", "description": "任务类型"},
        {"name": "required_jets", "type": "number", "required": false, "default": 2, "description": "需要的战机数量"}
    ]'
) ON DUPLICATE KEY UPDATE 
    display_name = VALUES(display_name),
    description = VALUES(description),
    code_content = VALUES(code_content),
    output_type = VALUES(output_type),
    input_params_schema = VALUES(input_params_schema);


-- ===========================================
-- Function 3: AI Satellite Analysis (Multimodal)
-- ===========================================
INSERT INTO meta_function_def (
    id, api_name, display_name, description, 
    code_content, output_type, input_params_schema
) VALUES (
    'fn_ai_recon_01',
    'ai_recon_analyze',
    'AI卫星图像分析',
    '对侦察图像进行AI分析，识别目标并更新坐标信息',
    '# AI Satellite Analysis Function (Multimodal)
# AI卫星图像分析

def main(context):
    """
    对卫星/侦察图像进行AI分析
    
    Args:
        context: {
            "image_id": str,           # 图像ID
            "confidence_threshold": float  # 置信度阈值
        }
    """
    image_id = context.get("image_id")
    confidence_threshold = context.get("confidence_threshold", 0.95)
    
    if not image_id:
        return {"success": False, "message": "Missing image_id parameter"}
    
    print(f"[AI Recon] Analyzing image: {image_id}")
    print(f"[AI Recon] Confidence threshold: {confidence_threshold}")
    
    # Simulate getting image object and S3 path
    # In production:
    # img_obj = get_object("ReconImage", image_id)
    # s3_path = img_obj.s3_path
    
    s3_path = f"s3://mdp-recon-images/{image_id}.jpg"
    print(f"[AI Recon] Image path: {s3_path}")
    
    # Simulate AI inference
    # In production:
    # detection = cv_model_client.detect_objects(s3_path)
    
    # Mock AI detection result
    detection = {
        "confidence": 0.97,
        "detected_objects": ["vessel", "wake_pattern"],
        "lat": 25.0340,
        "lon": 121.5645,
        "heading": 45.2
    }
    
    print(f"[AI Recon] Detection confidence: {detection[\"confidence\"]}")
    print(f"[AI Recon] Detected objects: {detection[\"detected_objects\"]}")
    
    if detection["confidence"] >= confidence_threshold:
        # High confidence - update target coordinates
        # In production:
        # target = img_obj.get_link("depicts_target")
        # target.lat = detection["lat"]
        # target.lon = detection["lon"]
        # target.save()
        
        print(f"[AI Recon] Updating target coordinates: ({detection[\"lat\"]}, {detection[\"lon\"]})")
        
        return {
            "success": True,
            "image_id": image_id,
            "confidence": detection["confidence"],
            "detected_objects": detection["detected_objects"],
            "coordinates_updated": True,
            "new_lat": detection["lat"],
            "new_lon": detection["lon"],
            "message": f"Target coordinates corrected by AI (Confidence: {detection[\"confidence\"]:.2%})"
        }
    else:
        print(f"[AI Recon] Low confidence ({detection[\"confidence\"]:.2%}), no changes made")
        return {
            "success": True,
            "image_id": image_id,
            "confidence": detection["confidence"],
            "detected_objects": detection["detected_objects"],
            "coordinates_updated": False,
            "message": f"Low confidence detection ({detection[\"confidence\"]:.2%}), no changes made"
        }
',
    'OBJECT',
    '[
        {"name": "image_id", "type": "string", "required": true, "description": "侦察图像ID"},
        {"name": "confidence_threshold", "type": "number", "required": false, "default": 0.95, "description": "AI置信度阈值 (0-1)"}
    ]'
) ON DUPLICATE KEY UPDATE 
    display_name = VALUES(display_name),
    description = VALUES(description),
    code_content = VALUES(code_content),
    output_type = VALUES(output_type),
    input_params_schema = VALUES(input_params_schema);


-- ===========================================
-- Action 1: Verify Intel Report
-- ===========================================
INSERT INTO meta_action_def (id, api_name, display_name, backing_function_id)
VALUES (
    'act_intel_verify_01',
    'verify_intel_report',
    '验证情报报告',
    'fn_intel_verify_01'
) ON DUPLICATE KEY UPDATE 
    display_name = VALUES(display_name),
    backing_function_id = VALUES(backing_function_id);


-- ===========================================
-- Action 2: Execute Strike Plan
-- ===========================================
INSERT INTO meta_action_def (id, api_name, display_name, backing_function_id)
VALUES (
    'act_mission_assign_01',
    'execute_strike_plan',
    '执行打击计划',
    'fn_mission_assign_01'
) ON DUPLICATE KEY UPDATE 
    display_name = VALUES(display_name),
    backing_function_id = VALUES(backing_function_id);


-- ===========================================
-- Action 3: Analyze Satellite Image
-- ===========================================
INSERT INTO meta_action_def (id, api_name, display_name, backing_function_id)
VALUES (
    'act_ai_recon_01',
    'analyze_satellite_image',
    '分析卫星图像',
    'fn_ai_recon_01'
) ON DUPLICATE KEY UPDATE 
    display_name = VALUES(display_name),
    backing_function_id = VALUES(backing_function_id);


-- ===========================================
-- Verification Query
-- ===========================================
-- SELECT 
--     a.id, a.api_name, a.display_name,
--     f.api_name as function_api_name, f.display_name as function_display_name
-- FROM meta_action_def a
-- LEFT JOIN meta_function_def f ON a.backing_function_id = f.id
-- WHERE a.id IN ('act_intel_verify_01', 'act_mission_assign_01', 'act_ai_recon_01');
