"""Switchback: backcountry permit availability and trip planning engine."""
__version__ = "2.28.0"

from .api import (search_permits, get_divisions, fetch_division_month,
                  classify_status, daterange, fetch_availability_rows,
                  HEADERS, PLACEHOLDER_THRESHOLD, BASE, UA)
from .config import load_profile, DEFAULT_PROFILE
from .extract import extract_park, save_park, load_park
from .graph import Graph
from .solver import Solver, fetch_availability
from .scoring import Scorer, load_scoring
