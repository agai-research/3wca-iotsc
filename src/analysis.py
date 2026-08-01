"""Algorithm 1: computation of the IoT services' coalitions.

Returns the maximum service coalition Delta, the minimum conflict set Gamma
(as minimal generators, reading A1) and the neutral service set psi.

Region assignment follows the priority Delta > Gamma > psi (adjustment A6):
a service belongs to Gamma's region when its conflict degree exceeds
theta_Gamma, which is the rule that reproduces Table 14 of the paper.
Author: F. Ghedass.
"""
from __future__ import annotations
from dataclasses import dataclass

import numpy as np

from . import trisect as tr
from . import degrees as dg


@dataclass
class Coalitions:
    delta: list          # maximum coalition of allied services
    gamma: list          # minimal conflict generators (i, j, r)
    psi: list            # neutral services
    mu_d: np.ndarray
    mu_g: np.ndarray
    mu_p: np.ndarray
    adj: np.ndarray      # conflict adjacency
    ally: np.ndarray
    region: list
    cliques: list        # conflicting concepts with m(E) > t2 (small spaces only)


def _greedy_mis(adj: np.ndarray, ally: np.ndarray, rng, restarts: int = 12) -> list:
    """Largest conflict-free service set; ties broken by alliance density."""
    n = adj.shape[0]
    deg = adj.sum(axis=1)
    best, best_key = [], (-1, -1)
    orders = [np.argsort(deg, kind="stable")]
    for _ in range(restarts - 1):
        orders.append(rng.permutation(n))
    for order in orders:
        chosen: list = []
        blocked = np.zeros(n, dtype=bool)
        for i in order:
            if not blocked[i]:
                chosen.append(int(i))
                blocked |= adj[i]
                blocked[i] = True
        allied = int(ally[np.ix_(chosen, chosen)].sum()) if chosen else 0
        key = (len(chosen), allied)
        if key > best_key:
            best, best_key = sorted(chosen), key
    return best


def _exact_mis(adj: np.ndarray, ally: np.ndarray) -> list:
    """Exhaustive search, used only for small spaces (e.g. the running example)."""
    import networkx as nx
    n = adj.shape[0]
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for i in range(n):
        for k in range(i + 1, n):
            if not adj[i, k]:
                g.add_edge(i, k)          # complement graph
    best, best_key = [], (-1, -1)
    for cl in nx.find_cliques(g):
        allied = int(ally[np.ix_(cl, cl)].sum())
        key = (len(cl), allied)
        if key > best_key:
            best, best_key = sorted(cl), key
    return best


def _cliques(adj: np.ndarray, t2: float, limit: int = 30) -> list:
    """Service groups classified into the conflict region, i.e. m(E) > t2."""
    n = adj.shape[0]
    if n > limit:
        return []
    import networkx as nx
    g = nx.from_numpy_array(adj.astype(int))
    out = []
    for cl in nx.find_cliques(g):
        if len(cl) > 1 and tr.m_measure(adj, cl) > t2:
            out.append(sorted(int(x) for x in cl))
    return sorted(out)


def run(S: np.ndarray, cfg: dict, rng=None, exact: bool | None = None) -> Coalitions:
    """Algorithm 1 end to end."""
    rng = rng or np.random.default_rng(cfg.get("seed", 0))
    an = cfg["analysis"]
    t2, theta = an["t2"], an["theta_gamma"]
    ns = S.shape[0]

    adj = tr.conflict_matrix(S)
    ally = tr.ally_matrix(S)
    gamma = tr.generators(S)

    # Delta: maximal conflict-free clique (m(E) = 0 < t1)
    use_exact = (ns <= 22) if exact is None else exact
    delta = _exact_mis(adj, ally) if use_exact else _greedy_mis(adj, ally, rng)

    mu_g = dg.mu_gamma(gamma, ns)
    in_delta = set(delta)
    region = ["delta" if i in in_delta else ("gamma" if mu_g[i] > theta else "psi")
              for i in range(ns)]
    psi = [i for i in range(ns) if region[i] == "psi"]

    mu_d = dg.mu_delta(ally, delta)
    mu_p = dg.mu_psi(S, psi)
    return Coalitions(delta, gamma, psi, mu_d, mu_g, mu_p, adj, ally, region,
                      _cliques(adj, t2))
