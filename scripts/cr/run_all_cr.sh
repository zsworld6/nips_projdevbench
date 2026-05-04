#!/usr/bin/env bash
set -euo pipefail

# 运行完整的 Code Review 流程
# 1. 运行 Python 规则检查 (evaluate_results.py)
# 2. 运行 LLM 评审 (run_claude_review_docker.sh)
# 3. 合并结果 (merge_cr_results.py) -> all_result.json

show_usage() {
  cat <<'EOF'
Usage: run_all_cr.sh [options] <agent_name> <model_name> [claude_model]

Run complete Code Review pipeline:
  1. Python-based rule checks (evaluate_results.py)
  2. LLM-as-a-Judge review (run_claude_review_docker.sh)
  3. Merge results (merge_cr_results.py) -> all_result.json

Arguments:
  agent_name    Name of the agent (e.g., augment, claude-code)
  model_name    Name of the model (e.g., GPT-5, deepseek-chat)
  claude_model  Model for LLM review (default: deepseek-chat)

Options:
  --all              Run for all agent/model combinations under logs/
  --skip-python      Skip Python-based checks
  --skip-llm         Skip LLM-as-a-Judge review
  --skip-merge       Skip merging results into all_result.json
  --only-problems    Comma-separated list of problem IDs to process (e.g., "003,020")
  -h, --help         Show this help message

Examples:
  # Run full CR for a specific agent/model
  ./run_all_cr.sh augment GPT-5 deepseek-chat

  # Run full CR for all agent/model combinations
  ./run_all_cr.sh --all

  # Run only Python checks for a specific agent/model
  ./run_all_cr.sh --skip-llm augment GPT-5

  # Run only LLM review for a specific agent/model
  ./run_all_cr.sh --skip-python augment GPT-5 deepseek-chat

  # Run for specific problems only
  ./run_all_cr.sh --only-problems "003,020" augment GPT-5 deepseek-chat
EOF
  exit 1
}

# Parse options
RUN_ALL=false
SKIP_PYTHON=false
SKIP_LLM=false
SKIP_MERGE=false
ONLY_PROBLEMS=""
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --all)
      RUN_ALL=true
      shift
      ;;
    --skip-python)
      SKIP_PYTHON=true
      shift
      ;;
    --skip-llm)
      SKIP_LLM=true
      shift
      ;;
    --skip-merge)
      SKIP_MERGE=true
      shift
      ;;
    --only-problems)
      ONLY_PROBLEMS="$2"
      shift 2
      ;;
    -h|--help)
      show_usage
      ;;
    -*)
      echo "Unknown option: $1" >&2
      show_usage
      ;;
    *)
      POSITIONAL_ARGS+=("$1")
      shift
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}"

# Validate arguments
if [[ "$RUN_ALL" == false ]]; then
  if [[ $# -lt 2 ]]; then
    echo "❌ Error: agent_name and model_name are required" >&2
    show_usage
  fi
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "========================================="
echo "🔍 Code Review Pipeline"
echo "========================================="
echo "Project root: ${PROJECT_ROOT}"
echo ""

# Function to run CR for a single agent/model
run_cr_for_agent_model() {
  local agent_name="$1"
  local model_name="$2"
  local claude_model="${3:-deepseek-chat}"

  local results_dir="${PROJECT_ROOT}/logs/${agent_name}/${model_name}"

  if [[ ! -d "${results_dir}" ]]; then
    echo "⚠️  Results directory not found: ${results_dir}, skipping." >&2
    return 1
  fi

  echo ""
  echo "========================================="
  echo "📦 Processing: ${agent_name}/${model_name}"
  echo "========================================="

  # Step 1: Run Python-based checks
  if [[ "$SKIP_PYTHON" == false ]]; then
    echo ""
    echo "🐍 Step 1: Running Python-based rule checks..."
    echo "-----------------------------------------"
    python3 "${SCRIPT_DIR}/evaluate_results.py" \
      "${results_dir}" \
      --scripts-root "${SCRIPT_DIR}"
    echo "✅ Python checks completed"
  else
    echo ""
    echo "⏭️  Skipping Python-based checks (--skip-python)"
  fi

  # Step 2: Run LLM-as-a-Judge review
  if [[ "$SKIP_LLM" == false ]]; then
    echo ""
    echo "🤖 Step 2: Running LLM-as-a-Judge review..."
    echo "-----------------------------------------"
    
    # Export ONLY_PROBLEMS if specified
    if [[ -n "${ONLY_PROBLEMS}" ]]; then
      export ONLY_PROBLEMS
    fi
    
    bash "${SCRIPT_DIR}/docker_script/run_claude_review_docker.sh" \
      "${agent_name}" \
      "${model_name}" \
      "${claude_model}"
    echo "✅ LLM review completed"
  else
    echo ""
    echo "⏭️  Skipping LLM review (--skip-llm)"
  fi

  # Step 3: Merge results into all_result.json
  if [[ "$SKIP_MERGE" == false ]]; then
    echo ""
    echo "📊 Step 3: Merging results into all_result.json..."
    echo "-----------------------------------------"
    
    local cr_result_dir="${PROJECT_ROOT}/cr_result/${agent_name}/${model_name}"
    
    if [[ -d "${cr_result_dir}" ]]; then
      python3 "${SCRIPT_DIR}/merge_cr_results.py" "${cr_result_dir}"
      echo "✅ Results merged"
    else
      echo "⚠️  CR result directory not found: ${cr_result_dir}"
    fi
  else
    echo ""
    echo "⏭️  Skipping merge (--skip-merge)"
  fi

  return 0
}

# Main execution
if [[ "$RUN_ALL" == true ]]; then
  # Run for all agent/model combinations
  LOGS_ROOT="${PROJECT_ROOT}/logs"
  
  if [[ ! -d "${LOGS_ROOT}" ]]; then
    echo "❌ Logs directory not found: ${LOGS_ROOT}" >&2
    exit 1
  fi

  CLAUDE_MODEL="${1:-deepseek-chat}"
  
  echo "Running CR for all agent/model combinations..."
  echo "LLM Model: ${CLAUDE_MODEL}"
  
  total_count=0
  success_count=0
  
  for agent_dir in "${LOGS_ROOT}"/*/; do
    [[ -d "${agent_dir}" ]] || continue
    agent_name="$(basename "${agent_dir}")"
    
    for model_dir in "${agent_dir}"/*/; do
      [[ -d "${model_dir}" ]] || continue
      model_name="$(basename "${model_dir}")"
      
      total_count=$((total_count + 1))
      
      if run_cr_for_agent_model "${agent_name}" "${model_name}" "${CLAUDE_MODEL}"; then
        success_count=$((success_count + 1))
      fi
    done
  done
  
  echo ""
  echo "========================================="
  echo "✅ All Code Review completed"
  echo "Processed: ${success_count}/${total_count} agent/model combinations"
  echo "========================================="
  
else
  # Run for a single agent/model
  AGENT_NAME="$1"
  MODEL_NAME="$2"
  CLAUDE_MODEL="${3:-deepseek-chat}"
  
  echo "Agent: ${AGENT_NAME}"
  echo "Model: ${MODEL_NAME}"
  echo "LLM Model: ${CLAUDE_MODEL}"
  
  if run_cr_for_agent_model "${AGENT_NAME}" "${MODEL_NAME}" "${CLAUDE_MODEL}"; then
    echo ""
    echo "========================================="
    echo "✅ Code Review completed for ${AGENT_NAME}/${MODEL_NAME}"
    echo "========================================="
  else
    echo ""
    echo "❌ Code Review failed for ${AGENT_NAME}/${MODEL_NAME}"
    exit 1
  fi
fi
