#!/bin/bash

# 确保脚本目录存在
mkdir -p .git/hooks

# 创建 pre-commit 钩子
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running pre-commit checks..."
./scripts/local_ci.sh
EOF

# 赋予执行权限
chmod +x .git/hooks/pre-commit
chmod +x scripts/local_ci.sh

echo "✅ Git hooks installed successfully!"
echo "Now 'scripts/local_ci.sh' will run automatically before every commit."
