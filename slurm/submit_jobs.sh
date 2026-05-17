#!/usr/bin/env bash
#
# Submit the lp-recognizer experiment array job.
#
# Usage:
#   ./slurm/submit_jobs.sh              # all 240 tasks (12 domains × 4 types × 5 obs)
#   ./slurm/submit_jobs.sh --fast       # 6 domains only  (120 tasks)
#   ./slurm/submit_jobs.sh --array 0-9  # explicit task range (for testing)
#
# Run from the repository root.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

# Domains used by --fast mode (mirrors get_results.sh -fast)
FAST_DOMAINS=(blocks-world depots driverlog dwr rovers sokoban)
N_TYPES=4
N_OBS=5

ARRAY_SPEC="0-239"   # default: all tasks
EXTRA_SBATCH_ARGS=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --fast)
            # Compute which task indices correspond to the 6 fast domains.
            # The full domain list order must match DOMAINS in run_experiment.sh.
            ALL_DOMAINS=(blocks-world depots driverlog dwr easy-ipc-grid ferry
                         logistics miconic rovers satellite sokoban zeno-travel)
            INDICES=()
            for i in "${!ALL_DOMAINS[@]}"; do
                for fast in "${FAST_DOMAINS[@]}"; do
                    if [[ "${ALL_DOMAINS[$i]}" == "$fast" ]]; then
                        START=$(( i * N_TYPES * N_OBS ))
                        END=$(( START + N_TYPES * N_OBS - 1 ))
                        INDICES+=("$START-$END")
                    fi
                done
            done
            ARRAY_SPEC="$(IFS=,; echo "${INDICES[*]}")"
            shift
            ;;
        --array)
            ARRAY_SPEC="$2"
            shift 2
            ;;
        *)
            # Pass unknown args straight to sbatch (e.g. --partition, --qos)
            EXTRA_SBATCH_ARGS+=("$1")
            shift
            ;;
    esac
done

mkdir -p "$SCRIPT_DIR/logs"

echo "Submitting array: $ARRAY_SPEC"
sbatch --array="$ARRAY_SPEC" "${EXTRA_SBATCH_ARGS[@]}" "$SCRIPT_DIR/run_experiment.sh"
