-- ===========================================
-- Seed: Function Execution Test Examples
-- Database: ontology_meta_new
-- 用于验证函数试运行功能的示例函数
-- ===========================================

-- Function: 简单计算（验证基础执行）
INSERT INTO meta_function_def (
    id, api_name, display_name, description,
    code_content, output_type, input_params_schema, project_id
) VALUES (
    'fn_test_simple_01',
    'test_simple_calc',
    '[测试] 简单计算',
    '验证基础执行：context.get 与算术运算',
    'def main(context):
    return context.get("x", 0) * 2
',
    'INTEGER',
    '[{"name": "x", "type": "number", "required": true, "description": "输入值"}]',
    'proj-integration-test-001'
) ON DUPLICATE KEY UPDATE
    display_name = VALUES(display_name),
    description = VALUES(description),
    code_content = VALUES(code_content),
    output_type = VALUES(output_type),
    input_params_schema = VALUES(input_params_schema),
    project_id = VALUES(project_id);


-- Function: 使用 stdlib（验证 math/json/datetime）
INSERT INTO meta_function_def (
    id, api_name, display_name, description,
    code_content, output_type, input_params_schema, project_id
) VALUES (
    'fn_test_stdlib_01',
    'test_stdlib_usage',
    '[测试] 标准库使用',
    '验证预加载标准库：math, json, datetime',
    'def main(context):
    n = context.get("n", 4)
    sqrt_val = math.sqrt(n)
    return {"sqrt": sqrt_val, "timestamp": str(datetime.datetime.now())[:19]}
',
    'OBJECT',
    '[{"name": "n", "type": "number", "required": false, "default": 4, "description": "开方数值"}]',
    'proj-integration-test-001'
) ON DUPLICATE KEY UPDATE
    display_name = VALUES(display_name),
    description = VALUES(description),
    code_content = VALUES(code_content),
    output_type = VALUES(output_type),
    input_params_schema = VALUES(input_params_schema),
    project_id = VALUES(project_id);


-- Function: print 输出（验证 stdout 捕获）
INSERT INTO meta_function_def (
    id, api_name, display_name, description,
    code_content, output_type, input_params_schema, project_id
) VALUES (
    'fn_test_stdout_01',
    'test_stdout_capture',
    '[测试] print 输出捕获',
    '验证 print 输出被正确捕获并返回',
    'def main(context):
    msg = context.get("msg", "Hello")
    print(f"[Test] {msg}")
    return 42
',
    'INTEGER',
    '[{"name": "msg", "type": "string", "required": false, "description": "要打印的消息"}]',
    'proj-integration-test-001'
) ON DUPLICATE KEY UPDATE
    display_name = VALUES(display_name),
    description = VALUES(description),
    code_content = VALUES(code_content),
    output_type = VALUES(output_type),
    input_params_schema = VALUES(input_params_schema),
    project_id = VALUES(project_id);
