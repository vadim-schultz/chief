#!/usr/bin/env bash
# CI harness for TypeScript repositories. Runs five stages in order and stops at the first failing stage.
set -euo pipefail

# One row per stage: the stage name and its tool.
STAGES=("format npx" "lint npx" "types npx" "unit npx" "build npm")

stage_format() { npx prettier --check .; }
stage_lint() { npx eslint .; }
stage_types() { npx tsc --noEmit; }
stage_unit() { npx vitest run; }
stage_build() { npm run build; }

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
