"""E1 - Impact of conflict density on composition reliability (Section 8.2).

sigma varies from 10% to 50% under |S|=500, |R|=200, |W_u|=10. Produces Table 16.
Author: F. Ghedass.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Data.gen_inst import set_density, slice_space      # noqa: E402
from experiments.runner import sweep                    # noqa: E402
from src.conf import load, setup_log                    # noqa: E402
from src.model import Icps                              # noqa: E402
from src.paths import MAIN                              # noqa: E402

TAG = "exp1_density"
POINTS = [10, 20, 30, 40, 50]


def run(cfg=None):
    cfg = cfg or load("exp1_density.yaml")
    log = setup_log(TAG)
    base = Icps.from_json(MAIN / "icps_main.json")

    def build(pt, rng):
        sp = slice_space(base, cfg["dataset"]["n_services"],
                         cfg["dataset"]["n_resources"], rng)
        return set_density(sp, pt / 100.0, rng), None

    return sweep(TAG, POINTS, build, cfg, log)


if __name__ == "__main__":
    run()
