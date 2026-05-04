#!/bin/bash
set -e

# --- 环境变量验证 ---
: "${PROBLEM_ID?Required: PROBLEM_ID}"
: "${OJ_PROBLEM_ID?Required: OJ_PROBLEM_ID}"
: "${AGENT_TYPE?Required: AGENT_TYPE}"
: "${GITHUB_TOKEN?Required: GITHUB_TOKEN}"
: "${OJ_TOKEN?Required: OJ_TOKEN}"

# --- 配置变量 ---
# 使用传入的TIMESTAMP，如果没有则退出
if [ -z "${TIMESTAMP}" ]; then
    echo "❌ TIMESTAMP is required"
    exit 1
fi

REPO_NAME="oj-eval-${AGENT_TYPE}-${PROBLEM_ID}-${TIMESTAMP}"
GITHUB_USER="${GITHUB_USER:-your-oj-account}"
WORKSPACE_DIR="/workspace/problem_${PROBLEM_ID}"

echo "========================================="
echo "OJBench Agent Repository Management Evaluation"
echo "Problem ID: ${PROBLEM_ID} (OJ: ${OJ_PROBLEM_ID})"
echo "Agent Type: ${AGENT_TYPE}"
echo "Timestamp: ${TIMESTAMP}"
echo "Repository: ${REPO_NAME}"
echo "Workspace: ${WORKSPACE_DIR}"
echo "========================================="

# --- 1. 环境配置 ---
export GITHUB_TOKEN
export OJ_TOKEN

# --- 2. 准备工作空间 ---
echo "📁 Setting up workspace from problem directory..."
mkdir -p "$WORKSPACE_DIR"
cd "$WORKSPACE_DIR"

# 复制problem文件夹内容到工作空间（从只读挂载复制到可写工作空间）
if [ -d "/problems/${PROBLEM_ID}" ]; then
    echo "📋 Copying problem files from read-only mount to workspace..."
    echo "Source: /problems/${PROBLEM_ID} (read-only)"
    echo "Destination: $(pwd) (writable)"
    
    # 复制所有文件和隐藏文件
    cp -r "/problems/${PROBLEM_ID}"/* . 2>/dev/null || true
    cp -r "/problems/${PROBLEM_ID}"/.[^.]* . 2>/dev/null || true
    
    # 确保工作空间中的文件是可写的
    chmod -R u+w . 2>/dev/null || true
    
    echo "✅ Problem files copied to workspace successfully"
    echo "📂 Files in workspace:"
    ls -la
    echo ""
    echo "✅ AI can now freely modify files in the workspace"
    echo "🔒 Original problem files remain protected (read-only)"
else
    echo "⚠️ No problem directory found at /problems/${PROBLEM_ID}"
    echo "Creating minimal workspace..."
    echo "# Problem ${PROBLEM_ID}" > README.md
    echo "OJ Problem ID: ${OJ_PROBLEM_ID}" >> README.md
fi

git config --global user.name "OJ-Evaluation-Agent"
git config --global user.email "agent@ojeval.com"

echo "========================================="
echo "OJBench Agent Repository Management Evaluation"
echo "Problem ID: ${PROBLEM_ID} (OJ: ${OJ_PROBLEM_ID})"
echo "Agent Type: ${AGENT_TYPE}"
echo "Timestamp: ${TIMESTAMP}"
echo "Repository: ${REPO_NAME}"
echo "Workspace: ${WORKSPACE_DIR}"
echo "========================================="

echo "🔧 Initializing Git repository..."
# 进入工作目录/workspace/problem_${PROBLEM_ID}
cd "$WORKSPACE_DIR"
git init
git add .
git commit -m "Initial commit: Problem ${PROBLEM_ID} setup" --allow-empty

# --- 4. 创建远程GitHub仓库并连接 ---
echo "📦 Creating remote GitHub repository..."
gh repo create ${GITHUB_USER}/${REPO_NAME} --public --source=. --push
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo "✅ Repository created: ${REPO_URL}"

# 配置Git远程URL使用Token认证 ---
echo "🔑 Configuring Git remote URL with token authentication..."
git remote set-url origin https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git
echo "✅ Git remote URL configured for authentication"

# --- 复制数据目录到工作空间 ---
echo "📊 Copying data directory to workspace..."
if [ -d "/data_readonly/${PROBLEM_ID}" ]; then
    echo "Source: /data_readonly/${PROBLEM_ID} (read-only mount)"
    echo "Destination: /workspace/data/${PROBLEM_ID} (writable workspace)"
    
    mkdir -p "/workspace/data/${PROBLEM_ID}"
    cp -r "/data_readonly/${PROBLEM_ID}"/* "/workspace/data/${PROBLEM_ID}/" 2>/dev/null || true
    
    echo "✅ Data copied successfully"
    echo "📂 Data size: $(du -sh /workspace/data/${PROBLEM_ID} 2>/dev/null | cut -f1)"
else
    echo "⚠️ No data directory found at /data_readonly/${PROBLEM_ID}"
fi

