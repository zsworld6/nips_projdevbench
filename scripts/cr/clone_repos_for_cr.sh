#!/usr/bin/env bash
# 从日志中提取仓库 URL 并克隆到对应目录
# Usage: ./clone_repos_for_cr.sh <agent> <model>

set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <agent> <model>"
    exit 1
fi

AGENT=$1
MODEL=$2

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

LOGS_DIR="${PROJECT_ROOT}/logs/${AGENT}/${MODEL}"

if [[ ! -d "${LOGS_DIR}" ]]; then
    echo "❌ Logs directory not found: ${LOGS_DIR}"
    exit 1
fi

echo "🔍 Scanning ${LOGS_DIR} for repository URLs..."

cloned=0
skipped=0

for problem_dir in "${LOGS_DIR}"/*/; do
    [[ -d "${problem_dir}" ]] || continue
    problem_id=$(basename "${problem_dir}")
    
    # 检查是否已有 oj-eval-* 目录
    existing_repo=$(find "${problem_dir}" -maxdepth 1 -type d -name "oj-eval-*" 2>/dev/null | head -1)
    if [[ -n "${existing_repo}" ]]; then
        echo "⏭️  Problem ${problem_id}: already has repo, skipping"
        skipped=$((skipped + 1))
        continue
    fi
    
    # 从日志中提取最新的仓库 URL
    repo_url=""
    for log_file in "${problem_dir}"/oj_eval_*.log; do
        [[ -f "${log_file}" ]] || continue
        url=$(grep -o 'https://github.com/[^[:space:]]*oj-eval-[^[:space:]]*' "${log_file}" 2>/dev/null | tail -1 || true)
        if [[ -n "${url}" ]]; then
            repo_url="${url}"
        fi
    done
    
    if [[ -z "${repo_url}" ]]; then
        echo "⚠️  Problem ${problem_id}: no repository URL found in logs"
        continue
    fi
    
    repo_name=$(basename "${repo_url}")
    target_dir="${problem_dir}/${repo_name}"
    
    echo "📥 Problem ${problem_id}: cloning ${repo_url}"
    if git clone --depth 1 "${repo_url}" "${target_dir}" 2>/dev/null; then
        echo "   ✅ Cloned to ${target_dir}"
        cloned=$((cloned + 1))
    else
        echo "   ❌ Failed to clone (repo may be private or deleted)"
    fi
done

echo ""
echo "========================================="
echo "✅ Clone completed"
echo "   Cloned: ${cloned}"
echo "   Skipped (already exists): ${skipped}"
echo "========================================="
