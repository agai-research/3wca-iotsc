"""Human-readable rendering of a 3WCA-IoTSC run. Author: F. Ghedass."""
from __future__ import annotations


def render(sp, co, wc, res, cfg) -> str:
    n = lambda i: sp.sname(i)
    L = []
    L.append("=" * 68)
    L.append("3WCA-IoTSC  -  conflict-aware IoT service composition")
    L.append("=" * 68)
    L.append(f"ICPS space          : |S|={sp.ns}  |R|={sp.nr}  |F|={len(sp.features)}")
    an = cfg["analysis"]
    L.append(f"parameters          : t1={an['t1']}  t2={an['t2']}  "
             f"theta_G={an['theta_gamma']}  w={an['w']}")
    L.append("")
    L.append(f"W_c (candidates)    : {len(wc)} services")
    if len(wc) <= 20:
        L.append("                      " + ", ".join(n(i) for i in wc))
    L.append(f"Delta (max coalition): |{len(co.delta)}| "
             + (", ".join(n(i) for i in co.delta) if len(co.delta) <= 20 else ""))
    L.append(f"Gamma (min conflict) : |{len(co.gamma)}| generators")
    if len(co.gamma) <= 20:
        for a, b, r in co.gamma:
            L.append(f"                      ({n(a)}, {n(b)}, {sp.rname(r)})")
    L.append(f"psi (neutral)        : |{len(co.psi)}| "
             + (", ".join(n(i) for i in co.psi) if len(co.psi) <= 20 else ""))
    L.append("")
    if sp.ns <= 20:
        L.append(f"{'service':10}{'mu_D':>8}{'mu_G':>8}{'mu_psi':>8}{'score':>9}  region")
        from .degrees import score_service
        sc = score_service(co.mu_d, co.mu_g, co.mu_p, an["w"])
        for i in range(sp.ns):
            L.append(f"{n(i):10}{co.mu_d[i]:8.3f}{co.mu_g[i]:8.3f}"
                     f"{co.mu_p[i]:8.3f}{sc[i]:9.3f}  {co.region[i]}")
        L.append("")
    L.append("selection trace:")
    L.extend("  " + t for t in res.trace)
    L.append("")
    L.append("C_IoT               : " + ", ".join(n(i) for i in res.services))
    L.append("resources assigned  : " + ", ".join(sp.rname(j) for j in res.resources))
    L.append(f"conflict-free       : {res.conflict_free}")
    L.append(f"Sev(C_IoT)          : {res.severity:.4f}")
    L.append(f"score(C_IoT)        : {res.score:.4f}")
    L.append("=" * 68)
    return "\n".join(L)
