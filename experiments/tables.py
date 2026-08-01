"""Rebuild Tables 16 to 21 from results/agg/, as CSV and as LaTeX fragments.

Row order is 3WCA-IoTSC, IoTSC-FCA, BSC-RCA-CPSO, TQoSC. The paper's
FFCA-IoTSC rows correspond to BSC-RCA-CPSO. Every cell carries mean +- std.
Author: F. Ghedass.
"""
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import AGG, TABLES        # noqa: E402

M = ["3WCA-IoTSC", "IoTSC-FCA", "BSC-RCA-CPSO", "TQoSC"]


def _c(d, key, scale=1.0, nd=2):
    if key not in d:
        return "---"
    return f"{d[key]['mean'] * scale:.{nd}f} $\\pm$ {d[key]['std'] * scale:.{nd}f}"


def _plain(d, key, scale=1.0, nd=3):
    return "---" if key not in d else f"{d[key]['mean'] * scale:.{nd}f}+-{d[key]['std'] * scale:.{nd}f}"


def emit(name: str, header: list, rows: list) -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    with open(TABLES / f"{name}.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    body = "\n".join(" & ".join(str(c) for c in r) + r" \\" for r in rows)
    tex = ("\\begin{tabular}{@{}" + "l" * 2 + "c" * (len(header) - 2) + "@{}}\n\\toprule\n"
           + " & ".join(f"\\textbf{{{h}}}" for h in header) + r" \\ \midrule" + "\n"
           + body + "\n\\bottomrule\n\\end{tabular}\n")
    (TABLES / f"{name}.tex").write_text(tex)
    print(f"  {name}: {len(rows)} rows")


def t16():
    a = json.load(open(AGG / "exp1_density.json"))
    rows = []
    for m in M:
        for p in [10, 20, 30, 40, 50]:
            d = a[str(p)][m]
            rows.append([m, p, _c(d, "success", 100, 1), _c(d, "conflict_free", 100, 1),
                         _c(d, "bound_ratio", 100, 1), _c(d, "severity", 1, 3),
                         _c(d, "time_ms", 1, 2), _c(d, "n_conflicts", 1, 2),
                         _c(d, "resources_used", 1, 1), _c(d, "services_used", 1, 1),
                         _c(d, "score", 1, 3)])
    emit("tab16_density", ["Method", "Density (%)", "Success rate (%)",
                           "Conflict-free (%)", "Tasks bound (%)", "Severity",
                           "Time (ms)", "#Conflicts", "Resources used",
                           "Services used", "Score"], rows)


def t17():
    a = json.load(open(AGG / "exp2_scale.json"))
    rows = []
    for m in M:
        for p in [200, 500, 1000, 1500, 2000]:
            d, aux = a[str(p)][m], a[str(p)]["_aux"]
            sets = ([f"{aux['delta']:.0f}", f"{aux['gamma']:.0f}", f"{aux['psi']:.0f}"]
                    if m == "3WCA-IoTSC" else ["---", "---", "---"])
            rows.append([m, p, _c(d, "time_ms", 1e-3, 3), _c(d, "memory_mb", 1, 1),
                         _c(d, "success", 100, 1)] + sets)
    emit("tab17_scalability", ["Method", "Space Size", "Time (s)", "Memory (MB)",
                               "Success Rate (%)", "Coalition |D|", "Conflict |G|",
                               "Neutral |psi|"], rows)


def t18():
    a = json.load(open(AGG / "exp3_workflow.json"))
    rows = []
    for m in M:
        for p in [5, 10, 20, 30, 50]:
            d = a[str(p)][m]
            rows.append([m, p, _c(d, "score", 1, 3), _c(d, "severity", 1, 3),
                         _c(d, "time_ms", 1, 2), _c(d, "resources_used", 1, 1),
                         _c(d, "services_used", 1, 1)])
    emit("tab18_workflow", ["Method", "Tasks", "Score", "Sev.", "Time (ms)",
                            "Res. used", "Serv. used"], rows)


def t19():
    a = json.load(open(AGG / "exp4_thresh.json"))
    rows = []
    for t in [(0.1, 0.9), (0.2, 0.8), (0.3, 0.7), (0.4, 0.6)]:
        d, aux = a[str(t)]["3WCA-IoTSC"], a[str(t)]["_aux"]
        rows.append([f"({t[0]}, {t[1]})", f"{aux['delta']:.0f}", f"{aux['gamma']:.0f}",
                     f"{aux['psi']:.0f}", _c(d, "success", 100, 1),
                     _c(d, "time_ms", 1, 2), _c(d, "severity", 1, 4)])
    emit("tab19_thresholds", ["(t1, t2)", "|Delta|", "|Gamma|", "|psi|",
                              "Succ. (%)", "Time (ms)", "Sev(C_IoT)"], rows)


def t20():
    a = json.load(open(AGG / "exp5_distrib.json"))
    prof = ["High-Alliance", "Balanced", "High-Neutral", "High-Conflict", "Realistic"]
    rows = []
    for m in M:
        for p in prof:
            d = a[p][m]
            rows.append([m, p, _c(d, "success", 100, 1), _c(d, "severity", 1, 3),
                         _c(d, "allied_usage", 1, 1), _c(d, "neutral_usage", 1, 1),
                         _c(d, "conflict_avoidance", 1, 1), _c(d, "time_ms", 1, 2)])
    emit("tab20_distribution", ["Method", "Distribution Profile", "Success rate (%)",
                                "Severity", "Allied usage (%)", "Neutral usage (%)",
                                "Conflict avoidance (%)", "Execution time (ms)"], rows)


def t21():
    a = json.load(open(AGG / "exp6_missing.json"))
    rows = []
    for m in M:
        base = a["0"][m]["success"]["mean"]
        for p in [10, 20, 30, 40]:
            d, aux = a[str(p)][m], a[str(p)]["_aux"]
            degr = 100.0 * (base - d["success"]["mean"]) / max(base, 1e-9)
            fa = f"{aux['false_allies']:.2f}" if m == "3WCA-IoTSC" else "---"
            fc = f"{aux['false_conflicts']:.2f}" if m == "3WCA-IoTSC" else "---"
            rows.append([m, p, _c(d, "success", 100, 1), f"{degr:.1f}",
                         _c(d, "severity", 1, 3), fa, fc, _c(d, "time_ms", 1, 2)])
    emit("tab21_completeness", ["Method", "Missing Data (%)", "Success Rate (%)",
                                "Degradation (%)", "Severity", "False allies (%)",
                                "False conflicts (%)", "Execution time (ms)"], rows)


def main():
    print("rebuilding result tables:")
    for f in (t16, t17, t18, t19, t20, t21):
        f()


if __name__ == "__main__":
    main()
