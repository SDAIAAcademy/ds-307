# Metrics, Semantic Models and Dashboards: labs

## Quick start

- Google Colab: open a notebook from the course page; its first cell clones this repository.
- Locally: clone the repository, then open the notebooks in `labs/` with Jupyter.

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

The notebooks are generated from the percent-format sources in `labs/_src/` by `labs/_tools/py2nb.py` (`uv run python _tools/py2nb.py` from `labs/`), which also writes the solutions to `labs/solutions/`. Edit the sources, not the notebooks.
