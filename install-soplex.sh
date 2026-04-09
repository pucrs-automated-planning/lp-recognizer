#!/usr/bin/env bash
#
# install-soplex.sh
# Installs SoPlex LP solver to a user-local directory (no sudo required).
#
# Environment variables you can set before running:
#   soplex_DIR       - where to install SoPlex (default: $HOME/.local/soplex)
#   SOPLEX_GIT_TAG   - soplex git tag to build (default: release-604)
#
# On HPC clusters, make sure cmake and a C++ compiler are available first:
#   module load cmake gcc   (or equivalent for your cluster)

die() { echo "ERROR: $*" >&2; exit 1; }

SOPLEX_GIT_TAG="${SOPLEX_GIT_TAG:-release-604}"

if [[ -z "${soplex_DIR:-}" ]]; then
    export soplex_DIR="$HOME/.local/soplex"
fi

if [[ -d "$soplex_DIR" ]]; then
    echo "SoPlex already present at ${soplex_DIR}"
    exit 0
fi

# Check prerequisites
MISSING=()
for cmd in git cmake g++; do
    if ! command -v "$cmd" &>/dev/null; then
        MISSING+=("$cmd")
    fi
done
if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "ERROR: Required tools not found: ${MISSING[*]}"
    echo "Install them or load the appropriate modules, e.g.:"
    echo "  module load cmake gcc"
    exit 1
fi

echo "Installing SoPlex (tag: ${SOPLEX_GIT_TAG}) to ${soplex_DIR}"

BUILD_TMP=$(mktemp -d)
trap 'rm -rf "$BUILD_TMP"' EXIT

git clone --branch "${SOPLEX_GIT_TAG}" --depth 1 \
    https://github.com/scipopt/soplex.git "${BUILD_TMP}/soplex" \
    || die "Failed to clone SoPlex tag '${SOPLEX_GIT_TAG}'. Try a different SOPLEX_GIT_TAG."

export CXXFLAGS="${CXXFLAGS:-} -Wno-use-after-free"
NPROC=$(nproc 2>/dev/null || sysctl -n hw.logicalcpu 2>/dev/null || echo 4)

cmake -S "${BUILD_TMP}/soplex" -B "${BUILD_TMP}/build" \
    -DCMAKE_INSTALL_PREFIX="${soplex_DIR}" \
    -DCMAKE_BUILD_TYPE=Release \
    || die "CMake configuration failed."

cmake --build "${BUILD_TMP}/build" -j"${NPROC}" \
    || die "SoPlex build failed."

cmake --install "${BUILD_TMP}/build" \
    || die "SoPlex installation to '${soplex_DIR}' failed."

echo "SoPlex installed to ${soplex_DIR}"

# Persist settings to shell config files
for RC_FILE in "${HOME}/.profile" "${HOME}/.bashrc"; do
    if [[ -f "$RC_FILE" ]] || [[ "$RC_FILE" == "${HOME}/.profile" ]]; then
        if ! grep -q "soplex_DIR" "$RC_FILE" 2>/dev/null; then
            printf '\nexport soplex_DIR="%s"\nexport lpr_solver=soplex\n' "${soplex_DIR}" >> "$RC_FILE"
            echo "  Written to $RC_FILE"
        fi
    fi
done

echo ""
echo "To activate in the current shell:"
echo "  export soplex_DIR=\"${soplex_DIR}\""
echo "  export lpr_solver=soplex"
