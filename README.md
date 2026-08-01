# 3WCA-IoTSC

Prototype implementation of **three-way conflict analysis for conflict-aware IoT
service composition**, with an application to smart education environments.

The approach models the stances of ICPS service providers towards the IoT
resources they share as a three-valued Pawlak situation table, derives a feature
lattice, a resource lattice and a conflict lattice from it, trisects the IoT
services into a maximum coalition `Delta`, a minimum conflict set `Gamma` and a
neutral set `psi`, and uses those sets to assemble the best non-conflicting
composition of IoT services and resources for a requested abstract workflow.

---

## 1. Repository map

| Path | Contents |
|---|---|
| `src/model.py` | ICPS entities and the situation table `K^c` |
| `src/context.py` | Formal contexts `K^r`, `K^f`, `K^c` |
| `src/lattice.py` | Lattice construction and concept location |
| `src/trisect.py` | Trisections `S_r^-/0/+` and `S_R^*`, the function `phi_r`, conflict generators, conflict measure `m(E)` |
| `src/degrees.py` | Coalition, conflict and neutrality degrees `mu_Delta`, `mu_Gamma`, `mu_psi`; severity `Sev`; composition score |
| `src/analysis.py` | Coalition computation: builds `Delta`, `Gamma`, `psi` |
| `src/filter.py` | Resource- and QoS-aware filtering of the candidate services |
| `src/compose.py` | Consensus-based conflict-aware composition |
| `src/engine.py` | End-to-end pipeline tying the stages together |
| `baselines/tqosc.py` | Baseline 1, combinatorial-auction QoS composition |
| `baselines/iotsc_fca.py` | Baseline 2, the approach **without** conflict knowledge (ablation) |
| `baselines/bsc_cpso.py` | Baseline 3, Relational Concept Analysis + Composite PSO |
| `Data/gen_data.py` | Dataset generator and the smart-classroom fixture |
| `Data/gen_inst.py` | Per-experiment instances derived from the main dataset |
| `experiments/` | The six experiments, metrics, harness, result tables, statistics |
| `Test/first_test.py` | Golden regression test on the smart-classroom example |

## 2. Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Python 3.9 or later. The implementation ships its own pruned (iceberg) lattice
builder, so the `concepts` and `ray` libraries are neither imported nor needed to
reproduce any result. Both are listed, commented out, at the bottom of
`requirements.txt`.

## 3. Quick start

```bash
python Data/gen_data.py                 # main dataset + classroom fixture
python lattices.py --name main          # formal contexts and lattices
python 3WCA-IoTSC.py                    # run the prototype on the classroom example
python -m pytest Test/ -q               # 20 unit tests
python Test/first_test.py               # 62 golden assertions
python main-exp.py                      # all six experiments
python experiments/tables.py            # result tables (CSV + LaTeX)
python experiments/stats.py             # Wilcoxon tests
```

`python 3WCA-IoTSC.py` prints the full trace of the smart-classroom scenario and
ends with:

```
C_IoT               : LS, QG, RM, SL, PC
conflict-free       : True
Sev(C_IoT)          : 0.1156
```

## 4. Configuration

Everything lives in `config/default.yaml`; per-experiment files overlay it and
CLI flags overlay those. No parameter is hardcoded in `src/`.

| Key | Symbol | Default | Range |
|---|---|---|---|
| `dataset.n_services` | `\|S\|` | 1000 | 100-2000 |
| `dataset.n_resources` | `\|R\|` | 500 | 50-500 |
| `dataset.n_features` | `\|F\|` | 20 | 10-30 |
| `dataset.density` | `sigma` | 0.20 | 0.10-0.50 |
| `dataset.popularity_alpha` | `alpha` | 0.3 | Zipf skew of device popularity |
| `analysis.t1` | `t_1` | 0.10 | 0.1-0.4 |
| `analysis.t2` | `t_2` | 0.60 | 0.6-0.9 |
| `analysis.theta_gamma` | `theta_Gamma` | 0.50 | 0.1-0.5 |
| `analysis.w` | `w_1,w_2,w_3` | [0.5, 0.3, 0.2] | fixed |
| `query.n_tasks` | `\|W_u\|` | 10 | 5-50 |
| `lattice.min_support`, `lattice.cap` | - | 1, 1200 | iceberg pruning |
| `run.n_runs`, `run.n_queries` | - | 30, 20 | statistics |

## 5. Methods compared

`3WCA-IoTSC`, `IoTSC-FCA`, `BSC-RCA-CPSO`, `TQoSC`. `BSC-RCA-CPSO` denotes the
approach combining Relational Concept Analysis with Composite Particle Swarm
Optimisation.
