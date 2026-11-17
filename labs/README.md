# Metrics, Semantic Models and Dashboards: labs

Hands-on notebooks for the SDAIA Academy course **DS-307 Metrics, Semantic Models and Dashboards**. Every lab answers
a question of **Wadi Noor Transit (نقل وادي نور)**, a fictional city bus operator with twelve routes from three
depots. Each lab starts from a supplied reference state, so none depends on an earlier one, and each has a solution
in `solutions/`.

A laptop CPU or a Colab CPU runtime is enough. No model is downloaded. Day 4 uses a free hosted model on OpenRouter
when you have a key, and a scripted stand-in when you do not (see "The agent and the model key" below).

## Quick start

**Google Colab**
1. Open a notebook from the [course page](https://sdaiaacademy.github.io/ds-307/), or directly:
   `https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/<notebook>.ipynb`.
2. Run the first cell. It clones this repository and installs `requirements-colab.txt`.

**Local**
```bash
git clone https://github.com/SDAIAAcademy/ds-307
cd ds-307/labs
uv sync                        # creates the environment from pyproject.toml (uv.lock pins every version)
uv run jupyter lab
```

Before Day 1, do the pre-work,
[`00_prework.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/00_prework.ipynb)
(five warm-up queries and an entry quiz), then run
[`00_setup_check.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/00_setup_check.ipynb)
(packages, data, the semantic model, speed and the optional key).

**Quick mode.** `WNT_QUICK=1` makes the timing lab (3.3) time one week of tiles instead of four. Every answer the
labs check stays the same.

## Notebooks

| Unit | Session | Notebook |
|---|---|---|
| Day 1 | Session 1 · Why three reports disagree | [`D1_1_three_on_time.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D1_1_three_on_time.ipynb) |
| Day 1 | Session 2 · Anatomy of a metric definition | [`D1_2_ridership_metrics.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D1_2_ridership_metrics.ipynb) |
| Day 1 | Session 3 · Ratios, distinct counts and time logic | [`D1_3_ratio_metrics.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D1_3_ratio_metrics.ipynb) |
| Day 1 | Session 4 · Metric trees | [`D1_4_metric_tree.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D1_4_metric_tree.ipynb) |
| Day 2 | Session 1 · Star schemas for analysis | [`D2_1_star_schema.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D2_1_star_schema.ipynb) |
| Day 2 | Session 2 · Changing dimensions and calendars | [`D2_2_route_history.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D2_2_route_history.ipynb) |
| Day 2 | Session 3 · Fan-out and join paths | [`D2_3_fan_out.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D2_3_fan_out.ipynb) |
| Day 2 | Session 4 · Metrics in an open specification | [`D2_4_semantic_layer.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D2_4_semantic_layer.ipynb) |
| Day 3 | Session 1 · Dashboards start from a decision | [`D3_1_wireframe.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D3_1_wireframe.ipynb) |
| Day 3 | Session 2 · Comparisons and bilingual layout | [`D3_2_bilingual_panels.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D3_2_bilingual_panels.ipynb) |
| Day 3 | Session 3 · Load time is a design constraint | [`D3_3_load_time.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D3_3_load_time.ipynb) |
| Day 3 | Session 4 · Investigating an anomaly | [`D3_4_ridership_drop.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D3_4_ridership_drop.ipynb) |
| Day 4 | Session 1 · From question to query | [`D4_1_agent_raw.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D4_1_agent_raw.ipynb) |
| Day 4 | Session 2 · Certified questions | [`D4_2_certified_answers.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D4_2_certified_answers.ipynb) |
| Day 4 | Session 3 · With and without the semantic layer | [`D4_3_score_configs.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D4_3_score_configs.ipynb) |
| Day 4 | Session 4 · What the agent may answer | [`D4_4_go_no_go.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D4_4_go_no_go.ipynb) |

The notebooks are generated from the percent-format sources in `_src/` by `_tools/py2nb.py`
(`uv run python _tools/py2nb.py` from `labs/`), which also writes the solutions to `solutions/`. Edit the sources,
not the notebooks. Each exercise is a function; until it is written, the cell after it uses the reference result, so
the notebook always runs to its last cell. Each source also runs as a script: `uv run python _src/D2_4_semantic_layer.py`.

Every lab writes its outputs under `artifacts/<lab>/`, so the shared data in `data/` never changes. Delete
`artifacts/` before running the course's `academy check`, which reports files it does not know under `labs/`.

## The agent and the model key

Day 4 tests **Nabih**, a conversational analytics agent (`wnt_agent.py`), in two configurations: writing SQL against
the raw warehouse, and asking the semantic layer for governed metrics.

- **Live.** With `OPENROUTER_API_KEY` in `labs/.env` (copy `.env.example`), or in Colab's Secrets panel, each question
  goes to a free hosted model (`google/gemma-4-31b-it:free` by default; set `WNT_MODEL` for another free one, such as
  `nvidia/nemotron-3.5-lightning:free`). The query the model writes runs on your machine. Free models are
  rate-limited: allow a minute for ten questions.
- **Stand-in.** Without a key, or when OpenRouter refuses the key, a **scripted stand-in** replays the query written
  for each certified question in `data/agent/stand_in.yaml`. Those queries were written to resemble the errors
  text-to-SQL agents make; they are not a recording of a model. They run for real, so every value is reproducible.
  Set `WNT_STAND_IN=1` to force the stand-in when you have a key.

Every answer records its mode and model in the lab's log, so a result never hides how it was produced. The batch run
of Lab 4.3 (`data/agent/batch_run.csv`) was produced with the stand-in; `rerun_live()` in that lab produces your own.

## The case study: Wadi Noor Transit

Synthetic and deterministic (`prepare_data.py`, seed 307), covering 1 January to 31 October 2026; no real operator,
route, rider, card or phone number.

| Data | Folder | Contents |
|---|---|---|
| Warehouse | `data/warehouse/` | eleven Parquet tables: trips, timepoints, card taps, complaints, pass sales and their dimensions |
| Reports | `data/reports/` | the three September on-time reports that disagree (Lab 1.1) |
| Catalogue | `data/catalogue/` | the twelve business questions, the data dictionary and the governed metric catalogue |
| Semantic model | `data/semantic/` | the Apache Ossie model, its starter, the 25 test queries, the Ossie JSON Schema (Apache-2.0, see `NOTICE.md`) |
| Dashboard brief | `data/dashboard/` | the operations director's brief (Day 3) |
| Agent | `data/agent/` | the 40 certified questions, the stand-in, the batch run and the scoring table (Day 4) |
| Reference states | `data/reference/` | the results each lab checks against and starts from |

## Helpers

| File | What it is |
|---|---|
| `wnt.py` | paths, `db()` (a DuckDB connection with the warehouse as views), `check`, `reference`, `lab_dir`, `timed`, `lint` |
| `wnt_semantic.py` | the course's Ossie compiler: validates a model, compiles metric requests to SQL, refuses fan-out joins and Restricted fields |
| `wnt_dash.py` | the brief checker, small-count suppression and the bilingual Altair panels (Day 3) |
| `wnt_agent.py` | Nabih (live or stand-in), the scorer, the Wilson interval and the memo checklist (Day 4) |
| `prepare_data.py` | regenerates the warehouse (`uv run python prepare_data.py`) |
| `_tools/make_reference.py` | rewrites `data/reference/`, the test queries, the certified questions and the batch run (`day1` … `day4`, `capstone`) |

The semantic layer of the course is a small compiler written for teaching, so that every step of it can be read.
MetricFlow and Cube Core read the same ideas; the Apache Ossie format is the interchange between them.

## The capstone

The brief, the starter model and the rubric are in [`capstone/`](capstone/README.md). The follow-up task after the
course is in [`followup/`](followup/README.md).

## Windows

- **Long folder paths.** If an install or an import fails with "The filename or extension is too long", run
  `git config core.longpaths true` and keep the environment in a short folder: set `UV_PROJECT_ENVIRONMENT` to a
  short path (for example a folder at the root of your drive) before `uv sync`.
- **Arabic in a terminal.** A script run in a Windows console may fail to print Arabic (`UnicodeEncodeError`): set
  `PYTHONUTF8=1` first. Notebooks are not affected.
