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
# Slurm directives — must appear before any executable code so that sbatch
# reads them.  Bash ignores lines beginning with # so they are harmless when
# the script is run directly.
# ---------------------------------------------------------------------------
#SBATCH --job-name=lp-recog-full
#SBATCH --time=24:00:00
#SBATCH --mem=24G
#SBATCH --cpus-per-task=1
#SBATCH --output=slurm/logs/%j.out
#SBATCH --error=slurm/logs/%j.err

# ---------------------------------------------------------------------------
# Self-submit block: only runs when called directly, not inside a Slurm job.
# Detects the partition via sinfo, then re-submits this script via sbatch.
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
# Job body
# ---------------------------------------------------------------------------
# SLURM_SUBMIT_DIR is set by Slurm to wherever sbatch was invoked from.
# BASH_SOURCE[0] is unusable here — Slurm copies the script to a temp path.
REPO_DIR="$SLURM_SUBMIT_DIR"

cd "$REPO_DIR/experiments"
srun bash get_results.sh -rerun "$@"
wait
