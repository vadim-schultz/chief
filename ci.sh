#!/usr/bin/env bash
# Repository harness. Runs every stage in order and stops at the first failing stage.
# Usage: ./ci.sh [all|lint|unit]
set -euo pipefail

# Hermetic tool environment: ignore the workstation uv, pip and npm settings, which point at corporate mirrors.
# UV_NO_CONFIG stops uv from discovering configuration files. tox.ini passes --default-index explicitly, so the
# public index is also set in UV_DEFAULT_INDEX.
export UV_NO_CONFIG=1
export UV_DEFAULT_INDEX=https://pypi.org/simple
export PIP_CONFIG_FILE=/dev/null
export NPM_CONFIG_USERCONFIG=/dev/null

script_path=${BASH_SOURCE[0]}
script_dir=${script_path%/*}
if [[ $script_dir == "$script_path" ]]; then
  script_dir=.
fi
cd -- "$script_dir"

declare -A MODE_STAGES=(
  [all]="format lint types unit build"
  [lint]="format lint types"
  [unit]="unit"
)

mode=${1:-all}
if [[ -z ${MODE_STAGES[$mode]+set} ]]; then
  echo "ci: unknown mode $mode" >&2
  exit 2
fi
read -r -a stages <<<"${MODE_STAGES[$mode]}"

resolve_unit_args() {
  unit_args=()
  if [[ -n ${CI_HARNESS_NESTED:-} ]]; then
    unit_args=(--ignore=tests/ci)
  fi
}
resolve_unit_args

stage_format() { tox -e format-check; }
stage_lint() { tox -e check; }
stage_types() { tox -e types -- --error-on-warning; }
stage_unit() { tox -e test-pytest -- "${unit_args[@]}"; }
stage_build() { tox -e build; }

require_tool() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ci: missing tool $1" >&2
    exit 1
  fi
}

REQUIRED_TOOLS=(uv tox)
for tool in "${REQUIRED_TOOLS[@]}"; do
  require_tool "$tool"
done

run_stage() {
  echo "ci: stage $1"
  if ! "stage_$1"; then
    echo "ci: stage $1 failed" >&2
    exit 1
  fi
}

for stage in "${stages[@]}"; do
  run_stage "$stage"
done
