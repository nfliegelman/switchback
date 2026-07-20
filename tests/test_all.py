"""Standard-discovery wrapper (v3.3.0): every legacy invariant script in
this directory runs as a pytest case, so `python -m pytest -q` exercises
the full suite instead of discovering a single test. The scripts remain
runnable directly; this file only subprocesses them."""
import glob
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(__file__)
SCRIPTS = sorted(p for p in glob.glob(os.path.join(HERE, "test_*.py"))
                 if os.path.basename(p) != "test_all.py")


@pytest.mark.parametrize("script", SCRIPTS,
                         ids=[os.path.basename(p) for p in SCRIPTS])
def test_invariant_script(script):
    r = subprocess.run([sys.executable, script], capture_output=True,
                       text=True, cwd=os.path.dirname(HERE))
    assert r.returncode == 0, (r.stdout + r.stderr)[-2000:]
