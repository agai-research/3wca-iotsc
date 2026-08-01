"""E7 (supplementary) - conflict density x workflow size cross-sweep.

The six experiments of the paper vary one factor at a time, which cannot show
how the factors interact. This supplementary sweep evaluates the four methods on
a full grid, so that the response of each method can be drawn as a surface.
It is not one of the paper's experiments and is reported only in the additional
figures.
Author: F. Ghedass.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Data.gen_inst import set_density, slice_space      # noqa: E402
from experiments.runner import sweep                    # noqa: E402
from src.conf import load, setup_log                    # noqa: E402
from src.model import Icps                              # noqa: E402
from src.paths import AGG, MAIN                         # noqa: E402

TAG = "exp7_grid"
DENS = [10, 20, 30, 40, 50]        # conflict density (%)
TASKS = [5, 10, 20, 30, 50]        # abstract workflow size


def run(cfg=None):
    cfg = cfg or load("exp7_grid.yaml")
    log = setup_log(TAG)
    base = Icps.from_json(MAIN / "icps_main.json")
    grid = {}
    for nt in TASKS:
        c = json.loads(json.dumps(cfg))
        c["query"]["n_tasks"] = nt

        def build(pt, rng, c=c):
            sp = slice_space(base, c["dataset"]["n_services"],
                             c["dataset"]["n_resources"], rng)
            return set_density(sp, pt / 100.0, rng), None

        agg = sweep(f"{TAG}_{nt}", DENS, build, c, log)
        grid[str(nt)] = agg
    (AGG / f"{TAG}.json").write_text(json.dumps(grid, indent=1))
    log.info("grid written: %d x %d points", len(TASKS), len(DENS))
    return grid


if __name__ == "__main__":
    run()
