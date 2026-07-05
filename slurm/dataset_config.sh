#!/usr/bin/env bash
#
# Shared dataset configuration for the Slurm scripts.
#
# This is the single source of truth for which goal/plan recognition dataset
# the Slurm pipeline runs against. Source it from run_experiment.sh,
# submit_jobs.sh, and collect_results.sh so all three agree on the domain list,
# dataset types, and dataset directory (in particular, submit_jobs.sh's array
# index math relies on using the same DOMAINS order as run_experiment.sh).
#
# Select the dataset with the DATASET environment variable:
#   DATASET=lp      (default) pucrs-automated-planning LP dataset — AAAI/JAIR
#   DATASET=metric  meneguzzi-lab metric goal/plan recognition dataset
#                   (https://github.com/meneguzzi-lab/metric-goal-plan-recognition-dataset)
#
# Datasets are expected to be cloned as siblings of this repository. Override
# the resolved location with the DATASET_DIR environment variable if your
# layout differs (e.g. the alternative goal-plan-recognition-dataset-lp clone).
#
# Exports (as shell variables in the sourcing script):
#   DATASET        normalised dataset name (lp|metric)
#   DOMAINS        array of domain names
#   FAST_DOMAINS   array of domains used by submit_jobs.sh --fast
#   BASE_TYPES     array of non-noisy dataset types
#   NOISY_TYPES    array of noisy dataset types
#   DATASET_DIR    absolute path to the dataset root

# Resolve the parent directory relative to this file so the default dataset
# path works regardless of the caller's working directory.
_DATASET_CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_REPO_DIR="$(dirname "$_DATASET_CONFIG_DIR")"
_PARENT_DIR="$(dirname "$_REPO_DIR")"

DATASET="${DATASET:-lp}"

case "$DATASET" in
    lp)
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
        FAST_DOMAINS=(blocks-world depots driverlog dwr rovers sokoban)
        BASE_TYPES=(optimal suboptimal)
        NOISY_TYPES=(optimal-old-noisy suboptimal-old-noisy)
        DATASET_DIR="${DATASET_DIR:-$_PARENT_DIR/goal-plan-recognition-dataset}"
        ;;
    metric)
        DOMAINS=(
            depots
            driverlog
            logistics
            rovers
            satellite
            sokoban
            zenotravel
        )
        FAST_DOMAINS=(depots driverlog rovers sokoban)
        BASE_TYPES=(optimal suboptimal)
        NOISY_TYPES=(optimal-noisy suboptimal-noisy)
        DATASET_DIR="${DATASET_DIR:-$_PARENT_DIR/metric-goal-plan-recognition-dataset/dataset}"
        ;;
    *)
        echo "ERROR: unknown DATASET '$DATASET' (expected 'lp' or 'metric')" >&2
        return 1 2>/dev/null || exit 1
        ;;
esac
