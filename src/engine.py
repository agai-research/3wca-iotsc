"""End-to-end 3WCA-IoTSC pipeline (Fig. 4 of the paper).

prepare() performs the offline stages - contexts, lattices, 3WCA analysis and
the construction of Delta / Gamma / psi. answer() runs the per-query stages -
resource- and QoS-aware filtering then consensus-based composition.
Author: F. Ghedass.
"""
from __future__ import annotations
import time
from dataclasses import dataclass

import numpy as np

from . import analysis, compose, context, filter as flt, lattice as lt


@dataclass
class Prepared:
    lat_r: list
    lat_f: list
    lat_c: list
    co: analysis.Coalitions
    timing: dict


def prepare(sp, cfg: dict, with_conflict: bool = True) -> Prepared:
    """Build the lattice family and run Algorithm 1."""
    lc = cfg["lattice"]
    t0 = time.perf_counter()
    inc_r, _ = context.k_resource(sp)
    inc_f, _ = context.k_feature(sp)
    lat_r = lt.build(inc_r, lc["min_support"], lc["cap"])
    lat_f = lt.build(inc_f, lc["min_support"], lc["cap"])
    t_lat = time.perf_counter() - t0

    lat_c, co = [], None
    t_an = 0.0
    if with_conflict:
        t1 = time.perf_counter()
        inc_c, _ = context.k_conflict(sp)
        lat_c = lt.build(inc_c, lc["min_support"], lc["cap"])
        co = analysis.run(sp.S, cfg, np.random.default_rng(cfg.get("seed", 0)))
        t_an = time.perf_counter() - t1
    return Prepared(lat_r, lat_f, lat_c, co,
                    {"lattice_s": t_lat, "analysis_s": t_an,
                     "n_cpt_r": len(lat_r), "n_cpt_f": len(lat_f),
                     "n_cpt_c": len(lat_c)})


def answer(sp, prep: Prepared, query: dict, cfg: dict):
    """Filter (Algorithm 2) then compose (Algorithm 3) for one user query."""
    wc = flt.run(sp, prep.lat_r, prep.lat_f, query["workflow"], set(query["features"]))
    res = compose.run(sp, prep.co, wc, query["workflow"], cfg)
    return wc, res
