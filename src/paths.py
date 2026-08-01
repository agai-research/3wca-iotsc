"""Single source of truth for every path in the repository. Author: F. Ghedass."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
DATA = ROOT / "Data"
MAIN = DATA / "main"
INST = DATA / "inst"
# TWCA_RESULTS lets a demo (e.g. a notebook) write elsewhere than results/,
# so a quick run never overwrites the shipped full-protocol results.
RESULTS = Path(os.environ.get("TWCA_RESULTS", ROOT / "results"))
RAW = RESULTS / "raw"
AGG = RESULTS / "agg"
FIGS = RESULTS / "figs"
LOGS = RESULTS / "logs"
TABLES = RESULTS / "tables"
DOCS = ROOT / "docs"
TEST = ROOT / "Test"


def ensure() -> None:
    """Create the output folders if they are missing."""
    for p in (MAIN, INST, RAW, AGG, FIGS, LOGS, TABLES, DOCS):
        p.mkdir(parents=True, exist_ok=True)
