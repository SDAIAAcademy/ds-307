<!-- academy:title -->
# Metrics, Semantic Models and Dashboards

المقاييس والنماذج الدلالية ولوحات المعلومات

Data Science Track · SDAIA Academy · DS-307 · Level 300

REPLACE: one line under the title: what participants can do after the course

Participants take over performance reporting for Wadi Noor Transit, a fictional bus operator whose three reports give three different on-time figures. On a synthetic warehouse of trips, boardings and routes they write governed metric definitions, build a semantic model that defines each metric once, design a dashboard for one decision within a load-time budget, trace an anomaly to its source, and test a conversational analytics agent on certified questions with and without the semantic layer. Platform-scale semantic layer design is DS-408.

**Format:** Intensive: 4 teaching days of four sessions and a capstone day, with guided pre-work and a tracked follow-up task

**Course page:** https://sdaiaacademy.github.io/ds-307/
<!-- /academy:title -->

## Outcomes

| | Outcomes | Level | Evidence |
|---|---|---|---|
| LO1 | Explain why reports built on one warehouse disagree on the same measure, given three operator reports with different on-time figures | Awareness | a diagnosis naming the definitional cause of each difference |
| LO2 | Draft metric definitions stating formula, grain, filters, time logic, owner and limits, given twelve business questions and the data dictionary | Applied | a metric catalogue that passes a peer checklist and reconciles to source totals |
| LO3 | Implement a star-schema semantic model with a slowly changing route dimension and each metric defined once, given the synthetic transit warehouse | Applied | reference values returned for 25 test queries |
| LO4 | Analyse a metric anomaly by drill-down and segmentation to find its source, given a seeded drop in weekly ridership | Applied | an anomaly note naming the cause, affected segments and correction |
| LO5 | Design a dashboard for a named audience and decision within a load-time budget, given the operations director's brief and a three-second budget | Performance | a dashboard, a one-page rationale and recorded timings, scored on a rubric |
| LO6 | Evaluate a conversational analytics agent against governed metrics and decide which question types it may answer unreviewed, given 40 certified questions and a stated tolerance for wrong figures | Performance | a memo with accuracy by question type and configuration, plausible wrong answers and a go or no-go decision |

<!-- academy:units -->
## Units

| Unit | Title | Sessions | Slides |
|---|---|---|---|
| Day 1 | Define the numbers | Why three reports disagree; Anatomy of a metric definition; Ratios, distinct counts and time logic; Metric trees | [`slides/day1.html`](slides/day1.html) |
| Day 2 | Model once | Star schemas for analysis; Changing dimensions and calendars; Fan-out and join paths; Metrics in an open specification | [`slides/day2.html`](slides/day2.html) |
| Day 3 | Show and investigate | Dashboards start from a decision; Comparisons and bilingual layout; Load time is a design constraint; Investigating an anomaly | [`slides/day3.html`](slides/day3.html) |
| Day 4 | Let an agent answer | From question to query; Certified questions; With and without the semantic layer; What the agent may answer | [`slides/day4.html`](slides/day4.html) |
| Capstone | Capstone project presentations |  | [`slides/capstone.html`](slides/capstone.html) |
<!-- /academy:units -->

## Case study

**REPLACE: the name of the fictional organisation every lab works on.** REPLACE: two sentences on the case study and its synthetic data

<!-- academy:labs -->
## Labs

Every lab is a notebook in `labs/`. Open it in Google Colab from the course page, or run it locally with `uv`. Exercises raise `NotImplementedError` until they are done; the reference versions are in `labs/solutions/`.

| | Session | Lab | File |
|---|---|---|---|
| 1.1 | Day 1 · Session 1 | Trace three on-time figures to their definitions (AI-off) | [`D1_1_trace_three_time.ipynb`](labs/D1_1_trace_three_time.ipynb) |
| 1.2 | Day 1 · Session 2 | Define four ridership metrics with grain, filters and owner | [`D1_2_define_four_ridership.ipynb`](labs/D1_2_define_four_ridership.ipynb) |
| 1.3 | Day 1 · Session 3 | Implement two ratio metrics and test them against hand-computed values | [`D1_3_implement_two_ratio.ipynb`](labs/D1_3_implement_two_ratio.ipynb) |
| 1.4 | Day 1 · Session 4 | Build a metric tree from the network goal to three drivers and a guardrail | [`D1_4_build_metric_tree.ipynb`](labs/D1_4_build_metric_tree.ipynb) |
| 2.1 | Day 2 · Session 1 | Model trips and boardings as facts and dimensions and check each grain | [`D2_1_model_trips_boardings.ipynb`](labs/D2_1_model_trips_boardings.ipynb) |
| 2.2 | Day 2 · Session 2 | Query a re-routed line through a type 2 route dimension and a dual-calendar date table | [`D2_2_query_re_routed.ipynb`](labs/D2_2_query_re_routed.ipynb) |
| 2.3 | Day 2 · Session 3 | Find a double-counting join and fix it with a reconciliation test | [`D2_3_find_double_counting.ipynb`](labs/D2_3_find_double_counting.ipynb) |
| 2.4 | Day 2 · Session 4 | Express five catalogue metrics in the semantic layer and run the test queries | [`D2_4_express_five_catalogue.ipynb`](labs/D2_4_express_five_catalogue.ipynb) |
| 3.1 | Day 3 · Session 1 | Wireframe the operations director's dashboard from the brief | [`D3_1_wireframe_operations_director.ipynb`](labs/D3_1_wireframe_operations_director.ipynb) |
| 3.2 | Day 3 · Session 2 | Build three panels with targets and prior periods in Arabic and English | [`D3_2_build_three_panels.ipynb`](labs/D3_2_build_three_panels.ipynb) |
| 3.3 | Day 3 · Session 3 | Bring a slow dashboard under three seconds and record timings | [`D3_3_bring_slow_dashboard.ipynb`](labs/D3_3_bring_slow_dashboard.ipynb) |
| 3.4 | Day 3 · Session 4 | Drill into the seeded ridership drop and write the anomaly note | [`D3_4_drill_into_seeded.ipynb`](labs/D3_4_drill_into_seeded.ipynb) |
| 4.1 | Day 4 · Session 1 | Run an agent on ten questions against the raw schema and log its SQL | [`D4_1_run_agent_ten.ipynb`](labs/D4_1_run_agent_ten.ipynb) |
| 4.2 | Day 4 · Session 2 | Write certified answers for ten questions, two of which the agent should refuse | [`D4_2_write_certified_answers.ipynb`](labs/D4_2_write_certified_answers.ipynb) |
| 4.3 | Day 4 · Session 3 | Score batch-run answers to 40 questions in both configurations and classify the errors | [`D4_3_score_batch_run.ipynb`](labs/D4_3_score_batch_run.ipynb) |
| 4.4 | Day 4 · Session 4 | Draft the go or no-go memo from a supplied scoring table | [`D4_4_draft_go_or.ipynb`](labs/D4_4_draft_go_or.ipynb) |
<!-- /academy:labs -->

## Capstone

Catalogue, semantic model, dashboard and agent memo for a second subject area (fares and concessions), in a public repository whose README reports measured query accuracy and load times, defended in a ten-minute review

**Submission:** REPLACE: what participants submit and how: a public repository link, or a shared folder for a course without code

## Prerequisites

- FN-104 SQL and Data Wrangling
- DS-203 Exploratory Analysis and Visualisation
- Writes SQL with joins, grouping and window functions
- Has built a chart-based report for others

<!-- academy:tools -->
## Tools

Each line is a capability; the examples are interchangeable.

- **Analytical SQL engine:** DuckDB, PostgreSQL
- **Semantic layer and metric definitions:** MetricFlow, Cube Core, Apache Ossie (Open Semantic Interchange) files
- **Dashboard tool:** Apache Superset, Metabase, an enterprise BI tool
- **Language model through a chat-completions style endpoint:** a locally served open-weight model, a free hosted open-weight model
<!-- /academy:tools -->

<!-- academy:sources -->
## Sources

- REPLACE: every source the course cites, with its address, in course.json under "sources"; this list is written from there
<!-- /academy:sources -->

### National references

- NDMO Data Management and Personal Data Protection Standards (Business Intelligence and Analytics domain): REPLACE: the address of the official text
- NDMO Data Classification Policy: REPLACE: the address of the official text
- Personal Data Protection Law and its implementing regulations: REPLACE: the address of the official text
- SDAIA Generative AI Guidelines for Government: REPLACE: the address of the official text
