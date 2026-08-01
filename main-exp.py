#!/usr/bin/env python3
"""Entry point: run every experiment, then rebuild the tables and figures.
Author: F. Ghedass."""
from __future__ import annotations
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).parent / "experiments" / "main-exp.py"),
                   run_name="__main__")
