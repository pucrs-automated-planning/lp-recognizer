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

echo "Building Fast Downward..."
pushd "$FD_ROOT" > /dev/null
    ./build.py release || die "Fast Downward build failed."
popd > /dev/null

echo ""
echo "Done. Fast Downward built at ${FD_ROOT}"
