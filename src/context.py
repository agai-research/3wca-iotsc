"""The family of formal contexts derived from the ICPS space (Defs. 5.1-5.3).
Author: F. Ghedass."""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np

from .model import Icps


def k_resource(sp: Icps):
    """K^r = (S, R, I_r): which service requires which IoT resource."""
    return sp.Ir, [r["id"] for r in sp.resources]


def k_feature(sp: Icps):
    """K^f = (S, F, I_f): which service possesses which functional feature."""
    return sp.If, [f["id"] for f in sp.features]


def k_conflict(sp: Icps):
    """K^c = (S, R, c) scaled to a binary context with attributes r+ and r-.

    FCA needs a binary incidence; the three-valued information is preserved by
    splitting each resource into a positive and a negative attribute.
    """
    pos, neg = (sp.S == 1), (sp.S == -1)
    inc = np.concatenate([pos, neg], axis=1)
    cols = [f"{r['id']}+" for r in sp.resources] + [f"{r['id']}-" for r in sp.resources]
    return inc, cols


def dump(sp: Icps, out: Path) -> dict:
    """Write the three formal contexts as JSON. Returns a small summary."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    info = {}
    for tag, (inc, cols) in {"r": k_resource(sp), "f": k_feature(sp),
                             "c": k_conflict(sp)}.items():
        rows = [s["id"] for s in sp.services]
        (out / f"ctx_{tag}.json").write_text(json.dumps({
            "objects": rows, "attributes": cols,
            "incidence": [[int(x) for x in np.nonzero(r)[0]] for r in inc]}))
        info[tag] = {"objects": len(rows), "attributes": len(cols),
                     "fill": round(float(inc.mean()), 5)}
    return info
