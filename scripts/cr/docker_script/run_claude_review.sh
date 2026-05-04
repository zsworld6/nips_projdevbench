#!/usr/bin/env bash
set -euo pipefail

show_usage() {
  cat <<'EOF'
Usage: run_claude_review.sh <agent_name> <model_name> <claude_model>

This script iterates over repositories under logs/<agent_name>/<model_name>/,
and for each problem repository invokes the Claude CLI to generate an
evaluation summary. Results are stored in cr_result/<agent>/<model>/.

The script expects the Claude credentials / configuration in
config/evaluate.env (sourced automatically).

Note: The <claude_model> parameter specifies which model to use for review.
      Typically "deepseek-chat" is used when using DeepSeek API via ANTHROPIC_BASE_URL.

Example:
  ./run_claude_review.sh augment GPT-5 deepseek-chat
EOF
  exit 1
}

if [[ $# -ne 3 ]]; then
  show_usage
fi

AGENT_NAME=$1
MODEL_NAME=$2
CLAUDE_MODEL=$3

# Optional: ONLY_PROBLEMS (space- or comma-separated) to restrict evaluation
# Example: ONLY_PROBLEMS="003 020" or ONLY_PROBLEMS="003,020"
ALLOWED_PROBLEMS=()
if [[ -n "${ONLY_PROBLEMS:-}" ]]; then
  # replace commas with spaces, split into array
  read -r -a ALLOWED_PROBLEMS <<<"$(echo "${ONLY_PROBLEMS}" | tr ',' ' ')"
fi

is_problem_allowed() {
  local pid="$1"
  if [[ ${#ALLOWED_PROBLEMS[@]} -eq 0 ]]; then
    return 0
  fi
  for p in "${ALLOWED_PROBLEMS[@]}"; do
    if [[ "$p" == "$pid" ]]; then
      return 0
    fi
  done
  return 1
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

CONFIG_FILE="${PROJECT_ROOT}/config/evaluate.env"
if [[ ! -f "${CONFIG_FILE}" ]]; then
  echo "❌ Config file not found: ${CONFIG_FILE}" >&2
  exit 1
fi

# Load Claude credentials (ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL, etc.)
set -a
# shellcheck disable=SC1090
source "${CONFIG_FILE}"
set +a

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "❌ ANTHROPIC_API_KEY is not set (check ${CONFIG_FILE})" >&2
  exit 1
fi

# Export as ANTHROPIC_AUTH_TOKEN for Claude CLI compatibility
export ANTHROPIC_AUTH_TOKEN="${ANTHROPIC_API_KEY}"

EVAL_ROOT="${PROJECT_ROOT}/logs/${AGENT_NAME}/${MODEL_NAME}"
if [[ ! -d "${EVAL_ROOT}" ]]; then
  echo "❌ Evaluation root not found: ${EVAL_ROOT}" >&2
  exit 1
fi

OUTPUT_ROOT="${PROJECT_ROOT}/cr_result/${AGENT_NAME}/${MODEL_NAME}"
mkdir -p "${OUTPUT_ROOT}"

overall_count=0
processed=0

for problem_dir in "${EVAL_ROOT}"/*/; do
  [[ -d "${problem_dir}" ]] || continue
  problem_id="$(basename "${problem_dir}")"
  if ! is_problem_allowed "${problem_id}"; then
    echo "⚠️  Skip problem ${problem_id} (not in ONLY_PROBLEMS)"
    continue
  fi
  repo_path=""
  # find first directory that looks like oj-eval-*
  while IFS= read -r -d '' candidate; do
    repo_path="${candidate}"
    break
  done < <(find "${problem_dir}" -maxdepth 1 -type d -name "oj-eval-*" -print0)

  overall_count=$((overall_count + 1))

  if [[ -z "${repo_path}" ]]; then
    echo "⚠️  Problem ${problem_id}: repository directory not found, skipping."
    continue
  fi

  if [[ ! -d "${repo_path}" ]]; then
    echo "⚠️  Problem ${problem_id}: ${repo_path} is not a directory, skipping."
    continue
  fi

  processed=$((processed + 1))
  echo "========================================="
  echo "📦 Evaluating problem ${problem_id}"
  echo "Repository: ${repo_path}"

  output_dir="${OUTPUT_ROOT}/${problem_id}"
  mkdir -p "${output_dir}"
  result_file="${output_dir}/result.json"

  problem_path="${PROJECT_ROOT}/problem/${problem_id}"
  problem_readme="${problem_path}/README.md"
  cr_list_path="${PROJECT_ROOT}/scripts/cr/${problem_id}/cr_list.json"

  # Build evaluation criteria as JSON from llm_as_a_judge entries
  criteria_json=""
  if [[ -f "${cr_list_path}" ]]; then
    criteria_json=$(python3 - <<PY
import json, sys, pathlib
path = pathlib.Path(${cr_list_path@Q})
try:
    data = json.loads(path.read_text(encoding="utf-8"))
    criteria = []
    for item in data:
        if isinstance(item, dict) and item.get("script") == "llm_as_a_judge":
            name = item.get("name", "").strip()
            desc = item.get("description", "").strip()
            if name or desc:
                criteria.append({
                    "name": name,
                    "description": desc
                })
    if criteria:
        print(json.dumps(criteria, ensure_ascii=False, indent=2))
    else:
        print("[]")
except Exception as exc:
    print("[]", file=sys.stderr)
    sys.exit(1)
PY
)
  fi

  if [[ -z "${criteria_json}" ]] || [[ "${criteria_json}" == "[]" ]]; then
    criteria_json='[{"name": "Review overall solution quality, correctness, and repository hygiene.", "description": "Review overall solution quality, correctness, and repository hygiene."}]'
  fi

  PROMPT_CONTENT_REVIEW=$(cat <<EOT
You are acting as a senior reviewer for the OJBench benchmark.
Analyse the provided repository and return only a single JSON object with evaluation scores.

Project context:
- Problem ID: ${problem_id}
- Problem directory: ${problem_path}
- Problem statement (if available): ${problem_readme}
- Solution repository: ${repo_path}

Evaluation criteria (as JSON array):
${criteria_json}

You must evaluate EXACTLY the criteria listed in the JSON array above. Each criterion in the array must have a corresponding entry in your response.

Respond with a JSON object using this exact schema:
{
  "criteria_scores": [
    {
      "name": "Name of the evaluation criterion (must match exactly one from the criteria array above)",
      "result": 0,  // integer from 0 to 10 inclusive representing the score for this criterion
      "explanation": "Brief justification for the score grounded in this specific criterion."
    }
    // Include EXACTLY one object for each criterion in the criteria array above
  ]
}

IMPORTANT:
- The number of objects in criteria_scores MUST equal the number of criteria in the input JSON array
- Each "name" field must match exactly one criterion name from the input array
- Do NOT split a single criterion into multiple entries
- Do NOT combine multiple criteria into a single entry

Ensure the response is valid JSON, without additional commentary or formatting.

You have full filesystem access. After producing the JSON, also create (or overwrite) the file at this exact path with the same JSON content:
${result_file}
EOT
)

  pushd "${repo_path}" >/dev/null

  echo "📝 Running Claude review (output -> ${result_file})"
  ANTHROPIC_MODEL="${CLAUDE_MODEL}" \
  ANTHROPIC_SMALL_FAST_MODEL="${CLAUDE_MODEL}" \
  ANTHROPIC_DEFAULT_HAIKU_MODEL="${CLAUDE_MODEL}" \
  ANTHROPIC_DEFAULT_SONNET_MODEL="${CLAUDE_MODEL}" \
  ANTHROPIC_DEFAULT_OPUS_MODEL="${CLAUDE_MODEL}" \
  claude -p "${PROMPT_CONTENT_REVIEW}" \
         --model "${CLAUDE_MODEL}" \
         --output-format text \
         --dangerously-skip-permissions \
         --verbose | tee "${output_dir}/result_stdout.log"

  if [[ ! -f "${result_file}" ]]; then
    echo "⚠️  Claude did not create ${result_file}. Please inspect ${output_dir}/result_stdout.log for details." >&2
  fi

  popd >/dev/null
done

echo "========================================="
echo "✅ Claude review completed."
echo "Processed repositories: ${processed}/${overall_count}"
echo "Results stored under: ${OUTPUT_ROOT}"

