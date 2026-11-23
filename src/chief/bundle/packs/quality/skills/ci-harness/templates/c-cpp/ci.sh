#!/usr/bin/env bash
# CI harness for C and C++ repositories built with CMake. Runs five stages in order and stops at the first failing stage.
set -euo pipefail

# One row per stage: the stage name and its tool.
STAGES=("format clang-format" "lint clang-tidy" "types cmake" "unit ctest" "build cmake")

# Sets SOURCES to the files that match the find expression, outside the build directories.
find_sources() {
  mapfile -d '' SOURCES < <(find . -path './build*' -prune -o "$@" -print0)
}

stage_format() { find_sources \( -name '*.cpp' -o -name '*.h' \) && clang-format --dry-run --Werror "${SOURCES[@]}"; }
stage_lint() {
  find_sources -name '*.cpp' &&
    cmake -S . -B build-lint -DCMAKE_EXPORT_COMPILE_COMMANDS=ON >/dev/null &&
    clang-tidy -p build-lint --warnings-as-errors='*' "${SOURCES[@]}"
}
stage_types() {
  cmake -S . -B build-types -DCMAKE_CXX_FLAGS="-Wall -Wextra -Werror" >/dev/null &&
    cmake --build build-types
}
stage_unit() {
  cmake -S . -B build-unit -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-omit-frame-pointer" \
    -DCMAKE_EXE_LINKER_FLAGS="-fsanitize=address,undefined" >/dev/null &&
    cmake --build build-unit &&
    ctest --test-dir build-unit --output-on-failure
}
stage_build() {
  cmake -S . -B build-release -DCMAKE_BUILD_TYPE=Release >/dev/null &&
    cmake --build build-release
}

require_tool() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ci: missing tool $1" >&2
    exit 1
  fi
  echo "ci: tool $1 found"
}

run_stage() {
  echo "ci: stage $1"
  require_tool "$2"
  if ! "stage_$1"; then
    echo "ci: stage $1 failed" >&2
    exit 1
  fi
}

for row in "${STAGES[@]}"; do
  read -r stage tool <<<"$row"
  run_stage "$stage" "$tool"
done
