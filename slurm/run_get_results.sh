#!/usr/bin/env bash
#
# Single Slurm job that runs experiments/get_results.sh end-to-end.
# Equivalent to running it locally with -rerun, but on the cluster.
#
# Usage (run directly — not via sbatch):
#   bash slurm/run_get_results.sh
#   bash slurm/run_get_results.sh -fast
#   bash slurm/run_get_results.sh --partition <name>   # override auto-detect
#
# The partition is detected automatically from sinfo (default partition first,
# falling back to the first available).  Any other flags are forwarded to
# get_results.sh.

# ---------------------------------------------------------------------------
# Self-submit block: only runs when called directly, not inside a Slurm job.
# ---------------------------------------------------------------------------
if [[ -z "${SLURM_JOB_ID:-}" ]]; then
    PARTITION=""
    PASSTHROUGH=()
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --partition|-p) PARTITION="$2"; shift 2 ;;
            *) PASSTHROUGH+=("$1"); shift ;;
        esac
    done

    if [[ -z "$PARTITION" ]]; then
        # Prefer the default partition (marked with * in sinfo output).
        PARTITION=$(sinfo -h -o "%P" | grep '\*' | head -1 | tr -d '*')
        # Fall back to the first listed partition if none is marked default.
        if [[ -z "$PARTITION" ]]; then
            PARTITION=$(sinfo -h -o "%P" | head -1 | tr -d '*')
        fi
        if [[ -z "$PARTITION" ]]; then
            echo "ERROR: could not detect a partition from sinfo." >&2
            exit 1
        fi
        echo "Using partition: $PARTITION"
    fi

    mkdir -p "$(dirname "${BASH_SOURCE[0]}")/logs"
    exec sbatch --partition="$PARTITION" "${BASH_SOURCE[0]}" "${PASSTHROUGH[@]}"
fi

# ---------------------------------------------------------------------------
# Slurm directives — read by sbatch when this script is submitted above.
# ---------------------------------------------------------------------------
#SBATCH --job-name=lp-recog-full
#SBATCH --time=48:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=1
#SBATCH --output=slurm/logs/%j.out
#SBATCH --error=slurm/logs/%j.err

# ---------------------------------------------------------------------------
# Job body
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$REPO_DIR/experiments"
bash get_results.sh -rerun "$@"
