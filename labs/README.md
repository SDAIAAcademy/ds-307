# Metrics, Semantic Models and Dashboards: labs

## Quick start

- Google Colab: open a notebook from the course page; its first cell clones this repository.
- Locally: clone the repository, then open the notebooks in `labs/` with Jupyter.

| Unit | Session | Notebook |
|---|---|---|
| Day 1 | Session 1 · Why three reports disagree | [`D1_1_trace_three_time.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D1_1_trace_three_time.ipynb) |
| Day 1 | Session 2 · Anatomy of a metric definition | [`D1_2_define_four_ridership.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D1_2_define_four_ridership.ipynb) |
| Day 1 | Session 3 · Ratios, distinct counts and time logic | [`D1_3_implement_two_ratio.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D1_3_implement_two_ratio.ipynb) |
| Day 1 | Session 4 · Metric trees | [`D1_4_build_metric_tree.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D1_4_build_metric_tree.ipynb) |
| Day 2 | Session 1 · Star schemas for analysis | [`D2_1_model_trips_boardings.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D2_1_model_trips_boardings.ipynb) |
| Day 2 | Session 2 · Changing dimensions and calendars | [`D2_2_query_re_routed.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D2_2_query_re_routed.ipynb) |
| Day 2 | Session 3 · Fan-out and join paths | [`D2_3_find_double_counting.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D2_3_find_double_counting.ipynb) |
| Day 2 | Session 4 · Metrics in an open specification | [`D2_4_express_five_catalogue.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D2_4_express_five_catalogue.ipynb) |
| Day 3 | Session 1 · Dashboards start from a decision | [`D3_1_wireframe_operations_director.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D3_1_wireframe_operations_director.ipynb) |
| Day 3 | Session 2 · Comparisons and bilingual layout | [`D3_2_build_three_panels.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D3_2_build_three_panels.ipynb) |
| Day 3 | Session 3 · Load time is a design constraint | [`D3_3_bring_slow_dashboard.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D3_3_bring_slow_dashboard.ipynb) |
| Day 3 | Session 4 · Investigating an anomaly | [`D3_4_drill_into_seeded.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D3_4_drill_into_seeded.ipynb) |
| Day 4 | Session 1 · From question to query | [`D4_1_run_agent_ten.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D4_1_run_agent_ten.ipynb) |
| Day 4 | Session 2 · Certified questions | [`D4_2_write_certified_answers.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D4_2_write_certified_answers.ipynb) |
| Day 4 | Session 3 · With and without the semantic layer | [`D4_3_score_batch_run.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D4_3_score_batch_run.ipynb) |
| Day 4 | Session 4 · What the agent may answer | [`D4_4_draft_go_or.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-307/blob/main/labs/D4_4_draft_go_or.ipynb) |

The notebooks are generated from the percent-format sources in `labs/_src/` by `labs/_tools/py2nb.py` (`uv run python _tools/py2nb.py` from `labs/`), which also writes the solutions to `labs/solutions/`. Edit the sources, not the notebooks.
