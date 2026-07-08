"""switchback.config: the one saved effort profile (2026-07-07 decision).

Limits are miles and gain only; grade returns after the DEM pass.
profile.json in the repo root is config, not state; edit it freely.
"""
import json
import os

DEFAULT_PROFILE = {
    "party_size": 2,
    "daily_pref": {"miles": 9.0, "gain_ft": 2200},
    "daily_max": {"miles": 13.0, "gain_ft": 4000},
    "trip_type": "loop",
    "include_walkup": False,
}

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_PATH = os.path.join(_REPO_ROOT, "profile.json")


def load_profile(path=None):
    """Defaults merged under whatever the profile file provides."""
    path = path or PROFILE_PATH
    prof = json.loads(json.dumps(DEFAULT_PROFILE))
    try:
        with open(path) as fh:
            user = json.load(fh)
    except (OSError, ValueError):
        return prof
    for k, v in user.items():
        if isinstance(v, dict) and isinstance(prof.get(k), dict):
            prof[k].update(v)
        else:
            prof[k] = v
    return prof
