#!/usr/bin/env bash
set -euo pipefail

# Offline checks for the global config and skills.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

fail() {
  printf 'not ok: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  [ -f "$1" ] || fail "missing file: $1"
  grep -Fq -- "$2" "$1" || fail "$1 does not contain: $2"
}

assert_not_contains() {
  [ -f "$1" ] || fail "missing file: $1"
  if grep -Fq -- "$2" "$1"; then
    fail "$1 unexpectedly contains: $2"
  fi
}

# The project-escape invocation has one public surface: `sandbox-escape <name> <args>`,
# never a per-target or by-path form. These pins moved here from agents-modes, whose
# tests must not reach outside their own repo.
for skill in standard-project add-escape; do
  doc="$ROOT/skills/$skill/SKILL.md"
  assert_contains "$doc" 'sandbox-escape <name> <args>'
  assert_not_contains "$doc" 'codex/bin/sandbox-escape'
  assert_not_contains "$doc" 'Invoke as `./sandbox-escapes/<name>'
  assert_not_contains "$doc" 'Invoke by path'
done

printf 'ok - agents-global offline checks passed\n'
