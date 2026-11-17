# Capstone · Fares and concessions

The capstone is individual. You do for **Wadi Noor Transit's fares and concessions** what the course did for network
performance: a metric catalogue, an Apache Ossie semantic model with test queries, a dashboard for one decision, and
an evaluation of Nabih on certified questions. You publish it in a **public GitHub repository** whose README reports
the measured query accuracy and load times and says how to rerun them. Then you defend it in a **ten-minute review**:
six minutes of walk-through, then four minutes in which the assessor picks a figure on your dashboard and you trace it
to source rows, live.

## The area

Yasmeen Al-Jaafari (strategy and finance) must recommend, by the end of the year, whether the free senior and
disability passes stay free, and whether the 30-day pass price changes. Her questions, for a start:

- How much do passes bring in, by product and fare type, month by month, in both calendars?
- How many free concession passes are issued, and how many taps do their holders make?
- What does a tap cost the operator in lost revenue for each fare type?
- Which sales channels (app, kiosk, driver) carry which products?

The data is in the course warehouse (`labs/data/warehouse/`): `fct_fare_sale` (121,000 pass sales),
`dim_fare_product`, `dim_fare_type`, `fct_boarding` (taps, with `fare_sar` for single fares paid at the validator)
and `dim_date`. Senior and disability fares are **Restricted at card level** (`dim_fare_type.card_level_classification`):
you may count them; you may not show, group or filter by a card. Use only the course's synthetic data or data you
generate yourself; no personal data and no internal data of your entity.

## Minimum requirements

1. **Catalogue.** At least eight governed metrics for the area, each with name, question, formula, table, grain,
   filters, time logic, unit, owner and limits; each passes `wnt.lint()` and reconciles to a source total.
2. **Semantic model.** An Apache Ossie document that validates (`starter.py validate`), with the relationships your
   metrics need, at least two model-scoped metrics written with `AGG()`, the access rules of the Restricted fields,
   and **at least 15 test queries** whose expected rows come from independent SQL; all pass (`starter.py test`).
3. **Dashboard.** A wireframe that passes the brief checker of Lab 3.1 against your own brief for Yasmeen's decision,
   at most six panels, built from the model in Arabic and English, with small counts suppressed; a **one-page
   rationale**; the load time measured from a clean process (`starter.py time`) under three seconds.
4. **Agent evaluation.** **At least 20 certified questions** across at least four types, refusals included; Nabih
   scored on them in the semantic configuration (`starter.py score`), live with a free model if you have a key or with
   your own stand-in file otherwise, stating which; a go or no-go memo per question type that passes the checklist of
   Lab 4.4.
5. **Reproducibility.** A clean clone reruns every number in the README with `uv run`; every number is backed by a
   committed file in `results/`.

## Rubric

| Criterion | Points | Full marks look like |
|---|---|---|
| Catalogue | 25 | every definition complete, linted and reconciled; the concession metrics state their limits |
| Semantic model | 25 | validates; 15 or more independent test queries pass; Restricted fields enforced by a role |
| Dashboard | 20 | one decision, comparisons on every panel, bilingual, suppression, measured load time |
| Agent evaluation | 20 | certified set with refusals; accuracy by type; plausible wrong answers named; a decision with its uncertainty |
| Reproducibility | 10 | a clean clone reproduces the README's numbers; the mode of every agent answer is recorded |

The capstone repository counts for 60% of the course result, and you need at least 60% on this rubric. The live
trace counts for 20% and the supervised AI-off check for the other 20%. The pass mark is 70% overall.

**AI policy.** AI is allowed. For each definition an assistant drafted, add a verification note: the query you ran to
check it and what you changed. The commit history and the query logs are part of the evidence of authorship.

## Getting started

```bash
cd labs
uv run python capstone/starter.py validate     # the starter model validates
uv run python capstone/starter.py test         # 3 example test queries
uv run python capstone/starter.py time         # the example dashboard's load time
uv run python capstone/starter.py score        # 3 example certified questions (stand-in without a key)
```

- `fares_model_starter.yaml`: the starter model (pass sales and dates, two metrics). Search for `CAPSTONE:`.
- `test_queries.example.yaml`, `certified.example.yaml`, `stand_in.example.yaml`: the formats, with three entries each.
- `TEMPLATE_README.md`: the README your repository starts from.

Copy the folder into your own repository with `wnt.py`, `wnt_semantic.py`, `wnt_dash.py`, `wnt_agent.py`,
`pyproject.toml` and the warehouse, or point the commands at a clone of this course.

## The labs closest to each part

| Part | Labs |
|---|---|
| Catalogue | 1.2 (definitions), 1.3 (ratios and distinct counts), 1.4 (a metric tree) |
| Semantic model | 2.1 (grain), 2.2 (history and calendars), 2.3 (fan-out), 2.4 (the model and its tests) |
| Dashboard | 3.1 (wireframe), 3.2 (bilingual panels), 3.3 (load time) |
| Agent evaluation | 4.2 (certified answers), 4.3 (scoring), 4.4 (the memo) |
