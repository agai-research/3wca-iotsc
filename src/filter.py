"""Algorithm 2: resource- and QoS-aware filtering of the candidate IoT services.

The resource lattice L^r is parsed with the largest extents first; a concept is
kept when its services cover at least one abstract task together with the IoT
resource that task needs. The result is then refined through the concept of the
features lattice L^f whose Intent covers the requested features F_u.
Author: F. Ghedass.
"""
from __future__ import annotations

from . import lattice as lt


def run(sp, lat_r: list, lat_f: list, workflow: list, feats: set) -> list:
    """Return W_c, the candidate service indices."""
    caps = sp.caps()
    pending = list(workflow)
    wc: set = set()

    for ext, intent in lat_r:                      # already sorted by extent size
        if not pending:
            break
        hit = False
        for task in list(pending):
            able = set(caps.get(task["capability"], []))
            rj = sp.ri.get(task.get("resource"))
            if (ext & able) and (rj is None or rj in intent):
                pending.remove(task)
                hit = True
        if hit:
            wc |= set(ext)

    # QoS / feature refinement (Algorithm 2, lines 13-18)
    if feats:
        want = {sp.fi[f] for f in feats if f in sp.fi}
        cpt = lt.locate(lat_f, want)
        if cpt is not None:
            wc &= set(cpt[0])
    return sorted(wc)
