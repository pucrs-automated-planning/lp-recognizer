#!/usr/bin/env bash
#
# Remove results from slurm-results/ so jobs will rerun them.
#
# Usage (from repository root):
#   bash slurm/clean_results.sh --partial            # empty/truncated .output files only
#   bash slurm/clean_results.sh --method delta-cdt   # all results for one method
#   bash slurm/clean_results.sh --domain blocks-world-optimal  # all results for one domain-type
#   bash slurm/clean_results.sh --all                # everything under slurm-results/
#
# --partial and --method/--domain can be combined, e.g.:
#   bash slurm/clean_results.sh --partial --method delta-cdt

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$(dirname "$SCRIPT_DIR")/slurm-results"

if [[ ! -d "$RESULTS_DIR" ]]; then
    echo "Nothing to clean: $RESULTS_DIR does not exist."
    exit 0
fi

MODE_PARTIAL=false
MODE_ALL=false
FILTER_METHOD=""
FILTER_DOMAIN=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --partial) MODE_PARTIAL=true; shift ;;
        --all)     MODE_ALL=true;     shift ;;
        --method)  FILTER_METHOD="$2"; shift 2 ;;
        --domain)  FILTER_DOMAIN="$2"; shift 2 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

if ! $MODE_PARTIAL && ! $MODE_ALL && [[ -z "$FILTER_METHOD" && -z "$FILTER_DOMAIN" ]]; then
    echo "Specify at least one of: --partial, --all, --method <name>, --domain <name>" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# --all: wipe everything
# ---------------------------------------------------------------------------
if $MODE_ALL; then
    echo "Removing all results under $RESULTS_DIR ..."
    rm -rf "$RESULTS_DIR"
    echo "Done."
    exit 0
fi

# ---------------------------------------------------------------------------
# --method / --domain: remove the matching subtree
# ---------------------------------------------------------------------------
if [[ -n "$FILTER_METHOD" ]]; then
    COUNT=0
    while IFS= read -r -d '' dir; do
        echo "Removing $dir"
        rm -rf "$dir"
        (( COUNT++ )) || true
    done < <(find "$RESULTS_DIR" -type d -name "$FILTER_METHOD" -print0)
    echo "Removed $COUNT method directories."
fi

if [[ -n "$FILTER_DOMAIN" ]]; then
    TARGET="$RESULTS_DIR/$FILTER_DOMAIN"
    if [[ -d "$TARGET" ]]; then
        echo "Removing $TARGET"
        rm -rf "$TARGET"
        echo "Done."
    else
        echo "Not found: $TARGET"
    fi
fi

# ---------------------------------------------------------------------------
# --partial: remove .output files that are empty or contain no result lines
# A valid .output file has at least one line starting with "> " (a hypothesis
# result). A file with only the header line or no content was written by a
# job that was killed before any hypothesis was evaluated.
# ---------------------------------------------------------------------------
if $MODE_PARTIAL; then
    REMOVED=0
    SEARCH_ROOT="${RESULTS_DIR}"

    while IFS= read -r -d '' f; do
        # Empty file
        if [[ ! -s "$f" ]]; then
            echo "Empty:    $f"
            rm "$f"
            (( REMOVED++ )) || true
            continue
        fi
        # File exists but has no hypothesis result lines
        if ! grep -q "^> " "$f"; then
            echo "Truncated: $f"
            rm "$f"
            (( REMOVED++ )) || true
        fi
    done < <(find "$SEARCH_ROOT" -name "*.output" -print0)

    echo "Removed $REMOVED partial .output files."
fi
