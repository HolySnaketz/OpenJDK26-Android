#!/usr/bin/env bash
set -euo pipefail
taskroot=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
mkdir -p "$taskroot/logs/patch-audit"
cd "${1:-$taskroot/source/openjdk}"
: > "$taskroot/logs/patch-audit/summary.tsv"
for patchfile in "$taskroot/recipes/openjdk-26/"*.patch; do
    name=$(basename "$patchfile")
    if patch --dry-run --batch --fuzz=0 -p1 -i "$patchfile" > "$taskroot/logs/patch-audit/$name.log" 2>&1; then
        printf 'APPLIES\t%s\n' "$name"
    else
        printf 'REBASE_REQUIRED\t%s\n' "$name"
    fi
done | tee "$taskroot/logs/patch-audit/summary.tsv"
