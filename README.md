# 3WCA-IoTSC

Prototype implementation of **three-way conflict analysis for conflict-aware IoT
service composition**, with application in
Smart Education Environments"*.

The approach models the stances of ICPS service providers towards the IoT
resources they share as a three-valued Pawlak situation table, derives a feature
lattice, a resource lattice and a conflict lattice from it, trisects the IoT services
into a maximum coalition $Delta$, a minimum conflict set `Gamma` and a neutral
set `psi`, and uses those sets to assemble the best non-conflicting composition
of IoT services and resources for a requested abstract workflow.

**Author:** F. Ghedass · **License:** MIT · see `CITATION.cff`.

---

## 1. Repository map

| Path | Contents | Paper reference |
|---|---|---|
| `src/model.py` | ICPS entities, situation table `K^c` | Defs. 5.1-5.3 |
| `src/context.py` | Formal contexts `K^r`, `K^f`, `K^c` | Defs. 5.1-5.3 |
| `src/lattice.py` | Lattice construction, concept location | Def. 5.4, Alg. 2 line 13 |
| `src/trisect.py` | `S_r^-/0/+`, `S_R^*`, `phi_r`, generators, `m(E)` | Sec. 5.2, Table 6, Eq. 2 |
| `src/degrees.py` | `mu_Delta`, `mu_Gamma`, `mu_psi`, `Sev`, `score` | Eqs. 1, 3-5, 7, 8 |
| `src/analysis.py` | **Algorithm 1** - coalitions `Delta`, `Gamma`, `psi` | Sec. 5.2 |
| `src/filter.py` | **Algorithm 2** - resource- and QoS-aware filtering | Sec. 6.1 |
| `src/compose.py` | **Algorithm 3** - consensus composition | Sec. 6.2 |
| `src/engine.py` | The pipeline of Fig. 4 | Sec. 6 |
| `baselines/tqosc.py` | Baseline 1, combinatorial-auction QoS composition | Sec. 8 |
| `baselines/iotsc_fca.py` | Baseline 2, our approach **without** conflict knowledge | ablation |
| `baselines/bsc_cpso.py` | Baseline 3, RCA + Composite PSO | Gharbi & Mezni |
| `Data/gen_data.py` | Dataset and smart-classroom fixture | Sec. 6.4, Sec. 8.1 |
| `Data/gen_inst.py` | Per-experiment instances | Sec. 8 |
| `experiments/` | The six experiments, metrics, harness, tables, stats | Secs. 8.2-8.7 |
| `figures/` | Figures 9-13 | Sec. 8 |
| `Test/first_test.py` | Golden regression test on the running example | Sec. 6.4 |

## 2. Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Python 3.9 or later. Section 8 of the paper names `concepts` and `ray`; this
implementation ships its own pruned (iceberg) lattice builder instead, for the
complexity reason recorded in adjustment A10, so neither library is imported and
neither is needed to reproduce any result. Both are listed, commented out, at the
bottom of `requirements.txt`.

## 3. Quick start

```bash
python Data/gen_data.py                 # main dataset + classroom fixture
python lattices.py --name main          # formal contexts and lattices
python 3WCA-IoTSC.py                    # run the prototype on the running example
python -m pytest Test/ -q               # 17 unit tests
python Test/first_test.py               # 62 golden assertions
python main-exp.py                      # all six experiments
python experiments/tables.py            # Tables 16-21 (CSV + LaTeX)
python figures/make_figs.py             # Figures 9-13 (PNG + PDF)
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

| Key | Symbol | Default | Range (Table 15) |
|---|---|---|---|
| `dataset.n_services` | `\|S\|` | 1000 | 100-2000 |
| `dataset.n_resources` | `\|R\|` | 500 | 50-500 |
| `dataset.n_features` | `\|F\|` | 20 | 10-30 |
| `dataset.density` | `sigma` | 0.20 | 0.10-0.50 |
| `dataset.popularity_alpha` | - | 0.3 | Zipf skew of device popularity (A15) |
| `analysis.t1` | `t_1` | 0.10 | 0.1-0.4 |
| `analysis.t2` | `t_2` | 0.60 | 0.6-0.9 |
| `analysis.theta_gamma` | `theta_Gamma` | 0.50 | 0.1-0.5 |
| `analysis.w` | `w_1,w_2,w_3` | [0.5, 0.3, 0.2] | fixed |
| `query.n_tasks` | `\|W_u\|` | 10 | 5-50 |
| `lattice.min_support`, `lattice.cap` | - | 1, 1200 | iceberg pruning (A10) |
| `run.n_runs`, `run.n_queries` | - | 30, 20 | statistics |

## 5. Experiments

| Script | Sweep | Table | Figure |
|---|---|---|---|
| `exp1_density.py` | `sigma` 10-50% | 16 | - |
| `exp2_scale.py` | 200-2000 entities | 17 | 10 |
| `exp3_workflow.py` | `\|W_u\|` 5-50 | 18 | 9, 11 |
| `exp4_thresh.py` | four `(t_1,t_2)` pairs | 19 | 12, 13 |
| `exp5_distrib.py` | five tripartite profiles | 20 | - |
| `exp6_missing.py` | 10-40% erased | 21 | - |

`exp4` covers **3WCA-IoTSC only**: `t_1` and `t_2` are parameters of Algorithm 1,
and the baselines have no coalition thresholds - exactly as Table 19 reports our
approach alone. All other experiments run all four methods.

Repetitions: 30 runs x 20 queries, except `exp2` (10 x 10) and `exp3` (15 x 10),
whose larger instances cost more; both are set in their config files. Every cell
is reported as mean ± std, with 95% CI in the aggregates.

### Additional comparison figures

`python figures/make_extra_figs.py` produces seven further figures in
`results/figs/extra/`, using plot models that the paper does not employ:

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
which is not one of the six experiments of the paper.

## 6. Methods compared

`3WCA-IoTSC`, `IoTSC-FCA`, `BSC-RCA-CPSO`, `TQoSC`. **The approach cited as
FFCA-IoTSC in the manuscript is implemented and reported here as
BSC-RCA-CPSO**; the manuscript's rows should be renamed accordingly.

## 7. Dataset

See [`docs/dataset-card.md`](docs/dataset-card.md) for entity counts and the
provenance of every field. The Yelp, CASAS and CIC-IoT-2022 corpora are not
reachable from the build environment, so the dataset is **synthetic**, generated
by the augmentation recipe of Section 8.1 and deterministic given `seed`.

## 8. Results integrity

No result is hardcoded. Every figure and every table is produced by loading
`results/agg/*.json`, which is written by actually running the four methods.
Divergences from the values printed in the paper are reported, cell by cell, in
[`docs/reconciliation.md`](docs/reconciliation.md) and
[`docs/reconciliation_auto.md`](docs/reconciliation_auto.md) - including one
case where the expected ordering among the baselines did not emerge, which is
reported as measured rather than adjusted.

Deviations from the paper's specification are listed in
[`docs/adjustments.md`](docs/adjustments.md).

## 9. Notebooks

`notebooks/` holds Colab notebooks: setup, prototype demo, dataset report, all
experiments, one per baseline, and the significance analysis. Each starts with an
install cell, uses relative paths only, and exposes a `QUICK` switch.
