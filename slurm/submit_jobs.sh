#!/usr/bin/env bash
#
# Submit one Slurm array job per recognizer method.
#
# Each method gets its own 120-task array (12 domains × 2 types × 5 obs)
# and a meaningful job name (e.g. lp-delta-cdt).
# Base methods  run on: optimal, suboptimal
# Noisy methods run on: optimal-old-noisy, suboptimal-old-noisy
#
# Usage (from repository root):
#   bash slurm/submit_jobs.sh                      # all 8 methods
#   bash slurm/submit_jobs.sh --fast               # 6 domains only  (120 tasks)
#   bash slurm/submit_jobs.sh --method delta-cdt   # single method
#   bash slurm/submit_jobs.sh --array 0-9          # explicit task range (for testing)
#   bash slurm/submit_jobs.sh --force              # rerun even if output files exist

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Domains used by --fast mode (mirrors get_results.sh -fast)
FAST_DOMAINS=(blocks-world depots driverlog dwr rovers sokoban)

# All domains — order must match DOMAINS in run_experiment.sh.
ALL_DOMAINS=(blocks-world depots driverlog dwr easy-ipc-grid ferry
             logistics miconic rovers satellite sokoban zeno-travel)

BASE_METHODS=(delta-cdt delta-o-cdto delta-o-cdtb5 delta-o1-cdtb5)
NOISY_METHODS=(delta-cdt-f2 delta-o-cdto-f2 delta-o-cdtb5-f2 delta-o1-cdtb5-f2)

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
SELECTED_METHODS=()
SELECTED_DOMAINS=("${ALL_DOMAINS[@]}")
ARRAY_OVERRIDE=""
FORCE=""
EXTRA_SBATCH_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --fast)
            # Compute which task indices correspond to the 6 fast domains.
            # The full domain list order must match DOMAINS in run_experiment.sh.
            SELECTED_DOMAINS=("${FAST_DOMAINS[@]}")
            shift
            ;;
        --method)
            SELECTED_METHODS=("$2")
            shift 2
            ;;
        --array)
            ARRAY_OVERRIDE="$2"
            shift 2
            ;;
        --force)
            FORCE="--force"
            shift
            ;;
        *)
            # Pass unknown args straight to sbatch (e.g. --partition, --qos)
            EXTRA_SBATCH_ARGS+=("$1")
            shift
            ;;
    esac
done

# Default to all methods if --method was not given
if [[ ${#SELECTED_METHODS[@]} -eq 0 ]]; then
    SELECTED_METHODS=("${BASE_METHODS[@]}" "${NOISY_METHODS[@]}")
fi

# ---------------------------------------------------------------------------
# Compute the array spec for the selected domains.
#
# Task index formula (must match run_experiment.sh):
#   task = domain_idx * (N_TYPES * N_OBS) + type_idx * N_OBS + obs_idx
# With N_TYPES=2 and N_OBS=5 per method array:
#   domain_idx 0 → tasks 0–9, domain_idx 1 → tasks 10–19, etc.
# ---------------------------------------------------------------------------
N_TYPE_OBS=10   # 2 types × 5 obs levels per domain

compute_array_spec() {
    local -a domain_list=("$@")
    local parts=()
    for domain in "${domain_list[@]}"; do
        for i in "${!ALL_DOMAINS[@]}"; do
            if [[ "${ALL_DOMAINS[$i]}" == "$domain" ]]; then
                local start=$(( i * N_TYPE_OBS ))
                local end=$(( start + N_TYPE_OBS - 1 ))
                parts+=("${start}-${end}")
                break
            fi
        done
    done
    local IFS=','
    echo "${parts[*]}"
}

ARRAY_SPEC="$(compute_array_spec "${SELECTED_DOMAINS[@]}")"

# ---------------------------------------------------------------------------
# Submit one array job per method
# ---------------------------------------------------------------------------
mkdir -p "$SCRIPT_DIR/logs"

for METHOD in "${SELECTED_METHODS[@]}"; do
    SPEC="${ARRAY_OVERRIDE:-$ARRAY_SPEC}"
    echo "Submitting lp-${METHOD}  array=${SPEC}"
    sbatch \
        --job-name="lp-${METHOD}" \
        --array="$SPEC" \
        "${EXTRA_SBATCH_ARGS[@]}" \
        "$SCRIPT_DIR/run_experiment.sh" \
        "$METHOD" $FORCE
done
