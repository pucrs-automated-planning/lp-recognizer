#!/usr/bin/env bash
#
# Slurm array job: one task per (domain × dataset-type × observability) for
# a single recognizer method.
#
# Array layout (120 tasks per method):
#   12 domains × 2 dataset types × 5 observability levels
#   Base methods  run on: optimal, suboptimal
#   Noisy methods run on: optimal-old-noisy, suboptimal-old-noisy
#
# Submit via submit_jobs.sh (preferred) or directly:
#   sbatch --array=0-119 slurm/run_experiment.sh delta-cdt
#
# Adjust the #SBATCH directives and the Configuration section below to match
# your cluster before submitting.

#SBATCH --job-name=lp-recog
#SBATCH --array=0-119
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

BASE_TYPES=(optimal suboptimal)
NOISY_TYPES=(optimal-old-noisy suboptimal-old-noisy)
OBS=(10 30 50 70 100)

LP_SOLVER="cplex"

# ---------------------------------------------------------------------------
# Method — passed as positional arg by submit_jobs.sh.
# ---------------------------------------------------------------------------
METHOD="${1:-}"
if [[ -z "$METHOD" ]]; then
    echo "ERROR: no method specified. Pass method name as first argument." >&2
    exit 1
fi

if [[ "$METHOD" == *-f2 ]]; then
    TYPES=("${NOISY_TYPES[@]}")
else
    TYPES=("${BASE_TYPES[@]}")
fi

# ---------------------------------------------------------------------------
# Paths — derived from SLURM_SUBMIT_DIR (where sbatch was called from).
# ---------------------------------------------------------------------------
REPO_DIR="$SLURM_SUBMIT_DIR"
SCRIPT_DIR="$REPO_DIR/slurm"
PARENT_DIR="$(dirname "$REPO_DIR")"

DATASET_DIR="$PARENT_DIR/goal-plan-recognition-dataset"
RESULTS_DIR="$REPO_DIR/slurm-results"

export PYTHONPATH="$REPO_DIR:${PYTHONPATH:-}"

# ---------------------------------------------------------------------------
# Decode array task index → (domain, type, obs)
#
#   task = domain_idx * (N_TYPES * N_OBS) + type_idx * N_OBS + obs_idx
# ---------------------------------------------------------------------------
N_TYPES=${#TYPES[@]}   # 2
N_OBS=${#OBS[@]}       # 5

DOMAIN_IDX=$(( SLURM_ARRAY_TASK_ID / (N_TYPES * N_OBS) ))
TYPE_IDX=$(( (SLURM_ARRAY_TASK_ID / N_OBS) % N_TYPES ))
OBS_IDX=$(( SLURM_ARRAY_TASK_ID % N_OBS ))

DOMAIN="${DOMAINS[$DOMAIN_IDX]}"
TYPE="${TYPES[$TYPE_IDX]}"
OBSERVABILITY="${OBS[$OBS_IDX]}"
DOMAIN_TYPE="$DOMAIN-$TYPE"

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
# Working directory — isolated per task to avoid file conflicts.
# ---------------------------------------------------------------------------
WORK_DIR="$PARENT_DIR/tmp/job_${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
mkdir -p "$WORK_DIR"
mkdir -p "$SCRIPT_DIR/logs"

trap 'rm -rf "$WORK_DIR"' EXIT

echo "================================================================"
echo "Task $SLURM_ARRAY_TASK_ID: $DOMAIN_TYPE  obs=$OBSERVABILITY%  method=$METHOD"
echo "Instances: ${#INSTANCES[@]}"
echo "Work dir:  $WORK_DIR"
echo "================================================================"

# ---------------------------------------------------------------------------
# Run each instance for this method
# ---------------------------------------------------------------------------
OUT_BASE="$RESULTS_DIR/$DOMAIN_TYPE/$METHOD/obs$OBSERVABILITY"
mkdir -p "$OUT_BASE"

for EXP_FILE in "${INSTANCES[@]}"; do
    INSTANCE_NAME="$(basename "$EXP_FILE" .tar.bz2)"
    OUT_FILE="$OUT_BASE/$INSTANCE_NAME.output"

    if [[ -f "$OUT_FILE" ]]; then
        echo "--- $INSTANCE_NAME  (already done, skipping)"
        continue
    fi

    echo "--- $INSTANCE_NAME"
    cd "$WORK_DIR"
    python3 "$REPO_DIR/slurm/run_instance.py" \
        "$EXP_FILE" \
        "$METHOD" \
        "$OUT_FILE" \
        -S "$LP_SOLVER"

    if [[ $? -ne 0 ]]; then
        echo "WARNING: run_instance.py failed for $INSTANCE_NAME (exit $?)"
    fi
done

echo "Task $SLURM_ARRAY_TASK_ID done."
