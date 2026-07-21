#!/usr/bin/env bash
# Canonical Switchback quality checks. CI runs this exact script, so local
# and CI never drift. Run it from anywhere; it moves to the repo root.
#
# One-time setup (dev machine or CI runner):
#   pip install -r requirements-web.txt -r requirements-dev.txt
#
# Exits nonzero if any check fails. The engine itself stays stdlib only;
# these tools are only for running the checks and the web tests.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0

echo "== 1/3 dash gate (no en or em dashes anywhere) =="
python3 - <<'PY' || fail=1
import pathlib, sys
EXTS = {".py", ".md", ".json", ".txt", ".js", ".html", ".webmanifest",
        ".yml", ".yaml", ".bat", ".sh"}
bad = []
for p in pathlib.Path(".").rglob("*"):
    s = str(p)
    if "/.git/" in s or not p.is_file() or p.suffix not in EXTS:
        continue
    try:
        t = p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    if "\u2013" in t or "\u2014" in t:
        bad.append(s)
if bad:
    print("FAIL: en or em dashes found in:")
    for b in sorted(bad):
        print("  ", b)
    sys.exit(1)
print("clean")
PY

echo "== 2/3 ruff (pyflakes: unused imports, dead variables, undefined names) =="
if command -v ruff >/dev/null 2>&1; then
    ruff check . || fail=1
else
    echo "FAIL: ruff is not installed (pip install -r requirements-dev.txt)"
    fail=1
fi

echo "== 3/3 pytest (full offline suite) =="
python3 -m pytest -q || fail=1

echo ""
if [ "$fail" -ne 0 ]; then
    echo "QUALITY CHECKS FAILED"
    exit 1
fi
echo "ALL QUALITY CHECKS PASSED"
