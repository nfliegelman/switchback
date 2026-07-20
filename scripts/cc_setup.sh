#!/bin/bash
# Claude Code session setup. Engine is stdlib-only; these are the test
# and GUI extras so the suite runs green in fresh environments.
if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then exit 0; fi
pip install --quiet fastapi httpx uvicorn shapely 2>/dev/null || \
  pip install --quiet --break-system-packages fastapi httpx uvicorn shapely
exit 0
