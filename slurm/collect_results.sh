#!/usr/bin/env bash
#
# Collect results produced by the Slurm array job into the format expected
# by get_results.sh / data_output.py.
#
# What this does:
#   1. Merges per-instance .output files (in observability order) into the
#      per-(domain-type, method) .output files that data_output.py reads.
#   2. Calls data_output.py to regenerate the LaTeX .txt tables, equivalent
#      to running:  cd experiments && ./get_results.sh -txt
#
# Usage (from repository root):
#   bash slurm/collect_results.sh
#   bash slurm/collect_results.sh --check   # report missing output files only

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

RESULTS_DIR="$REPO_DIR/slurm-results"
OUTPUTS_DIR="$REPO_DIR/outputs"

OBS=(10 30 50 70 100)

# Methods — mirrors get_results.sh
# DELR methods (second paper)
#METHODS_BASE="delta-cdt delta-o-cdto delta-o-cdtb5 delta-o1-cdtb5"
#METHODS_NOISY="delta-cdt-f2 delta-o-cdto-f2 delta-o-cdtb5-f2 delta-o1-cdtb5-f2"

# LMC methods (JAIR 2021 paper)
METHODS_BASE="delta-cl delta-o-cl delta-o-cl3 delta-o-cl1"
METHODS_NOISY="delta-cl-f2 delta-o-cl-f2 delta-o-cl3-f2 delta-o-cl1-f2"

# Original Domains
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
## Metric domains
# DOMAINS=(
#     depots
#     driverlog
#     logistics
#     rovers
#     satellite
#     sokoban
#     zenotravel
# )

# Use the types below for the LP dataset
TYPES=(optimal suboptimal optimal-old-noisy suboptimal-old-noisy)
# Use the types below for the metric experiments
# TYPES=(optimal suboptimal optimal-noisy suboptimal-noisy)

CHECK_ONLY=false
GEN_LATEX=false
for arg in "$@"; do
    case "$arg" in
        --check) CHECK_ONLY=true ;;
        --latex) GEN_LATEX=true ;;
    esac
done

# DATASET_DIR="$(dirname "$REPO_DIR")/goal-plan-recognition-dataset"
DATASET_DIR="$(dirname "$REPO_DIR")/goal-plan-recognition-dataset-lp"
# DATASET_DIR="$(dirname "$REPO_DIR")/metric-goal-plan-recognition-dataset/dataset"

mkdir -p "$OUTPUTS_DIR"

MISSING=0
MERGED=0

for DOMAIN in "${DOMAINS[@]}"; do
    for TYPE in "${TYPES[@]}"; do
        DOMAIN_TYPE="$DOMAIN-$TYPE"
        if [[ "$TYPE" == *noisy* ]]; then
            METHODS="$METHODS_NOISY"
        else
            METHODS="$METHODS_BASE"
        fi

        for METHOD in $METHODS; do
            MERGED_FILE="$OUTPUTS_DIR/$DOMAIN_TYPE-$METHOD.output"
            PARTS=()
            ALL_PRESENT=true

            for OB in "${OBS[@]}"; do
                DATASET_OB_DIR="$DATASET_DIR/$DOMAIN_TYPE/$OB"
                OB_DIR="$RESULTS_DIR/$DOMAIN_TYPE/$METHOD/obs$OB"

                # Skip obs levels that have no dataset instances.
                mapfile -t EXPECTED < <(
                    find "$DATASET_OB_DIR" -maxdepth 1 -name "*.tar.bz2" \
                         2>/dev/null | sort
                )
                if [[ ${#EXPECTED[@]} -eq 0 ]]; then
                    continue
                fi

                if $CHECK_ONLY; then
                    # Per-instance cross-check: every .tar.bz2 must have a .output
                    for src in "${EXPECTED[@]}"; do
                        base="$(basename "$src" .tar.bz2)"
                        out="$OB_DIR/${base}.output"
                        if [[ ! -f "$out" ]]; then
                            echo "MISSING output: $DOMAIN_TYPE/$METHOD/obs$OB/${base}.output"
                            ALL_PRESENT=false
                            (( MISSING++ )) || true
                        elif ! grep -q "^> " "$out"; then
                            echo "TRUNCATED:      $DOMAIN_TYPE/$METHOD/obs$OB/${base}.output"
                            ALL_PRESENT=false
                            (( MISSING++ )) || true
                        fi
                    done
                    # Also flag output files with no matching dataset instance.
                    if [[ -d "$OB_DIR" ]]; then
                        mapfile -t ACTUAL < <(find "$OB_DIR" -name "*.output" | sort)
                        for out in "${ACTUAL[@]}"; do
                            base="$(basename "$out" .output)"
                            src="$DATASET_OB_DIR/${base}.tar.bz2"
                            if [[ ! -f "$src" ]]; then
                                echo "EXTRA output:   $DOMAIN_TYPE/$METHOD/obs$OB/${base}.output"
                                (( MISSING++ )) || true
                            fi
                        done
                    fi
                    continue
                fi

                if [[ ! -d "$OB_DIR" ]]; then
                    echo "MISSING dir:  $OB_DIR"
                    ALL_PRESENT=false
                    (( MISSING++ )) || true
                    continue
                fi
                # Collect instance files in sorted order (matches test_domain.py's sort)
                mapfile -t FILES < <(find "$OB_DIR" -name "*.output" | sort)
                if [[ ${#FILES[@]} -eq 0 ]]; then
                    echo "MISSING files: $OB_DIR/*.output"
                    ALL_PRESENT=false
                    (( MISSING++ )) || true
                else
                    PARTS+=("${FILES[@]}")
                fi
            done

            if $CHECK_ONLY; then
                $ALL_PRESENT && echo "OK:             $DOMAIN_TYPE / $METHOD"
                continue
            fi

            if [[ ${#PARTS[@]} -gt 0 ]]; then
                cat "${PARTS[@]}" > "$MERGED_FILE"
                echo "Merged $(( ${#PARTS[@]} )) files → $MERGED_FILE"
                (( MERGED++ )) || true
            fi
        done
    done
done

if $CHECK_ONLY; then
    echo ""
    if [[ $MISSING -eq 0 ]]; then
        echo "All instances accounted for."
    else
        echo "Issues found: $MISSING (missing, truncated, or extra output files)"
    fi
    exit 0
fi

echo ""
echo "Merged $MERGED .output files into $OUTPUTS_DIR"
echo ""

# Regenerate LaTeX tables from the merged .output files — same as:
#   cd experiments && ./get_results.sh -txt
echo "Regenerating data tables..."
cd "$REPO_DIR"
for DOMAIN in "${DOMAINS[@]}"; do
    for TYPE in "${TYPES[@]}"; do
        DOMAIN_TYPE="$DOMAIN-$TYPE"
        if [[ "$TYPE" == *noisy* ]]; then
            METHODS="$METHODS_NOISY"
        else
            METHODS="$METHODS_BASE"
        fi
        # Only run data_output.py if at least one merged .output file exists
        HAVE_ANY=false
        for METHOD in $METHODS; do
            [[ -f "$OUTPUTS_DIR/$DOMAIN_TYPE-$METHOD.output" ]] && HAVE_ANY=true && break
        done
        if $HAVE_ANY; then
            echo "  data_output.py for $DOMAIN_TYPE ..."
            python3 data_output.py "$METHODS" "$DOMAIN_TYPE" -D "$DATASET_DIR"
        fi
    done
done

echo "Done. Tables are in data-tables/ and data-charts/."

if $GEN_LATEX; then
    # Build explicit domain-type lists from DOMAINS array to avoid parse_domains()
    # expanding hardcoded shorthand keywords (optimal-all, etc.)
    BASE_DTS=()
    NOISY_DTS=()
    for D in "${DOMAINS[@]}"; do
        BASE_DTS+=("$D-optimal" "$D-suboptimal")
        NOISY_DTS+=("$D-optimal-noisy" "$D-suboptimal-noisy")
    done

    mkdir -p data-comparison data-charts latex-charts

    echo ""
    echo "Generating comparison tables..."
    # DELR methods (second paper)
    #python3 data_comparison.py delr  "delta-cdt delta-o-cdto delta-o-cdtb5 delta-o1-cdtb5" optimal suboptimal
    #python3 data_comparison.py delrf2 "delta-cdt-f2 delta-o-cdto-f2 delta-o-cdtb5-f2 delta-o1-cdtb5-f2" optimal-old-noisy suboptimal-old-noisy
    # LMC methods (JAIR 2021 paper)
    python3 data_comparison.py lmc   "$METHODS_BASE"  "${BASE_DTS[@]}"  -D "$DATASET_DIR"
    python3 data_comparison.py lmcf2 "$METHODS_NOISY" "${NOISY_DTS[@]}" -D "$DATASET_DIR"
    echo "Comparison tables are in data-comparison/."

    echo ""
    echo "Generating chart data files..."
    # DELR methods (second paper)
    #python3 data_charts.py "delta-cdt delta-o-cdto delta-o-cdtb5 delta-o1-cdtb5" all
    #python3 data_charts.py "delta-cdt-f2 delta-o-cdto-f2 delta-o-cdtb5-f2 delta-o1-cdtb5-f2" all
    # LMC methods (JAIR 2021 paper)
    python3 data_charts.py "$METHODS_BASE"  "${BASE_DTS[@]}"  -D "$DATASET_DIR"
    python3 data_charts.py "$METHODS_NOISY" "${NOISY_DTS[@]}" -D "$DATASET_DIR"
    echo "Chart data files are in latex-charts/."
fi
