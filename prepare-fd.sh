#!/usr/bin/env bash
#
# prepare-fd.sh
# Downloads, patches, and builds Fast Downward for use with lp-recognizer.
#
# Can be run from any directory.
#
# On HPC clusters, make sure build tools are available first, e.g.:
#   module load cmake gcc python3

die() { echo "ERROR: $*" >&2; exit 1; }

DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Check prerequisites
MISSING=()
for cmd in git python3 cmake g++ patch; do
    if ! command -v "$cmd" &>/dev/null; then
        MISSING+=("$cmd")
    fi
done
if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "ERROR: Required tools not found: ${MISSING[*]}"
    echo "Install them or load the appropriate modules, e.g.:"
    echo "  module load cmake gcc python3"
    exit 1
fi

# Create output directories
for d in data-domains data-charts data-tables data-comparison outputs; do
    mkdir -p "${DIR}/${d}"
done

FD_REV=$(cat "${DIR}/fd-patch-rev")
PARENT=$(cd "${DIR}/.." && pwd)
FD_ROOT="${PARENT}/fast-downward"

if [[ ! -d "$FD_ROOT" ]]; then
    echo "Downloading Fast Downward..."
    git clone https://github.com/aibasel/downward.git "$FD_ROOT" \
        || die "Failed to clone Fast Downward."
else
    echo "Fast Downward found at $FD_ROOT"
fi

echo "Checking out revision ${FD_REV}..."
pushd "$FD_ROOT" > /dev/null
    git reset --hard
    git clean -fd .
    git checkout "$FD_REV" || die "Could not check out FD revision ${FD_REV}."
popd > /dev/null

echo "Applying LP-Recognizer patch..."
pushd "$PARENT" > /dev/null
    patch -s -p0 -i "${DIR}/fd-patch.diff" \
        || die "Patch failed. Check if fd-patch.diff is compatible with FD rev ${FD_REV}."
popd > /dev/null
echo "Patch applied successfully."

# FindCplex.cmake only lists x86-64/x64 as bitwidth hints; add arm64 for Apple Silicon.
# On x86-64 Linux/macOS, arm64_* paths won't exist so cmake falls through harmlessly.
sed -i.bak 's/set(BITWIDTH_HINTS "x86-64" "x64")/set(BITWIDTH_HINTS "arm64" "x86-64" "x64")/' \
    "${FD_ROOT}/src/search/cmake/FindCplex.cmake"

echo "Building Fast Downward..."

# Require at least one LP solver — the operator-counting heuristics won't work without one.
if [[ -z "${soplex_DIR:-}" && -z "${cplex_DIR:-}" ]]; then
    DEFAULT_SOPLEX="$HOME/.local/soplex"
    if [[ -f "${DEFAULT_SOPLEX}/include/soplex.h" ]]; then
        export soplex_DIR="${DEFAULT_SOPLEX}"
        echo "soplex_DIR not set; found SoPlex at default location, using ${soplex_DIR}"
    else
        die "No LP solver found. Set one of the following before running this script:" \
$'\n  export soplex_DIR=<path>   # e.g. $HOME/.local/soplex  (run install-soplex.sh first)' \
$'\n  export cplex_DIR=<path>    # macOS: /Applications/CPLEX_Studio<ver>/cplex' \
$'\n                             # Linux: /opt/ibm/ILOG/CPLEX_Studio<ver>/cplex'
    fi
fi

# On macOS, prefer Homebrew GCC over Apple Clang to match the compiler used for SoPlex.
# if [[ "$(uname -s)" == "Darwin" ]] && [[ -z "${CXX:-}" ]]; then
#     _BREW_GXX=$(ls "$(brew --prefix gcc 2>/dev/null)/bin/g++-"* 2>/dev/null | sort -V | tail -1)
#     if [[ -x "${_BREW_GXX:-}" ]]; then
#         export CC="${_BREW_GXX//g++/gcc}"
#         export CXX="${_BREW_GXX}"
#         echo "macOS: using Homebrew GCC (${CXX})"
#     fi
# fi

# cmake reads CMAKE_PREFIX_PATH from the environment for find_package() searches.
# This lets build.py pass the solver locations without modifying its configure args.
if [[ -n "${soplex_DIR:-}" ]]; then
    export CMAKE_PREFIX_PATH="${soplex_DIR}${CMAKE_PREFIX_PATH:+:${CMAKE_PREFIX_PATH}}"
fi
if [[ -n "${cplex_DIR:-}" ]]; then
    export CMAKE_PREFIX_PATH="${cplex_DIR}${CMAKE_PREFIX_PATH:+:${CMAKE_PREFIX_PATH}}"
fi

pushd "$FD_ROOT" > /dev/null
    # Remove stale cmake cache so solver detection re-runs with current env vars.
    rm -f builds/release/CMakeCache.txt
    python3 build.py release || die "Fast Downward build failed."
popd > /dev/null

echo ""
echo "Done. Fast Downward built at ${FD_ROOT}"
