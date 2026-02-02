#!/usr/bin/env bash

# ==============================================================================
# Prompt definitions for different evaluation metrics
# ==============================================================================

# Common prompts for Level-1 Deictic tasks (Addition, Removal, Replacement, Translation)
PROMPT_TXT_Deictic_1="Instruction_Adherence=prompt/Instruction_Adherence.txt"
PROMPT_TXT_Deictic_2="Contextual_Preservation=prompt/Contextual_Preservation.txt"
PROMPT_TXT_Deictic_3="Visual_Coherence=prompt/Visual_Coherence.txt"

# Prompts for Light Control task
PROMPT_TXT_Light_Control_1="Light_Direction_Consistency=prompt/Light_Control/Light_Direction_Consistency.txt"
PROMPT_TXT_Light_Control_2="Contextual_Preservation=prompt/Light_Control/Contextual_Preservation.txt"

# Prompts for Flow Simulation task
PROMPT_TXT_Flow_Simulation_1="Wind_Direction_Consistency=prompt/Flow_Simulation/Wind_Direction_Consistency.txt"
PROMPT_TXT_Flow_Simulation_2="Wind_Contextual_Preservation=prompt/Flow_Simulation/Wind_Contextual_Preservation.txt"

# Prompts for Reorientation task
PROMPT_TXT_Reorientation_1="Orientation_Alignment=prompt/Reorientation/Orientation_Alignment.txt"
PROMPT_TXT_Reorientation_2="Reorientation_Contextual_Preservation=prompt/Reorientation/Reorientation_Contextual_Preservation.txt"

# Prompts for Draft Instantiation task
PROMPT_TXT_Draft_Instantiation_1="Instruction_Adherence=prompt/Draft_Instantiation/Instruction_Adherence.txt"
PROMPT_TXT_Draft_Instantiation_2="Contextual_Preservation=prompt/Draft_Instantiation/Contextual_Preservation.txt"
PROMPT_TXT_Draft_Instantiation_3="Visual_Coherence=prompt/Draft_Instantiation/Visual_Coherence.txt"

# Prompts for Billiards task
PROMPT_TXT_Billiards_1="Billiards=prompt/Billiards/Billiards.txt"

# Prompts for Pose Control task
PROMPT_TXT_Pose_Control_1="Pose_Consistency=prompt/Pose_Control/Pose_Consistency.txt"
PROMPT_TXT_Pose_Control_2="BII_CIC_CP=prompt/Pose_Control/BII_CIC_CP.txt"

# ==============================================================================
# Configuration
# ==============================================================================

BASE_RESULTS="/path/to/VIBE-Results"
MODEL="Banana_pro"

echo "🚀 Starting evaluation for all 10 tasks..."
echo ""

# ==============================================================================
# Level-1-Deictic: Task 1 - Addition
# ==============================================================================
echo "=========================================="
echo "📌 Level-1-Deictic: Addition"
echo "=========================================="

DIM="Level-1-Deictic"
TASK_NAME="Addition"
LOG_DIR="./logs/${DIM}/${TASK_NAME}"
mkdir -p "$LOG_DIR"

results_root="${BASE_RESULTS}/${MODEL}/${DIM}/${TASK_NAME}"
result_json="${results_root}/${TASK_NAME}_results.json"
gen_prefix="${results_root}"
log_file="${LOG_DIR}/${MODEL}.log"

if [[ -f "$result_json" ]]; then
  echo "✓ Running evaluation..."
  nohup python -m pipeline.run_eval \
    --prompt "$PROMPT_TXT_Deictic_1" \
    --prompt "$PROMPT_TXT_Deictic_2" \
    --prompt "$PROMPT_TXT_Deictic_3" \
    --result_json "$result_json" \
    --gen_prefix "$gen_prefix" \
    --results_root "$results_root" \
    --task_name "$TASK_NAME" \
    --repeat 3 \
    > "$log_file" 2>&1 &
  echo "  PID=$!, Log: $log_file"
else
  echo "⚠️  Skipped: $result_json not found"
fi
echo ""

# ==============================================================================
# Level-1-Deictic: Task 2 - Removal
# ==============================================================================
echo "=========================================="
echo "📌 Level-1-Deictic: Removal"
echo "=========================================="

TASK_NAME="Removal"
LOG_DIR="./logs/${DIM}/${TASK_NAME}"
mkdir -p "$LOG_DIR"

results_root="${BASE_RESULTS}/${MODEL}/${DIM}/${TASK_NAME}"
result_json="${results_root}/${TASK_NAME}_results.json"
gen_prefix="${results_root}"
log_file="${LOG_DIR}/${MODEL}.log"

if [[ -f "$result_json" ]]; then
  echo "✓ Running evaluation..."
  nohup python -m pipeline.run_eval \
    --prompt "$PROMPT_TXT_Deictic_1" \
    --prompt "$PROMPT_TXT_Deictic_2" \
    --prompt "$PROMPT_TXT_Deictic_3" \
    --result_json "$result_json" \
    --gen_prefix "$gen_prefix" \
    --results_root "$results_root" \
    --task_name "$TASK_NAME" \
    --repeat 3 \
    > "$log_file" 2>&1 &
  echo "  PID=$!, Log: $log_file"
else
  echo "⚠️  Skipped: $result_json not found"
fi
echo ""

# ==============================================================================
# Level-1-Deictic: Task 3 - Replacement
# ==============================================================================
echo "=========================================="
echo "📌 Level-1-Deictic: Replacement"
echo "=========================================="

TASK_NAME="Replacement"
LOG_DIR="./logs/${DIM}/${TASK_NAME}"
mkdir -p "$LOG_DIR"

results_root="${BASE_RESULTS}/${MODEL}/${DIM}/${TASK_NAME}"
result_json="${results_root}/${TASK_NAME}_results.json"
gen_prefix="${results_root}"
log_file="${LOG_DIR}/${MODEL}.log"

if [[ -f "$result_json" ]]; then
  echo "✓ Running evaluation..."
  nohup python -m pipeline.run_eval \
    --prompt "$PROMPT_TXT_Deictic_1" \
    --prompt "$PROMPT_TXT_Deictic_2" \
    --prompt "$PROMPT_TXT_Deictic_3" \
    --result_json "$result_json" \
    --gen_prefix "$gen_prefix" \
    --results_root "$results_root" \
    --task_name "$TASK_NAME" \
    --repeat 3 \
    > "$log_file" 2>&1 &
  echo "  PID=$!, Log: $log_file"
else
  echo "⚠️  Skipped: $result_json not found"
fi
echo ""

# ==============================================================================
# Level-1-Deictic: Task 4 - Translation
# ==============================================================================
echo "=========================================="
echo "📌 Level-1-Deictic: Translation"
echo "=========================================="

TASK_NAME="Translation"
LOG_DIR="./logs/${DIM}/${TASK_NAME}"
mkdir -p "$LOG_DIR"

results_root="${BASE_RESULTS}/${MODEL}/${DIM}/${TASK_NAME}"
result_json="${results_root}/${TASK_NAME}_results.json"
gen_prefix="${results_root}"
log_file="${LOG_DIR}/${MODEL}.log"

if [[ -f "$result_json" ]]; then
  echo "✓ Running evaluation..."
  nohup python -m pipeline.run_eval \
    --prompt "$PROMPT_TXT_Deictic_1" \
    --prompt "$PROMPT_TXT_Deictic_2" \
    --prompt "$PROMPT_TXT_Deictic_3" \
    --result_json "$result_json" \
    --gen_prefix "$gen_prefix" \
    --results_root "$results_root" \
    --task_name "$TASK_NAME" \
    --repeat 3 \
    > "$log_file" 2>&1 &
  echo "  PID=$!, Log: $log_file"
else
  echo "⚠️  Skipped: $result_json not found"
fi
echo ""

# ==============================================================================
# Level-2-Morphological: Task 5 - Reorientation
# ==============================================================================
echo "=========================================="
echo "📌 Level-2-Morphological: Reorientation"
echo "=========================================="

DIM="Level-2-Morphological"
TASK_NAME="Reorientation"
LOG_DIR="./logs/${DIM}/${TASK_NAME}"
mkdir -p "$LOG_DIR"

results_root="${BASE_RESULTS}/${MODEL}/${DIM}/${TASK_NAME}"
result_json="${results_root}/${TASK_NAME}_results.json"
gen_prefix="${results_root}"
log_file="${LOG_DIR}/${MODEL}.log"

if [[ -f "$result_json" ]]; then
  echo "✓ Running evaluation..."
  nohup python -m pipeline.run_eval \
    --prompt "$PROMPT_TXT_Reorientation_1" \
    --prompt "$PROMPT_TXT_Reorientation_2" \
    --result_json "$result_json" \
    --gen_prefix "$gen_prefix" \
    --results_root "$results_root" \
    --task_name "$TASK_NAME" \
    --repeat 3 \
    > "$log_file" 2>&1 &
  echo "  PID=$!, Log: $log_file"
else
  echo "⚠️  Skipped: $result_json not found"
fi
echo ""

# ==============================================================================
# Level-2-Morphological: Task 6 - Draft_Instantiation
# ==============================================================================
echo "=========================================="
echo "📌 Level-2-Morphological: Draft_Instantiation"
echo "=========================================="

TASK_NAME="Draft_Instantiation"
LOG_DIR="./logs/${DIM}/${TASK_NAME}"
mkdir -p "$LOG_DIR"

results_root="${BASE_RESULTS}/${MODEL}/${DIM}/${TASK_NAME}"
result_json="${results_root}/${TASK_NAME}_results.json"
gen_prefix="${results_root}"
log_file="${LOG_DIR}/${MODEL}.log"

if [[ -f "$result_json" ]]; then
  echo "✓ Running evaluation..."
  nohup python -m pipeline.run_eval \
    --prompt "$PROMPT_TXT_Draft_Instantiation_1" \
    --prompt "$PROMPT_TXT_Draft_Instantiation_2" \
    --prompt "$PROMPT_TXT_Draft_Instantiation_3" \
    --result_json "$result_json" \
    --gen_prefix "$gen_prefix" \
    --results_root "$results_root" \
    --task_name "$TASK_NAME" \
    --repeat 3 \
    > "$log_file" 2>&1 &
  echo "  PID=$!, Log: $log_file"
else
  echo "⚠️  Skipped: $result_json not found"
fi
echo ""

# ==============================================================================
# Level-2-Morphological: Task 7 - Pose_Control
# ==============================================================================
echo "=========================================="
echo "📌 Level-2-Morphological: Pose_Control"
echo "=========================================="

TASK_NAME="Pose_Control"
LOG_DIR="./logs/${DIM}/${TASK_NAME}"
mkdir -p "$LOG_DIR"

results_root="${BASE_RESULTS}/${MODEL}/${DIM}/${TASK_NAME}"
result_json="${results_root}/${TASK_NAME}_results.json"
gen_prefix="${results_root}"
log_file="${LOG_DIR}/${MODEL}.log"

if [[ -f "$result_json" ]]; then
  echo "✓ Running evaluation..."
  nohup python -m pipeline.run_eval \
    --prompt "$PROMPT_TXT_Pose_Control_1" \
    --prompt "$PROMPT_TXT_Pose_Control_2" \
    --result_json "$result_json" \
    --gen_prefix "$gen_prefix" \
    --results_root "$results_root" \
    --task_name "$TASK_NAME" \
    --repeat 3 \
    > "$log_file" 2>&1 &
  echo "  PID=$!, Log: $log_file"
else
  echo "⚠️  Skipped: $result_json not found"
fi
echo ""

# ==============================================================================
# Level-3-Causal: Task 8 - Light_Control
# ==============================================================================
echo "=========================================="
echo "📌 Level-3-Causal: Light_Control"
echo "=========================================="

DIM="Level-3-Causal"
TASK_NAME="Light_Control"
LOG_DIR="./logs/${DIM}/${TASK_NAME}"
mkdir -p "$LOG_DIR"

results_root="${BASE_RESULTS}/${MODEL}/${DIM}/${TASK_NAME}"
result_json="${results_root}/${TASK_NAME}_results.json"
gen_prefix="${results_root}"
log_file="${LOG_DIR}/${MODEL}.log"

if [[ -f "$result_json" ]]; then
  echo "✓ Running evaluation..."
  nohup python -m pipeline.run_eval \
    --prompt "$PROMPT_TXT_Light_Control_1" \
    --prompt "$PROMPT_TXT_Light_Control_2" \
    --result_json "$result_json" \
    --gen_prefix "$gen_prefix" \
    --results_root "$results_root" \
    --task_name "$TASK_NAME" \
    --repeat 3 \
    > "$log_file" 2>&1 &
  echo "  PID=$!, Log: $log_file"
else
  echo "⚠️  Skipped: $result_json not found"
fi
echo ""

# ==============================================================================
# Level-3-Causal: Task 9 - Flow_Simulation
# ==============================================================================
echo "=========================================="
echo "📌 Level-3-Causal: Flow_Simulation"
echo "=========================================="

TASK_NAME="Flow_Simulation"
LOG_DIR="./logs/${DIM}/${TASK_NAME}"
mkdir -p "$LOG_DIR"

results_root="${BASE_RESULTS}/${MODEL}/${DIM}/${TASK_NAME}"
result_json="${results_root}/${TASK_NAME}_results.json"
gen_prefix="${results_root}"
log_file="${LOG_DIR}/${MODEL}.log"

if [[ -f "$result_json" ]]; then
  echo "✓ Running evaluation..."
  nohup python -m pipeline.run_eval \
    --prompt "$PROMPT_TXT_Flow_Simulation_1" \
    --prompt "$PROMPT_TXT_Flow_Simulation_2" \
    --result_json "$result_json" \
    --gen_prefix "$gen_prefix" \
    --results_root "$results_root" \
    --task_name "$TASK_NAME" \
    --repeat 3 \
    > "$log_file" 2>&1 &
  echo "  PID=$!, Log: $log_file"
else
  echo "⚠️  Skipped: $result_json not found"
fi
echo ""

# ==============================================================================
# Level-3-Causal: Task 10 - Billiards
# ==============================================================================
echo "=========================================="
echo "📌 Level-3-Causal: Billiards"
echo "=========================================="

TASK_NAME="Billiards"
LOG_DIR="./logs/${DIM}/${TASK_NAME}"
mkdir -p "$LOG_DIR"

results_root="${BASE_RESULTS}/${MODEL}/${DIM}/${TASK_NAME}"
result_json="${results_root}/${TASK_NAME}_results.json"
gen_prefix="${results_root}"
log_file="${LOG_DIR}/${MODEL}.log"

if [[ -f "$result_json" ]]; then
  echo "✓ Running evaluation..."
  nohup python -m pipeline.run_eval \
    --prompt "$PROMPT_TXT_Billiards_1" \
    --result_json "$result_json" \
    --gen_prefix "$gen_prefix" \
    --results_root "$results_root" \
    --task_name "$TASK_NAME" \
    --repeat 3 \
    > "$log_file" 2>&1 &
  echo "  PID=$!, Log: $log_file"
else
  echo "⚠️  Skipped: $result_json not found"
fi
echo ""

# ==============================================================================
# Summary
# ==============================================================================
echo "=========================================="
echo "✅ All evaluation jobs launched!"
echo "=========================================="
echo "📁 Results: ${BASE_RESULTS}/${MODEL}/"
echo "📄 Logs: ./logs/"
echo "=========================================="
