# Function Execution 测试指南

## 运行后端测试

```bash
# 在 backend 目录下，激活虚拟环境后
cd backend
.\.venv\Scripts\activate   # Windows
pytest tests/test_function_examples.py -v
```

## 执行种子数据（添加测试用 Function）

```bash
cd backend
python run_seed_function_test_examples.py
```

## 前端试运行验证

1. 进入 **本体场景库** -> 选择项目 -> **函数** 列表
2. 找到 `[测试] 简单计算` / `[测试] 标准库使用` / `[测试] print 输出捕获`
3. 点击编辑 -> **Code** 页签
4. 在 Test Inputs 中填写参数，如 `{"x": 5}` 或 `{"n": 9}`
5. 点击 **运行**，验证结果和 stdout

### 预期失败示例（手动输入验证）

在 Code  tab 中可输入以下代码验证错误处理：

| 代码 | 预期错误 |
|------|----------|
| `def foo(): return 1` | Code must define a 'main(context)' function |
| `def main(ctx): return 1/0` | ZeroDivisionError |
| `def main(ctx): open('/tmp/x')` | NameError (open 被限制) |
