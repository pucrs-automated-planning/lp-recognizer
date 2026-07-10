#!/usr/bin/env bash
#
# Submit one Slurm array job per recognizer method.
#
# Each method gets its own array (N_domains × 2 types × 5 obs) and a job name
# tagged with the dataset and method (e.g. lp-delta-cdt, metric-delta-cdt).
# Base methods  run on: optimal, suboptimal
# Noisy methods run on the selected dataset's noisy types (see dataset_config.sh).
#
# Usage (from repository root):
#   bash slurm/submit_jobs.sh                      # all 8 methods, lp dataset
#   bash slurm/submit_jobs.sh --dataset metric     # all 8 methods, metric dataset
#   bash slurm/submit_jobs.sh --fast               # fast-domain subset only
#   bash slurm/submit_jobs.sh --method delta-cdt   # single method
#   bash slurm/submit_jobs.sh --array 0-9          # explicit task range (for testing)
#   bash slurm/submit_jobs.sh --force              # rerun even if output files exist

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# AAAI 2021 paper — LMC methods + JAIR paper — DELR methods
BASE_METHODS=(delta-cl delta-o-cl delta-o-cl3 delta-o-cl1
              delta-cdt delta-o-cdto delta-o-cdtb5 delta-o1-cdtb5)
NOISY_METHODS=(delta-cl-f2 delta-o-cl-f2 delta-o-cl3-f2 delta-o-cl1-f2
               delta-cdt-f2 delta-o-cdto-f2 delta-o-cdtb5-f2 delta-o1-cdtb5-f2)

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
SELECTED_METHODS=()
USE_FAST=false
ARRAY_OVERRIDE=""
FORCE=""
EXTRA_SBATCH_ARGS=()
DATASET="${DATASET:-lp}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --fast)
            USE_FAST=true
            shift
            ;;
        --dataset)
            DATASET="$2"
            shift 2
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

# Dataset selection (DOMAINS + FAST_DOMAINS) comes from dataset_config.sh, the
# same source run_experiment.sh uses — so the array index math below stays in
# sync with the domain order the job decodes. Sourced after arg parsing so
# --dataset takes effect.
source "$SCRIPT_DIR/dataset_config.sh" || exit 1

# All domains — order must match DOMAINS in run_experiment.sh (same source).
ALL_DOMAINS=("${DOMAINS[@]}")

# Resolve the domain subset now that the dataset (and its FAST_DOMAINS) is known.
if $USE_FAST; then
    SELECTED_DOMAINS=("${FAST_DOMAINS[@]}")
else
    SELECTED_DOMAINS=("${ALL_DOMAINS[@]}")
fi

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
    echo "Submitting ${DATASET}-${METHOD}  array=${SPEC}"
    sbatch \
        --job-name="${DATASET}-${METHOD}" \
        --array="$SPEC" \
        "${EXTRA_SBATCH_ARGS[@]}" \
        "$SCRIPT_DIR/run_experiment.sh" \
        "$METHOD" $FORCE --dataset "$DATASET"
done
