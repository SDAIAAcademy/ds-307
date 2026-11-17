---
course: "Metrics, Semantic Models and Dashboards"
code: "DS-307"
version: "2027.1.0"
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-307/index.html"
---

# Metrics, Semantic Models and Dashboards

المقاييس والنماذج الدلالية ولوحات المعلومات

Data Science Track · 4 teaching days + capstone day · 26 hours · Level 300

Define each number once, model it, show it to the person who decides, and test the agent that answers questions about it

Participants take over performance reporting for Wadi Noor Transit, a fictional bus operator whose three reports give three different on-time figures. On a synthetic warehouse of trips, boardings and routes they write governed metric definitions, build a semantic model that defines each metric once, design a dashboard for one decision within a load-time budget, trace an anomaly to its source, and test a conversational analytics agent on certified questions with and without the semantic layer. Platform-scale semantic layer design is DS-408.

**Who it is for:** Practitioners. Data scientists and analysts who have completed the level 200 set or can show equivalent work: an analysis they framed, carried out and explained to a stakeholder.

**Format:** Intensive: 4 teaching days of four sessions and a capstone day, with guided pre-work and a tracked follow-up task

## The case study

**Wadi Noor Transit.** A fictional city bus operator with twelve routes from three depots, whose operations, planning and board reports give three different on-time figures for the same month. A synthetic warehouse (January to October 2026, fixed seed) holds about 85,000 trips, 329,000 timepoint arrivals, 849,000 card taps, 2,400 complaints and 121,000 fare sales, with planted problems for every session.

## The course

### Day 1: Define the numbers

Slides: https://sdaiaacademy.github.io/ds-307/slides/day1.md

- **Session 1: Why three reports disagree**
  - Name the four places two definitions of one measure can differ
  - Reproduce a published figure from its written rule
  - Explain a gap between two figures one rule at a time
  - [Lab 1.1: Three on-time figures (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D1_1_three_on_time.ipynb)
- **Session 2: Anatomy of a metric definition**
  - Write a definition with formula, grain, filters, time logic, owner and limits
  - Tell taps, cards and journeys apart
  - Reconcile a definition to the source totals
  - [Lab 1.2: Four ridership definitions (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D1_2_ridership_metrics.ipynb)
- **Session 3: Ratios, distinct counts and time logic**
  - Compute a ratio of sums and say why it differs from a mean of ratios
  - Explain why distinct counts do not add across periods
  - Test a metric against hand-computed values
  - [Lab 1.3: Two ratio metrics, tested (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D1_3_ratio_metrics.ipynb)
- **Session 4: Metric trees**
  - Decompose a goal metric into drivers that multiply back to it
  - Add a guardrail that a driver could harm
  - Assign an owner to each node
  - [Lab 1.4: A network metric tree (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D1_4_metric_tree.ipynb)

### Day 2: Model once

Slides: https://sdaiaacademy.github.io/ds-307/slides/day2.md

- **Session 1: Star schemas for analysis**
  - State the grain of each fact table
  - Prove a key by counting
  - Draw the star of a subject area
  - [Lab 2.1: Facts, dimensions and their grain (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D2_1_star_schema.ipynb)
- **Session 2: Changing dimensions and calendars**
  - Join a fact to the dimension version valid on its date
  - Compare a route before and after a change
  - Report by Hijri month and in Ramadan from one date table
  - [Lab 2.2: A re-routed line and two calendars (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D2_2_route_history.ipynb)
- **Session 3: Fan-out and join paths**
  - Recognise a join that repeats rows
  - Write a reconciliation test against a source total
  - Aggregate each fact before joining
  - [Lab 2.3: The double-counting join (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D2_3_fan_out.ipynb)
- **Session 4: Metrics in an open specification**
  - Write datasets, fields, relationships and metrics in an Apache Ossie document
  - Tell a dataset-scoped from a model-scoped metric
  - Validate a model and run test queries against it
  - [Lab 2.4: Five metrics in the semantic layer (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D2_4_semantic_layer.ipynb)

### Day 3: Show and investigate

Slides: https://sdaiaacademy.github.io/ds-307/slides/day3.md

- **Session 1: Dashboards start from a decision**
  - Turn a brief into a decision, an audience and a cadence
  - Give every panel a comparison
  - Cut a dashboard to the panels the decision needs
  - [Lab 3.1: A wireframe from the brief (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D3_1_wireframe.ipynb)
- **Session 2: Comparisons and bilingual layout**
  - Show a number against a target and a prior period
  - Lay out the same panel in Arabic and English
  - Suppress small counts before publishing
  - [Lab 3.2: Three bilingual panels (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D3_2_bilingual_panels.ipynb)
- **Session 3: Load time is a design constraint**
  - Measure a dashboard tile by tile
  - Replace per-tile queries with one grouped query
  - Pre-aggregate to the grain the panels need, keeping the parts of each ratio
  - [Lab 3.3: Under three seconds (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D3_3_load_time.ipynb)
- **Session 4: Investigating an anomaly**
  - Drill a change down a tree of segments
  - Tell a data fault from a change in demand
  - Write an anomaly note with cause, segments and correction
  - [Lab 3.4: The October ridership drop (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D3_4_ridership_drop.ipynb)

### Day 4: Let an agent answer

Slides: https://sdaiaacademy.github.io/ds-307/slides/day4.md

- **Session 1: From question to query**
  - Describe the steps from a question to a query
  - Log every query an agent runs
  - Judge an answer against a governed figure
  - [Lab 4.1: Ten questions, raw schema (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D4_1_agent_raw.ipynb)
- **Session 2: Certified questions**
  - Write a certified answer with value, query and tolerance
  - Write a refusal with its reason
  - Mark the fields an agent may never read
  - [Lab 4.2: Ten certified answers (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D4_2_certified_answers.ipynb)
- **Session 3: With and without the semantic layer**
  - Score agent answers against certified ones
  - Classify wrong answers by error type
  - Compare accuracy by question type and configuration
  - [Lab 4.3: Forty questions, two configurations (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D4_3_score_configs.ipynb)
- **Session 4: What the agent may answer**
  - Set a tolerance for wrong figures
  - Decide per question type: answer, review or refuse
  - Write the decision with its evidence
  - [Lab 4.4: The go or no-go memo (25 min)](https://sdaiaacademy.github.io/ds-307/labs/D4_4_go_no_go.ipynb)

### Capstone: Capstone: fares and concessions

Slides: https://sdaiaacademy.github.io/ds-307/slides/capstone.md

## Capstone

Catalogue, semantic model, dashboard and agent memo for a second subject area (fares and concessions), in a public repository whose README reports measured query accuracy and load times, defended in a ten-minute review

**What you submit:** A public GitHub repository for the fares and concessions area: the metric catalogue, the Apache Ossie model with its test queries, the dashboard with its one-page rationale, the agent memo, and a README that reports the measured query accuracy and the load times and says how to rerun them.

**Rubric:**

- Catalogue: 25%
- Semantic model: 25%
- Dashboard: 20%
- Agent evaluation: 20%
- Reproducibility: 10%

## Outcomes

- **LO1** Explain why reports built on one warehouse disagree on the same measure, given three operator reports with different on-time figures (Awareness) Evidence: a diagnosis naming the definitional cause of each difference
- **LO2** Draft metric definitions stating formula, grain, filters, time logic, owner and limits, given twelve business questions and the data dictionary (Applied) Evidence: a metric catalogue that passes a peer checklist and reconciles to source totals
- **LO3** Implement a star-schema semantic model with a slowly changing route dimension and each metric defined once, given the synthetic transit warehouse (Applied) Evidence: reference values returned for 25 test queries
- **LO4** Analyse a metric anomaly by drill-down and segmentation to find its source, given a seeded drop in weekly ridership (Applied) Evidence: an anomaly note naming the cause, affected segments and correction
- **LO5** Design a dashboard for a named audience and decision within a load-time budget, given the operations director's brief and a three-second budget (Performance) Evidence: a dashboard, a one-page rationale and recorded timings, scored on a rubric
- **LO6** Evaluate a conversational analytics agent against governed metrics and decide which question types it may answer unreviewed, given 40 certified questions and a stated tolerance for wrong figures (Performance) Evidence: a memo with accuracy by question type and configuration, plausible wrong answers and a go or no-go decision

## Tools

- **Analytical SQL engine:** DuckDB, PostgreSQL
- **Semantic layer and metric definitions:** MetricFlow, Cube Core, Apache Ossie (Open Semantic Interchange) files
- **Dashboard tool:** Apache Superset, Metabase, an enterprise BI tool
- **Language model through a chat-completions style endpoint:** a locally served open-weight model, a free hosted open-weight model

## Prerequisites

- FN-104 SQL and Data Wrangling
- DS-203 Exploratory Analysis and Visualisation
- Writes SQL with joins, grouping and window functions
- Has built a chart-based report for others

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

---

SDAIA Academy · Data Science Track · Metrics, Semantic Models and Dashboards

Course version 2027.1.0 · engine 1.0.0 · built 2026-11-15 · commit 6720e14
