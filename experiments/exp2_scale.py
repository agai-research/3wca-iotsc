"""E2 - Scalability with the ICPS space size (Section 8.3).

The total number of entities grows from 200 to 2000 with a 2:1 service-to-
resource ratio. Produces Table 17 and Figure 10.
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

TAG = "exp2_scale"
POINTS = [200, 500, 1000, 1500, 2000]


def _sets(prep, co, sp, truth, cfg):
    return {"delta": len(co.delta), "gamma": len(co.gamma), "psi": len(co.psi),
            "lattice_s": prep.timing["lattice_s"] + prep.timing["analysis_s"]}


def run(cfg=None):
    cfg = cfg or load("exp2_scale.yaml")
    log = setup_log(TAG)
    base = Icps.from_json(MAIN / "icps_scale.json")

    def build(pt, rng):
        ns, nr = int(round(pt * 2 / 3)), int(round(pt / 3))
        sp = slice_space(base, ns, nr, rng)
        return set_density(sp, cfg["dataset"]["density"], rng), None

    return sweep(TAG, POINTS, build, cfg, log, extra=_sets)


if __name__ == "__main__":
    run()
