#!/usr/bin/env bash
set -euo pipefail

# 在 Docker 中运行 Claude 审查脚本

show_usage() {
  cat <<'EOF'
Usage: run_claude_review_docker.sh <agent_name> <model_name> <claude_model>

This script runs the Claude review in a Docker container.
It mounts the necessary directories and runs run_claude_review.sh inside the container.

Note: The <claude_model> parameter specifies which model to use for review.
      Typically "deepseek-chat" is used when using DeepSeek API via ANTHROPIC_BASE_URL.

Example:
  ./run_claude_review_docker.sh augment GPT-5 deepseek-chat
  ./run_claude_review_docker.sh claude-code deepseek-chat deepseek-chat
EOF
  exit 1
}

if [[ $# -ne 3 ]]; then
  show_usage
fi

AGENT_NAME=$1
MODEL_NAME=$2
CLAUDE_MODEL=$3

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

# 检查配置文件
CONFIG_FILE="${PROJECT_ROOT}/config/evaluate.env"
if [[ ! -f "${CONFIG_FILE}" ]]; then
  echo "❌ Config file not found: ${CONFIG_FILE}" >&2
  exit 1
fi

# 检查 Docker 镜像是否存在（优先使用 llm-claude 镜像，如果没有则使用 agent-runner）
DOCKER_IMAGE=""
if docker image inspect ojbench-llm-claude:latest &>/dev/null 2>&1; then
  DOCKER_IMAGE="ojbench-llm-claude:latest"
  echo "✅ Using Docker image: ${DOCKER_IMAGE}"
elif docker image inspect projdevbench-runner:latest &>/dev/null 2>&1; then
  DOCKER_IMAGE="projdevbench-runner:latest"
  echo "✅ Using Docker image: ${DOCKER_IMAGE}"
else
  echo "❌ No suitable Docker image found"
  echo "Please build one of the following images:"
  echo "  - ojbench-llm-claude:latest (recommended)"
  echo "  - projdevbench-runner:latest"
  exit 1
fi

echo "========================================="
echo "🐳 Running Claude Review in Docker"
echo "========================================="
echo "Agent: ${AGENT_NAME}"
echo "Model: ${MODEL_NAME}"
echo "Claude Model: ${CLAUDE_MODEL}"
echo "Docker Image: ${DOCKER_IMAGE}"
echo ""

# 从配置文件读取环境变量
set -a
source "${CONFIG_FILE}"
set +a

# 构建环境变量参数
DOCKER_ENV_ARGS=(
  -e "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}"
  -e "ANTHROPIC_BASE_URL=${ANTHROPIC_BASE_URL:-}"
  -e "AGENT_NAME=${AGENT_NAME}"
  -e "MODEL_NAME=${MODEL_NAME}"
  -e "CLAUDE_MODEL=${CLAUDE_MODEL}"
  -e "ONLY_PROBLEMS=${ONLY_PROBLEMS:-}"
)

# 根据镜像类型设置挂载路径和工作目录
if [[ "${DOCKER_IMAGE}" == "ojbench-llm-claude"* ]]; then
  WORK_DIR="/opt/ojbench"
  # 对于 llm-claude 镜像，需要挂载到 /opt/ojbench
  DOCKER_MOUNT_ARGS=(
    -v "${PROJECT_ROOT}:/opt/ojbench:rw"
    -v "${CONFIG_FILE}:/opt/ojbench/config/evaluate.env:ro"
  )
else
  WORK_DIR="/workspace"
  # 对于 agent-runner 镜像，使用 /workspace
  DOCKER_MOUNT_ARGS=(
    -v "${PROJECT_ROOT}:/workspace:rw"
    -v "${CONFIG_FILE}:/workspace/config/evaluate.env:ro"
  )
fi

# 在 Docker 容器中运行脚本
docker run --rm \
  "${DOCKER_MOUNT_ARGS[@]}" \
  "${DOCKER_ENV_ARGS[@]}" \
  -w "${WORK_DIR}" \
  --entrypoint /bin/bash \
  "${DOCKER_IMAGE}" \
  -c "bash scripts/cr/docker_script/run_claude_review.sh '${AGENT_NAME}' '${MODEL_NAME}' '${CLAUDE_MODEL}'"

echo ""
echo "========================================="
echo "✅ Docker execution completed"
echo "========================================="

