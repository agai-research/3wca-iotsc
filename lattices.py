#!/usr/bin/env python3
"""Entry point: build the family of formal contexts and lattices from the dataset.

Writes ctx_{r,f,c}.json and lat_{r,f,c}.json for the requested ICPS space.
Author: F. Ghedass.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src import context, lattice as lt             # noqa: E402
from src.conf import load, setup_log               # noqa: E402
from src.model import Icps                         # noqa: E402
from src.paths import INST, MAIN, ensure           # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="build the formal contexts and lattices")
    ap.add_argument("--space", default=str(MAIN / "icps_main.json"))
    ap.add_argument("--name", default="main", help="instance folder under Data/inst")
    ap.add_argument("--config", default="default.yaml")
    ap.add_argument("--log-level", default="INFO")
    args = ap.parse_args()

    ensure()
    log = setup_log("lattices", args.log_level)
    cfg = load(args.config)
    sp = Icps.from_json(Path(args.space))
    out = INST / args.name
    out.mkdir(parents=True, exist_ok=True)

    info = context.dump(sp, out)
    log.info("formal contexts written to %s: %s", out, info)

    lc = cfg["lattice"]
    summary = {}
    for tag, (inc, cols) in {"r": context.k_resource(sp), "f": context.k_feature(sp),
                             "c": context.k_conflict(sp)}.items():
        cps = lt.build(inc, lc["min_support"], lc["cap"])
        meta = {"builder": "iceberg-intersection", "min_support": lc["min_support"],
                "cap": lc["cap"], "capped": len(cps) >= lc["cap"]}
        lt.save(cps, out / f"lat_{tag}.json", [s["id"] for s in sp.services], cols, meta)
        summary[tag] = len(cps)
        log.info("lattice L^%s: %d concepts (capped=%s)", tag, len(cps), meta["capped"])
    (out / "summary.json").write_text(json.dumps({"contexts": info,
                                                  "lattices": summary}, indent=1))


if __name__ == "__main__":
    main()
