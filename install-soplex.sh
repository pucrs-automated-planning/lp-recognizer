#!/usr/bin/env bash
#
# install-soplex.sh
# Installs SoPlex LP solver to a user-local directory (no sudo required).
#
# Environment variables you can set before running:
#   soplex_DIR       - where to install SoPlex (default: $HOME/.local/soplex)
#   SOPLEX_GIT_TAG   - soplex git tag to build (default: release-710)
#
# On HPC clusters, make sure cmake and a C++ compiler are available first:
#   module load cmake gcc   (or equivalent for your cluster)

die() { echo "ERROR: $*" >&2; exit 1; }

SOPLEX_GIT_TAG="${SOPLEX_GIT_TAG:-release-604}"

if [[ -z "${soplex_DIR:-}" ]]; then
    export soplex_DIR="$HOME/.local/soplex"
fi

SOPLEX_INSTALL_PREFIX="${soplex_DIR}"

if [[ ! -d "$SOPLEX_INSTALL_PREFIX" ]]; then
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

    echo "Installing SoPlex (tag: ${SOPLEX_GIT_TAG}) to ${SOPLEX_INSTALL_PREFIX}"

    BUILD_TMP=$(mktemp -d)
    trap 'rm -rf "$BUILD_TMP"' EXIT

    git clone --branch "${SOPLEX_GIT_TAG}" --depth 1 \
        https://github.com/scipopt/soplex.git "${BUILD_TMP}/soplex" \
        || die "Failed to clone SoPlex tag '${SOPLEX_GIT_TAG}'. Try a different SOPLEX_GIT_TAG."

    export CXXFLAGS="${CXXFLAGS:-} -Wno-use-after-free"
    NPROC=$(nproc 2>/dev/null || sysctl -n hw.logicalcpu 2>/dev/null || echo 4)

    # On macOS, both SoPlex and FD must use the same compiler to avoid ABI mismatches.
    # Uncomment below (and the matching block in prepare-fd.sh) to force Homebrew GCC
    # instead of Apple Clang if the default compiler does not work.
    # if [[ "$(uname -s)" == "Darwin" ]] && [[ -z "${CXX:-}" ]]; then
    #     _BREW_GXX=$(ls "$(brew --prefix gcc 2>/dev/null)/bin/g++-"* 2>/dev/null | sort -V | tail -1)
    #     if [[ -x "${_BREW_GXX:-}" ]]; then
    #         export CC="${_BREW_GXX//g++/gcc}"
    #         export CXX="${_BREW_GXX}"
    #         echo "macOS: using Homebrew GCC (${CXX})"
    #     fi
    # fi

    cmake -S "${BUILD_TMP}/soplex" -B "${BUILD_TMP}/build" \
        -DCMAKE_INSTALL_PREFIX="${SOPLEX_INSTALL_PREFIX}" \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
        -DBOOST=off \
        -DGMP=off \
        || die "CMake configuration failed."

    cmake --build "${BUILD_TMP}/build" -j"${NPROC}" \
        || die "SoPlex build failed."

    cmake --install "${BUILD_TMP}/build" \
        || die "SoPlex installation to '${SOPLEX_INSTALL_PREFIX}' failed."

else
    echo "SoPlex already present at ${SOPLEX_INSTALL_PREFIX}"
fi

# Verify the cmake config was installed (lib vs lib64 varies by platform/distro).
SOPLEX_CMAKE_FOUND=0
for candidate in \
    "${SOPLEX_INSTALL_PREFIX}/lib/cmake/soplex" \
    "${SOPLEX_INSTALL_PREFIX}/lib64/cmake/soplex"; do
    if [[ -f "${candidate}/soplex-config.cmake" ]]; then
        SOPLEX_CMAKE_FOUND=1
        break
    fi
done
if [[ $SOPLEX_CMAKE_FOUND -eq 0 ]]; then
    die "Could not find soplex-config.cmake under ${SOPLEX_INSTALL_PREFIX}. Installation may be incomplete."
fi

# soplex_DIR is the install prefix; CMake's find_package searches lib/cmake and
# lib64/cmake inside it automatically, so no need to point at the subdir directly.
echo ""
echo "SoPlex ready at ${SOPLEX_INSTALL_PREFIX}"
echo "Before building Fast Downward, export:"
echo "  export soplex_DIR=\"${SOPLEX_INSTALL_PREFIX}\""
