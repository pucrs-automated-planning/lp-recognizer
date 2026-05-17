#!/usr/bin/env bash
#
# Slurm array job: one task per (domain × dataset-type × observability).
#
# Array layout (240 tasks total):
#   12 domains × 4 dataset types × 5 observability levels
#
# Submit via:
#   sbatch slurm/run_experiment.sh          # all 240 tasks
#   sbatch --array=0-59 slurm/run_experiment.sh   # first 3 dataset types only, etc.
#
# Adjust the #SBATCH directives and the Configuration section below to match
# your cluster before submitting.

#SBATCH --job-name=lp-recog
#SBATCH --array=0-239
#SBATCH --time=08:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1
#SBATCH --output=slurm/logs/%A_%a.out
#SBATCH --error=slurm/logs/%A_%a.err

# ---------------------------------------------------------------------------
# Configuration — mirrors experiments/get_results.sh
# ---------------------------------------------------------------------------
DOMAINS=(
    blocks-world
    depots
    driverlog
    dwr
    easy-ipc-grid
    ferry
    logistics
    miconic
    rovers
    satellite
    sokoban
    zeno-travel
)

TYPES=(optimal suboptimal optimal-old-noisy suboptimal-old-noisy)
OBS=(10 30 50 70 100)

# Methods from get_results.sh (lines 152-158)
METHODS_BASE="delta-cdt delta-o-cdto delta-o-cdtb5 delta-o1-cdtb5"
METHODS_NOISY="delta-cdt-f2 delta-o-cdto-f2 delta-o-cdtb5-f2 delta-o1-cdtb5-f2"

LP_SOLVER="cplex"   # change to "cplex" if a licence is available on the cluster
# LP_SOLVER="soplex"   # change to "cplex" if a licence is available on the cluster

# ---------------------------------------------------------------------------
# Paths — derived from SLURM_SUBMIT_DIR (where sbatch was called from).
# BASH_SOURCE[0] is unusable in a Slurm job — the script is copied to a
# temp path before execution.
# ---------------------------------------------------------------------------
REPO_DIR="$SLURM_SUBMIT_DIR"
SCRIPT_DIR="$REPO_DIR/slurm"
PARENT_DIR="$(dirname "$REPO_DIR")"

DATASET_DIR="$PARENT_DIR/goal-plan-recognition-dataset"
RESULTS_DIR="$REPO_DIR/slurm-results"

# PYTHONPATH lets run_instance.py import the repo's modules without installing.
export PYTHONPATH="$REPO_DIR:${PYTHONPATH:-}"

# ---------------------------------------------------------------------------
# Decode array task index → (domain, type, obs)
#
# Index ordering: domain is the slowest-varying axis, obs the fastest.
#   task = domain_idx * (N_TYPES * N_OBS) + type_idx * N_OBS + obs_idx
# ---------------------------------------------------------------------------
N_OBS=${#OBS[@]}       # 5
N_TYPES=${#TYPES[@]}   # 4

DOMAIN_IDX=$(( SLURM_ARRAY_TASK_ID / (N_TYPES * N_OBS) ))
TYPE_IDX=$(( (SLURM_ARRAY_TASK_ID / N_OBS) % N_TYPES ))
OBS_IDX=$(( SLURM_ARRAY_TASK_ID % N_OBS ))

DOMAIN="${DOMAINS[$DOMAIN_IDX]}"
TYPE="${TYPES[$TYPE_IDX]}"
OBSERVABILITY="${OBS[$OBS_IDX]}"
DOMAIN_TYPE="$DOMAIN-$TYPE"

if [[ "$TYPE" == *noisy* ]]; then
    METHODS="$METHODS_NOISY"
else
    METHODS="$METHODS_BASE"
fi

# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------
EXP_DIR="$DATASET_DIR/$DOMAIN_TYPE/$OBSERVABILITY"
if [[ ! -d "$EXP_DIR" ]]; then
    echo "Dataset directory not found, skipping: $EXP_DIR"
    exit 0
fi

mapfile -t INSTANCES < <(find "$EXP_DIR" -name "*.tar.bz2" | sort)
if [[ ${#INSTANCES[@]} -eq 0 ]]; then
    echo "No .tar.bz2 instances in $EXP_DIR, skipping."
    exit 0
fi

# ---------------------------------------------------------------------------
# Working directory
#
# Each array task gets its own isolated directory to avoid file conflicts.
# ---------------------------------------------------------------------------
WORK_DIR="$PARENT_DIR/tmp/job_${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "$WORK_DIR"
mkdir -p "$SCRIPT_DIR/logs"

trap 'rm -rf "$WORK_DIR"' EXIT

echo "================================================================"
echo "Task $SLURM_ARRAY_TASK_ID: $DOMAIN_TYPE  obs=$OBSERVABILITY%"
echo "Methods:   $METHODS"
echo "Instances: ${#INSTANCES[@]}"
echo "Work dir:  $WORK_DIR"
echo "================================================================"

# ---------------------------------------------------------------------------
# Run each method × instance sequentially within this task
# ---------------------------------------------------------------------------
for METHOD in $METHODS; do
    OUT_BASE="$RESULTS_DIR/$DOMAIN_TYPE/$METHOD/obs$OBSERVABILITY"
    mkdir -p "$OUT_BASE"

    for EXP_FILE in "${INSTANCES[@]}"; do
        INSTANCE_NAME="$(basename "$EXP_FILE" .tar.bz2)"
        OUT_FILE="$OUT_BASE/$INSTANCE_NAME.output"

        if [[ -f "$OUT_FILE" ]]; then
            echo "--- $METHOD | $INSTANCE_NAME  (already done, skipping)"
            continue
        fi

        echo "--- $METHOD | $INSTANCE_NAME"
        cd "$WORK_DIR"
        python3 "$REPO_DIR/slurm/run_instance.py" \
            "$EXP_FILE" \
            "$METHOD" \
            "$OUT_FILE" \
            -S "$LP_SOLVER"

        if [[ $? -ne 0 ]]; then
            echo "WARNING: run_instance.py failed for $METHOD / $INSTANCE_NAME (exit $?)"
        fi
    done
done

echo "Task $SLURM_ARRAY_TASK_ID done."
