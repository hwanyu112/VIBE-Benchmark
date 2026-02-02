# !/usr/bin/env bash

PROMPT_TXT1="Instruction_Adherence=./prompt/Instruction_Adherence.txt"
PROMPT_TXT2="Contextual_Preservation=./prompt/Contextual_Preservation.txt"
PROMPT_TXT3="Visual_Coherence=./prompt/Visual_Coherence.txt"


BASE_RESULTS="/path/to/VIBE-Results"
DIM="Level-1-Deictic"
TASK_NAME="3-Tasks"
LOG_DIR="./logs/${DIM}/Multi-Tasks"
mkdir -p "$LOG_DIR"


MODELS=(
  "Banana_pro"
)

echo "Launching ${#MODELS[@]} eval jobs with nohup ..."

for model in "${MODELS[@]}"; do
  results_root="${BASE_RESULTS}/${model}/${DIM}/Multi-Tasks"
  result_json="${results_root}/${TASK_NAME}_results.json"
  gen_prefix="${results_root}"
  log_file="${LOG_DIR}/${model}_${TASK_NAME}.log"

  if [[ ! -f "$result_json" ]]; then
    echo "⚠️ Skip ${model}: ${result_json} not found"
    continue
  fi

  echo "🚀 Start ${model}, log -> ${log_file}"

  nohup python -m pipeline.run_eval \
    --prompt "$PROMPT_TXT1" \
    --prompt "$PROMPT_TXT2" \
    --prompt "$PROMPT_TXT3" \
    --result_json "$result_json" \
    --gen_prefix "$gen_prefix" \
    --results_root "$results_root" \
    --task_name "$TASK_NAME" \
    --repeat 3 \
    --repeat_resume \
    > "$log_file" 2>&1 &
  pid=$!
  echo "    PID=${pid}, log=${log_file}"

done

echo "✅ All jobs launched with nohup."
echo "📄 Logs directory: $LOG_DIR"
