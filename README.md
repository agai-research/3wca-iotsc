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
python figures/make_figs.py             # figures (PNG + PDF)
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

## 5. Experiments

| Script | Sweep | Outputs |
|---|---|---|
| `exp1_density.py` | conflict density `sigma` 10-50% | result table |
| `exp2_scale.py` | ICPS space size 200-2000 entities | result table + scalability figure |
| `exp3_workflow.py` | workflow size `\|W_u\|` 5-50 | result table + workflow-quality figures |
| `exp4_thresh.py` | four `(t_1,t_2)` pairs | result table + threshold-sensitivity figures |
| `exp5_distrib.py` | five tripartite stance profiles | result table |
| `exp6_missing.py` | 10-40% of stances erased | result table |

`exp4` covers **3WCA-IoTSC only**: `t_1` and `t_2` are parameters of the
coalition analysis, and the baselines have no coalition thresholds. All other
experiments run all four methods.

Repetitions: 30 runs x 20 queries, except `exp2` (10 x 10) and `exp3` (15 x 10),
whose larger instances cost more; both are set in their config files. Every cell
is reported as mean ± std, with 95% CI in the aggregates.

### Additional comparison figures

`python figures/make_extra_figs.py` produces seven further figures in
`results/figs/extra/`, using additional plot models:

| File | Model | Shows |
|---|---|---|
| `figX1_surface3d` | 3D response surfaces | conflict-free rate over the density x workflow grid, one surface per method |
| `figX2_scale3d` | 3D trajectories | scaling path through (space size, time, memory) |
| `figX3_radar` | radar chart | normalised six-metric profile per method |
| `figX4_parallel` | parallel coordinates | all four methods across six metrics and five densities |
| `figX5_heatmap` | annotated heat map | conflict-free rate over all 24 experimental conditions |
| `figX6_pareto` | bubble scatter + Pareto front | cost against robustness, bubble area = resources used |
| `figX7_violin` | violin plot | per-run distributions behind the reported means |

`figX1` is backed by a supplementary cross-sweep, `experiments/exp7_grid.py`,
which is additional to the six main experiments.

## 6. Methods compared

`3WCA-IoTSC`, `IoTSC-FCA`, `BSC-RCA-CPSO`, `TQoSC`. `BSC-RCA-CPSO` denotes the
approach combining Relational Concept Analysis with Composite Particle Swarm
Optimisation.

## 7. Dataset

See [`docs/dataset-card.md`](docs/dataset-card.md) for entity counts and the
provenance of every field. The Yelp, CASAS and CIC-IoT-2022 corpora are not
reachable from the build environment, so the dataset is **synthetic**, generated
by the augmentation recipe documented in the dataset card and deterministic given
`seed`.

## 8. Results integrity

No result is hardcoded. Every figure and every table is produced by loading
`results/agg/*.json`, which is written by actually running the four methods.
What the runs produced is recorded in
[`docs/reconciliation.md`](docs/reconciliation.md) and
[`docs/reconciliation_auto.md`](docs/reconciliation_auto.md), including one case
where an expected ordering among the baselines did not emerge; it is reported as
measured rather than adjusted.

Implementation decisions and deviations from the original specification are
listed in [`docs/adjustments.md`](docs/adjustments.md).

## 9. Notebooks

`notebooks/` holds Colab notebooks: setup, prototype demo, dataset report, all
experiments, one per baseline, and the significance analysis. Each starts with an
install cell, uses relative paths only, and exposes a `QUICK` switch.
