<!-- academy:title -->
# Metrics, Semantic Models and Dashboards

المقاييس والنماذج الدلالية ولوحات المعلومات

Data Science Track · SDAIA Academy · DS-307 · Level 300

Define each number once, model it, show it to the person who decides, and test the agent that answers questions about it

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
| Capstone | Capstone: fares and concessions |  | [`slides/capstone.html`](slides/capstone.html) |
<!-- /academy:units -->

## Case study

**Wadi Noor Transit (نقل وادي نور).** A fictional city bus operator: twelve routes from three depots (North,
Central, East), whose operations, planning and board reports give three different on-time figures for the same
September. The synthetic warehouse in `labs/data/warehouse/` is written by `labs/prepare_data.py` with a fixed seed
and covers 1 January to 31 October 2026: about 85,000 scheduled trips, 329,000 timepoint arrivals, 849,000 card
taps, 2,400 complaints and 121,000 pass sales, with a dual-calendar date table (Gregorian and Umm al-Qura Hijri) and
a route dimension that keeps the history of a re-routed line. No real operator, route, rider or card: every name is
invented. Problems are planted for the labs to find; the trainer's list is in `labs/solutions/answer_key.md`.

People in the case: Mashael Al-Saadi (operations director, who owns the dashboard decision), Tawfiq Al-Sahafi
(control centre), Dhuha Al-Rowais (network planning), Yasmeen Al-Jaafari (strategy and finance), Muneer Al-Thaqafi
(data platform, the warehouse) and Haneen Al-Shamrani (data governance). Nabih (نبيه) is the conversational
analytics agent tested on Day 4. You are the new performance reporting analyst.

## How the course is organised

- **Pre-work** (guided self-study, about two hours): `labs/00_prework.ipynb`, five warm-up queries on the warehouse
  and a short entry quiz on joins, grouping and window functions; then `labs/00_setup_check.ipynb`.
- **Four teaching days** of four sessions. Each session is about 25 minutes of ideas, a checkpoint and a 25-minute
  lab. Every lab starts from supplied data and has a solution in `labs/solutions/`.
- **AI policy.** AI off for the first lab of each day (1.1, 2.1, 3.1, 4.1) and for the supervised check; an
  AI tutor in the other labs, explaining errors without writing definitions; AI allowed in the capstone, with a
  verification note for each AI-drafted definition. On Day 4 the agent is under test, not an aid.
- **Follow-up task** (tracked, after the course): `labs/followup/README.md`. Write three governed definitions and
  ten certified questions for a measure your own team reports, and test one assistant or report against them.

## Assessment

- A supervised AI-off check on definitions, grain and joins (20%).
- The capstone repository, scored on the rubric below (60%).
- A live review in which the assessor picks a figure on your dashboard and you reconcile it to source rows (20%).

Passing needs 70% overall and at least 60% on the capstone rubric. Authenticity rests on the commit history and the
query logs of the capstone repository and on the live trace. The certificate is a completion certificate with assessed
work.

<!-- academy:labs -->
## Labs

Every lab is a notebook in `labs/`. Open it in Google Colab from the course page, or run it locally with `uv`. Exercises raise `NotImplementedError` until they are done; the reference versions are in `labs/solutions/`.

| | Session | Lab | File |
|---|---|---|---|
| 1.1 | Day 1 · Session 1 | Three on-time figures | [`D1_1_three_on_time.ipynb`](labs/D1_1_three_on_time.ipynb) |
| 1.2 | Day 1 · Session 2 | Four ridership definitions | [`D1_2_ridership_metrics.ipynb`](labs/D1_2_ridership_metrics.ipynb) |
| 1.3 | Day 1 · Session 3 | Two ratio metrics, tested | [`D1_3_ratio_metrics.ipynb`](labs/D1_3_ratio_metrics.ipynb) |
| 1.4 | Day 1 · Session 4 | A network metric tree | [`D1_4_metric_tree.ipynb`](labs/D1_4_metric_tree.ipynb) |
| 2.1 | Day 2 · Session 1 | Facts, dimensions and their grain | [`D2_1_star_schema.ipynb`](labs/D2_1_star_schema.ipynb) |
| 2.2 | Day 2 · Session 2 | A re-routed line and two calendars | [`D2_2_route_history.ipynb`](labs/D2_2_route_history.ipynb) |
| 2.3 | Day 2 · Session 3 | The double-counting join | [`D2_3_fan_out.ipynb`](labs/D2_3_fan_out.ipynb) |
| 2.4 | Day 2 · Session 4 | Five metrics in the semantic layer | [`D2_4_semantic_layer.ipynb`](labs/D2_4_semantic_layer.ipynb) |
| 3.1 | Day 3 · Session 1 | A wireframe from the brief | [`D3_1_wireframe.ipynb`](labs/D3_1_wireframe.ipynb) |
| 3.2 | Day 3 · Session 2 | Three bilingual panels | [`D3_2_bilingual_panels.ipynb`](labs/D3_2_bilingual_panels.ipynb) |
| 3.3 | Day 3 · Session 3 | Under three seconds | [`D3_3_load_time.ipynb`](labs/D3_3_load_time.ipynb) |
| 3.4 | Day 3 · Session 4 | The October ridership drop | [`D3_4_ridership_drop.ipynb`](labs/D3_4_ridership_drop.ipynb) |
| 4.1 | Day 4 · Session 1 | Ten questions, raw schema | [`D4_1_agent_raw.ipynb`](labs/D4_1_agent_raw.ipynb) |
| 4.2 | Day 4 · Session 2 | Ten certified answers | [`D4_2_certified_answers.ipynb`](labs/D4_2_certified_answers.ipynb) |
| 4.3 | Day 4 · Session 3 | Forty questions, two configurations | [`D4_3_score_configs.ipynb`](labs/D4_3_score_configs.ipynb) |
| 4.4 | Day 4 · Session 4 | The go or no-go memo | [`D4_4_go_no_go.ipynb`](labs/D4_4_go_no_go.ipynb) |
<!-- /academy:labs -->

## Capstone

Catalogue, semantic model, dashboard and agent memo for a second subject area (fares and concessions), in a public repository whose README reports measured query accuracy and load times, defended in a ten-minute review

| Criterion | Weight |
|---|---|
| Catalogue | 25 |
| Semantic model | 25 |
| Dashboard | 20 |
| Agent evaluation | 20 |
| Reproducibility | 10 |

The brief and a README template are in `labs/capstone/`. Each review lasts ten minutes: a six-minute walk-through,
then four minutes in which the assessor picks a dashboard figure and you trace it to source rows.

**Submission:** a public GitHub repository for the fares and concessions area: the metric catalogue, the Apache
Ossie model with its test queries, the dashboard with its one-page rationale, the agent memo, and a README that
reports the measured query accuracy and the load times and says how to rerun them.

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

### National references

- [NDMO Data Management and Personal Data Protection Standards (Business Intelligence and Analytics domain)](https://sdaia.gov.sa/en/SDAIA/about/Documents/DataManagementPersonalDataProtectionStandards.pdf)
- [NDMO Data Classification Policy](https://sdaia.gov.sa/en/SDAIA/about/Documents/DataClassificationPolicy.pdf)
- [Personal Data Protection Law](https://sdaia.gov.sa/en/SDAIA/about/Documents/PersonalDataProtectionLaw.pdf)
- [Implementing Regulation of the Personal Data Protection Law](https://sdaia.gov.sa/en/SDAIA/about/Documents/ImplementingRegulationPersonalDataProtectionLaw.pdf)
- [SDAIA Generative AI Guidelines for Government](https://sdaia.gov.sa/en/SDAIA/about/Files/GenAIGuidelinesForGovernmentENCompressed.pdf)

### Semantic layers and metric definitions

- [Apache Ossie (Incubating): the new name for Open Semantic Interchange](https://ossie.apache.org/updates/ossie-enters-apache-incubator/)
- [Apache Ossie core specification (spec.md) and JSON Schema](https://github.com/apache/ossie/blob/main/core-spec/spec.md)
- [Apache Ossie converters (dbt, Cube, Snowflake, Polaris and others)](https://github.com/apache/ossie-converters)
- [MetricFlow](https://github.com/dbt-labs/metricflow)
- [Cube Core](https://github.com/cube-js/cube)

### Engines, dashboards and libraries

- [DuckDB on PyPI](https://pypi.org/project/duckdb/)
- [DuckDB documentation: window functions](https://duckdb.org/docs/stable/sql/functions/window_functions)
- [Apache Superset](https://github.com/apache/superset)
- [Metabase](https://github.com/metabase/metabase)
- [Vega-Altair](https://altair-viz.github.io/)
- [hijridate: Hijri and Gregorian dates on the Umm al-Qura calendar](https://pypi.org/project/hijridate/)

### Conversational analytics

- [Lei et al., Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows (ICLR 2025)](https://arxiv.org/abs/2411.07763)
- [OpenRouter: the list of models, with the free ones](https://openrouter.ai/models?max_price=0)
<!-- /academy:sources -->

### National references

- NDMO Data Management and Personal Data Protection Standards (Business Intelligence and Analytics domain): https://sdaia.gov.sa/en/SDAIA/about/Documents/DataManagementPersonalDataProtectionStandards.pdf
- NDMO Data Classification Policy: https://sdaia.gov.sa/en/SDAIA/about/Documents/DataClassificationPolicy.pdf
- Personal Data Protection Law: https://sdaia.gov.sa/en/SDAIA/about/Documents/PersonalDataProtectionLaw.pdf, and its Implementing Regulation: https://sdaia.gov.sa/en/SDAIA/about/Documents/ImplementingRegulationPersonalDataProtectionLaw.pdf
- SDAIA Generative AI Guidelines for Government: https://sdaia.gov.sa/en/SDAIA/about/Files/GenAIGuidelinesForGovernmentENCompressed.pdf

All four were read on 15 November 2026 from the addresses above, linked from SDAIA's regulations and policies page:
https://sdaia.gov.sa/en/SDAIA/about/Pages/RegulationsAndPolicies.aspx
