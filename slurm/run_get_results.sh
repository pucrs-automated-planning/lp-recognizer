#!/usr/bin/env bash
#
# Single Slurm job that runs experiments/get_results.sh end-to-end.
# Equivalent to running it locally with -rerun, but on the cluster.
#
# Usage:
#   sbatch slurm/run_get_results.sh           # full run (all 12 domains)
#   sbatch slurm/run_get_results.sh -fast     # 6-domain subset
#
# Any arguments after the script name are forwarded to get_results.sh.

#SBATCH --job-name=lp-recog-full
#SBATCH --time=48:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=1
#SBATCH --output=slurm/logs/%j.out
#SBATCH --error=slurm/logs/%j.err

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

mkdir -p "$SCRIPT_DIR/logs"

cd "$REPO_DIR/experiments"
bash get_results.sh -rerun "$@"
