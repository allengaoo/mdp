-- ============================================================
-- Object 360 View Configuration Seed Data
-- MDP Platform V3.1 - Low-Code Object Profile View
-- ============================================================

-- Use the metadata database
-- Assumes tables: app_definition, app_module, app_widget exist

-- ============================================================
-- Step 1: Create App Definition for Target 360 Profile
-- ============================================================

-- First, check if already exists and delete for idempotency
DELETE FROM app_widget WHERE module_id IN (
    SELECT id FROM app_module WHERE app_id IN (
        SELECT id FROM app_definition WHERE name = 'Target 360 Profile'
    )
);
DELETE FROM app_module WHERE app_id IN (
    SELECT id FROM app_definition WHERE name = 'Target 360 Profile'
);
DELETE FROM app_definition WHERE name = 'Target 360 Profile';

-- Insert App Definition
INSERT INTO app_definition (id, project_id, name, app_type, global_config, created_by, created_at, updated_at)
VALUES (
    'app-target-360',
    'default-project',  -- Assuming a default project exists
    'Target 360 Profile',
    'EXPLORER',
    '{"object_type": "Target", "theme": "dark", "refresh_interval": 30000}',
    'system',
    NOW(),
    NOW()
);

-- ============================================================
-- Step 2: Create Modules (Layout Sections)
-- ============================================================

-- Module A: Identity (Left Panel - 25%)
INSERT INTO app_module (id, app_id, name, layout_config, display_order)
VALUES (
    'mod-identity',
    'app-target-360',
    'Identity',
    '{"width": 6, "position": "left", "collapsible": true}',
    1
);

-- Module B: Context (Center Panel - 50%)
INSERT INTO app_module (id, app_id, name, layout_config, display_order)
VALUES (
    'mod-context',
    'app-target-360',
    'Context',
    '{"width": 12, "position": "center", "scrollable": true}',
    2
);

-- Module C: Intelligence (Right Panel - 25%)
INSERT INTO app_module (id, app_id, name, layout_config, display_order)
VALUES (
    'mod-intelligence',
    'app-target-360',
    'Intelligence',
    '{"width": 6, "position": "right", "collapsible": true}',
    3
);

-- ============================================================
-- Step 3: Create Widgets (Components)
-- ============================================================

-- Widget 1: Property List (In Module A - Identity)
INSERT INTO app_widget (id, module_id, widget_type, data_binding, view_config, position_config)
VALUES (
    'wgt-props',
    'mod-identity',
    'PROPERTY_LIST',
    '{"fields": ["mmsi", "imo", "name", "country", "status", "threat_level", "speed", "heading"]}',
    '{"title": "基本信息", "layout": "vertical", "labelWidth": 100}',
    '{"order": 1, "height": "auto"}'
);

-- Widget 2: Mini Map (In Module A - Identity)
INSERT INTO app_widget (id, module_id, widget_type, data_binding, view_config, position_config)
VALUES (
    'wgt-minimap',
    'mod-identity',
    'MINI_MAP',
    '{"lat": "latitude", "lon": "longitude", "heading": "heading"}',
    '{"title": "当前位置", "zoom": 12, "showTrack": true}',
    '{"order": 2, "height": 200}'
);

-- Widget 3: Timeline (In Module B - Context)
INSERT INTO app_widget (id, module_id, widget_type, data_binding, view_config, position_config)
VALUES (
    'wgt-timeline',
    'mod-context',
    'TIMELINE',
    '{"sources": ["sys_action_log", "linked_events"], "time_field": "created_at"}',
    '{"title": "活动时间线", "mode": "left", "showIcon": true}',
    '{"order": 1, "height": 400}'
);

-- Widget 4: Relation List (In Module B - Context)
INSERT INTO app_widget (id, module_id, widget_type, data_binding, view_config, position_config)
VALUES (
    'wgt-relations',
    'mod-context',
    'RELATION_LIST',
    '{"link_types": ["has_mission", "corroborated_by", "detected_by", "docked_at"]}',
    '{"title": "关联关系", "showType": true, "expandable": true}',
    '{"order": 2, "height": "auto"}'
);

-- Widget 5: Media Carousel (In Module C - Intelligence)
INSERT INTO app_widget (id, module_id, widget_type, data_binding, view_config, position_config)
VALUES (
    'wgt-media',
    'mod-intelligence',
    'MEDIA_CAROUSEL',
    '{"link_type": "has_recon_image", "media_types": ["image", "video"]}',
    '{"title": "侦察影像", "autoPlay": false, "showThumbnails": true}',
    '{"order": 1, "height": 250}'
);

-- Widget 6: AI Insights (In Module C - Intelligence)
INSERT INTO app_widget (id, module_id, widget_type, data_binding, view_config, position_config)
VALUES (
    'wgt-ai',
    'mod-intelligence',
    'AI_INSIGHTS',
    '{"vector_field": "image_vector", "top_k": 5, "similarity_threshold": 0.7}',
    '{"title": "AI 智能分析", "showScore": true, "allowCompare": true}',
    '{"order": 2, "height": "auto"}'
);

-- Widget 7: Stats Card (In Module A - Identity) - Additional
INSERT INTO app_widget (id, module_id, widget_type, data_binding, view_config, position_config)
VALUES (
    'wgt-stats',
    'mod-identity',
    'STAT_CARD',
    '{"metrics": ["total_sightings", "last_seen_days", "threat_score"]}',
    '{"title": "统计摘要", "layout": "grid", "columns": 3}',
    '{"order": 0, "height": 80}'
);

-- ============================================================
-- Verify: Show inserted data
-- ============================================================
SELECT 'App Definition:' as section;
SELECT id, name, app_type, global_config FROM app_definition WHERE id = 'app-target-360';

SELECT 'Modules:' as section;
SELECT id, name, layout_config, display_order FROM app_module WHERE app_id = 'app-target-360' ORDER BY display_order;

SELECT 'Widgets:' as section;
SELECT w.id, m.name as module_name, w.widget_type, w.position_config
FROM app_widget w
JOIN app_module m ON w.module_id = m.id
WHERE m.app_id = 'app-target-360'
ORDER BY m.display_order, JSON_EXTRACT(w.position_config, '$.order');
