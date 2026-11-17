---
course: "Metrics, Semantic Models and Dashboards"
code: "DS-307"
version: "2027.1.0"
scope: "course"
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-307/"
---

# Metrics, Semantic Models and Dashboards

Define each number once, model it, show it to the person who decides, and test the agent that answers questions about it

Participants take over performance reporting for Wadi Noor Transit, a fictional bus operator whose three reports give three different on-time figures. On a synthetic warehouse of trips, boardings and routes they write governed metric definitions, build a semantic model that defines each metric once, design a dashboard for one decision within a load-time budget, trace an anomaly to its source, and test a conversational analytics agent on certified questions with and without the semantic layer. Platform-scale semantic layer design is DS-408.

- **Audience:** Practitioners. Data scientists and analysts who have completed the level 200 set or can show equivalent work: an analysis they framed, carried out and explained to a stakeholder.
- **Prerequisites:** FN-104 SQL and Data Wrangling; DS-203 Exploratory Analysis and Visualisation; Writes SQL with joins, grouping and window functions; Has built a chart-based report for others
- **Case study:** Wadi Noor Transit: A fictional city bus operator with twelve routes from three depots, whose operations, planning and board reports give three different on-time figures for the same month. A synthetic warehouse (January to October 2026, fixed seed) holds about 85,000 trips, 329,000 timepoint arrivals, 849,000 card taps, 2,400 complaints and 121,000 fare sales, with planted problems for every session.

## Outcomes

- LO1 (Awareness): Explain why reports built on one warehouse disagree on the same measure, given three operator reports with different on-time figures
- LO2 (Applied): Draft metric definitions stating formula, grain, filters, time logic, owner and limits, given twelve business questions and the data dictionary
- LO3 (Applied): Implement a star-schema semantic model with a slowly changing route dimension and each metric defined once, given the synthetic transit warehouse
- LO4 (Applied): Analyse a metric anomaly by drill-down and segmentation to find its source, given a seeded drop in weekly ridership
- LO5 (Performance): Design a dashboard for a named audience and decision within a load-time budget, given the operations director's brief and a three-second budget
- LO6 (Performance): Evaluate a conversational analytics agent against governed metrics and decide which question types it may answer unreviewed, given 40 certified questions and a stated tolerance for wrong figures

## Day 1: Define the numbers

Three reports, one warehouse: definitions someone else can compute

#### [day1#title] Define the numbers

*SDAIA Academy · Metrics, Semantic Models and Dashboards*

Day 1: Three reports, one warehouse: definitions someone else can compute

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-307

#### [day1#four-days-one-operator] Four days from a disputed number to an agent you can trust with it

*The course at a glance*

- **Day 1 · Define.** Why reports disagree, definitions, ratios, metric trees.
- **Day 2 · Model.** Star schemas, a route that changed, fan-out, and each metric defined once in an open specification.
- **Day 3 · Show.** A dashboard for one decision under three seconds; an anomaly traced.
- **Day 4 · Test.** An agent on certified questions, and a go or no-go.

> **Day 5 · Capstone.** The same four pieces for a second subject area, fares and concessions, defended in a ten-minute review with a live trace of one figure.

#### [day1#how-we-work] Every number you show this week can be traced to its definition and its rows

*How this course works*

- **Reproduce first.** Before you argue about a number, compute it again from its written rule.
- **Define once.** One name, one formula, one owner. A second meaning gets a second name.
- **Test it.** Hand-computed values, source totals and reference queries, every day.

> **AI policy.** AI off for the first lab of each day and for the supervised check. A tutor in the other labs, explaining errors without writing your definitions. In the capstone an assistant may draft; every drafted definition carries a verification note. On Day 4 the agent is under test, not your helper.

#### [day1#wadi-noor-transit] Wadi Noor Transit: twelve bus routes, three depots, three on-time figures

*One case study all week*

A fictional city bus operator (نقل وادي نور). Synthetic data from January to October 2026. You are the new performance reporting analyst.

- **Mashael Al-Saadi.** Operations director. Decides every Sunday where the reserve buses and supervisors go.
- **Three report owners.** Tawfiq Al-Sahafi (control centre), Dhuha Al-Rowais (planning), Yasmeen Al-Jaafari (board pack).
- **Muneer and Haneen.** Muneer Al-Thaqafi owns the warehouse; Haneen Al-Shamrani owns data classification.

#### [day1#the-warehouse] Five facts, six dimensions, one embedded analytical database

*What you work on*

| Fact table | Rows | One row is |
| --- | --- | --- |
| `fct_trip` | 85,010 | a scheduled trip |
| `fct_timepoint` | 329,188 | a trip at one of four timepoints |
| `fct_boarding` | 848,501 | a card tap at a validator |
| `fct_complaint` | 2,400 | a complaint |
| `fct_fare_sale` | 121,133 | a pass sold (capstone) |

- **DuckDB in the notebook.** `W.db()` opens the Parquet files as read-only views. PostgreSQL would serve the same queries.
- **Dimensions.** Dates with both calendars, routes with history, vehicles, depots, fare types and products.

#### [day1#setup-check] Run the setup check before the first lab

*Lab environment*

1. In **Google Colab**: open a lab from the course page; its first cell clones the course and installs what it needs.
2. On a laptop: install **uv**, then the commands on the right.
3. Run `00_setup_check.ipynb`. Every lab starts from supplied data, never from another lab of the same day.

```bash
# file: terminal (local option)
git clone https://github.com/SDAIAAcademy/ds-307
cd ds-307/labs
uv sync
uv run jupyter lab
```

#### [day1#agenda] Define the numbers

*Today*

- **Session 1 · Why three reports disagree**: What makes three reports on one warehouse give three numbers
- **Session 2 · Anatomy of a metric definition**: The eight parts of a definition someone else can compute
- **Session 3 · Ratios, distinct counts and time logic**: Ratios, distinct counts and the calendar inside a metric
- **Session 4 · Metric trees**: From one goal metric to the drivers a team can move

### Session 1: Why three reports disagree

#### [day1#s1] Why three reports disagree

*Session 1*

- Name the four places two definitions of one measure can differ
- Reproduce a published figure from its written rule
- Explain a gap between two figures one rule at a time

#### [day1#three-figures] One warehouse, one month, three on-time figures

*The problem you inherit*

- **80.7%** Operations report, September
- **66.0%** Planning service review, September
- **58.4%** Board pack, September meeting

Nobody made an arithmetic error. Each figure is right for its own rule.

#### [day1#rules-as-written] The three owners wrote three different rules under one name

*Read the rules, not the totals*

| Report | Counts | On time means | Cancelled trips | Period |
| --- | --- | --- | --- | --- |
| Operations (Tawfiq) | trips | left the first stop 1 min early to 5 late | left out | September |
| Planning (Dhuha) | timepoint arrivals | 1 min early to 5 late, at every timepoint | no arrivals to count | September |
| Board (Yasmeen) | trips | reached the terminus at most 5 min late | count as late | Rabi al-Thani 1448 |

Source: `labs/data/reports/three_reports.yaml`, the sentence under each report.

#### [day1#four-places] Two definitions of one measure differ in four places

*Where definitions differ*

- **Grain.** What is counted: trips, timepoint arrivals, riders, cards.
- **Rule.** Where it is measured and the tolerance: first stop or terminus, early allowed or not.
- **Filter.** What enters the denominator: cancelled trips, partial trips, holidays.
- **Period.** Which dates: Gregorian month, Hijri month, a Sunday week or an ISO week.

> **Use it as a checklist.** Two figures that disagree differ in at least one of these four. Find which before you look for a bug.

#### [day1#reconciliation-walk] Change one rule at a time and the gap explains itself

*A reconciliation walk*

| Item | Value |
| --- | --- |
| Operations rules | 80.7% |
| Measured at the terminus | 50.4% |
| Early arrivals allowed | 59.7% |
| Cancelled trips count as late | 58.0% |
| Hijri month, not September | 58.4% |

#### [day1#grain-changes-question] Counting timepoints, not trips, asks a different question

*The biggest step*

- **Per trip, at the first stop.** "Did the bus leave when the timetable said?" The rider waiting at the start can plan on it.
- **Per timepoint arrival.** "Was the bus on time along the way?" Delays build up, so later timepoints pull the figure down.

> **Neither is wrong.** Planning's 66.0% is the honest answer to its own question. The fault is the shared name.

#### [day1#cost-of-disagreement] A disputed number spends the meeting on the number, not the decision

*Why it matters*

- Three figures invite each team to **quote the one that suits it**
- Every new report adds a definition nobody wrote down
- An agent asked "what was on-time performance?" will pick one, and **not say which**
- The fix is not a fourth report: it is one catalogue, one owner per metric

#### [day1#diagnosis-table] The diagnosis names a definitional cause for each difference

*What you hand over*

| Difference | Causes, in walk order |
| --- | --- |
| Operations 80.7% vs planning 66.0% | grain (trips vs timepoint arrivals) |
| Operations 80.7% vs board 58.4% | point measured, tolerance, cancelled trips, period |

This table, with the walk behind it, is the evidence for the first course outcome.

#### [day1#checkpoint-1] Why is the planning figure lower?

*Checkpoint*

**Question:** Operations reports 80.7% and planning 66.0% for the same September, on the same warehouse, both with a tolerance of one minute early to five late. What explains most of the gap?

- A. Planning reads a stale copy of the data
- B. Planning counts every timepoint arrival, where delays have built up
- C. Planning counts cancelled trips as late
- D. Planning reports a Hijri month

#### [day1#lab-1-1] Three on-time figures

Lab 1.1 · 25 min

Compute the operations, planning and board on-time figures for September from their written rules, walk from one to the next one rule at a time, and write the diagnosis.

[D1_1_three_on_time.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D1_1_three_on_time.ipynb)

- [ ] Compute the operations figure from its rule (6 min)
- [ ] Compute the planning and board figures (7 min)
- [ ] Walk from one figure to the next, one rule at a time (8 min)
- [ ] Write the diagnosis: one cause per difference (4 min)
- [ ] ✱ Stretch: Which figure answers the question the operations director asks every Sunday?

### Session 2: Anatomy of a metric definition

#### [day1#s2] Anatomy of a metric definition

*Session 2*

- Write a definition with formula, grain, filters, time logic, owner and limits
- Tell taps, cards and journeys apart
- Reconcile a definition to the source totals

#### [day1#ridership-four-numbers] "Ridership last week" is four different numbers

*One word, four numbers*

| Item | Value |
| --- | --- |
| Card taps | 19,826 |
| Linked journeys | 16,231 |
| Card-days | 13,992 |
| Different cards | 9,864 |

The week of 13 to 19 September 2026, from Lab 1.2.

#### [day1#taps-cards-journeys] A tap, a journey and a card count different things

*Counting units in transit*

1. **Tap** one card at one validator, every boarding
2. **Journey** taps of one card within 60 minutes linked as one trip
3. **Card-day** one card that travelled on a day
4. **Card** one card seen in the period

> **The trap.** Each step to the right is distinct within its period, so it is no longer additive: card-days add across days, cards do not.

#### [day1#eight-parts] A definition someone else can compute has eight parts

*Anatomy of a definition*

1. **Name** and the **question** it answers
2. **Formula**: one aggregate, or a ratio of two
3. **Grain**: what one counted row is
4. **Filters**: what is in and out

5. **Time logic**: which date, which calendar, which week
6. **Unit** of the result
7. **Owner**: a person and their role
8. **Limits**: what it must not be used for

> **The test.** Give it to a colleague: if they compute your number without asking you anything, it is a definition.

#### [day1#one-definition] The journeys definition, as the catalogue holds it

*An entry of the catalogue*

```yaml
# file: labs/data/catalogue/metric_catalogue.yaml
- name: journeys
  question: How many journeys did riders make, counting a transfer as part of one journey?
  formula: SUM(journey_start)
  table: boarding_linked
  grain: one card tap, journey_start = 1 when the card made no tap in the 60 minutes before
  filters: none
  time_logic: service_date of the tap; the 60-minute look-back crosses midnight
  unit: journeys
  owner: Dhuha Al-Rowais, network planning manager
  limits: a return trip within 60 minutes counts as a transfer
```

#### [day1#owner-and-change] An owner decides what the metric means; a change gets a new version

*Owners and change control*

- The **owner** answers questions about the definition and approves changes
- A change that moves the number is announced, dated and versioned
- A second meaning is a **second metric** with its own name and owner
- The board's measure stays, renamed `terminal_on_time_rate`, owned by Yasmeen

#### [day1#reconcile-to-source] A definition reconciles when its formula, run as written, gives the source total

*Proof, not belief*

```python
# file: Lab 1.2 · reconcile
for d in defs:
    got = W.measure(con, d, *WEEK)
    W.check(got == counts[d["name"]], d["name"])
```

- Run the formula on the table the definition names, for the period
- Compare with the count taken directly from the source
- Add a sum test: **taps by route plus taps without a route equal all taps**

#### [day1#dictionary-classification] The dictionary marks what a metric may count but never show

*Responsible use, from the first definition*

- `card_id` is pseudonymous personal data: **Restricted**
- Counting distinct cards is allowed; listing them is not
- The PDPL limits personal data to the minimum the purpose needs
- Counts of cards are not shown below 10

- **Four levels.** The NDMO Data Classification Policy has four: Top Secret, Secret, Restricted, Public. Label every field the catalogue uses.

#### [day1#checkpoint-2] Which definition can a colleague compute without asking?

*Checkpoint*

**Question:** Four drafts of "weekly riders". Which one could Muneer compute for any week and get the number you would get?

- A. Distinct cards in fct_boarding per week
- B. COUNT(DISTINCT card_id)
- C. Riders who used the network last week, owned by planning
- D. COUNT(DISTINCT card_id) on fct_boarding, by service_date, weeks Sunday to Saturday

#### [day1#lab-1-2] Four ridership definitions

Lab 1.2 · 25 min

Count four ridership numbers for one week, write each as a governed definition, run the peer checklist and reconcile every definition to the source totals.

[D1_2_ridership_metrics.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D1_2_ridership_metrics.ipynb)

- [ ] Count four ridership numbers for one week (6 min)
- [ ] Write the four definitions in the catalogue template (8 min)
- [ ] Run the peer checklist (5 min)
- [ ] Reconcile each definition to the source totals (6 min)
- [ ] ✱ Stretch: Add the Arabic name and a limits line to each definition

### Session 3: Ratios, distinct counts and time logic

#### [day1#s3] Ratios, distinct counts and time logic

*Session 3*

- Compute a ratio of sums and say why it differs from a mean of ratios
- Explain why distinct counts do not add across periods
- Test a metric against hand-computed values

#### [day1#ratio-of-sums] A network rate is a ratio of sums, not a mean of route rates

*Ratios*

| Route | Departed | On time | Rate |
| --- | --- | --- | --- |
| A | 100 | 90 | 90% |
| B | 10 | 5 | 50% |
| C | 40 | 30 | 75% |
| Network | 150 | 125 | 83.3% |

**71.7%** mean of the three route rates

- **Not the network.** The mean gives route B's ten trips the weight of route A's hundred.

#### [day1#when-mean-of-ratios] A mean of ratios answers "how does a typical route do?"

*When the mean is right*

- Network performance: **ratio of sums**, each trip counted once
- The typical route: **mean of route ratios**, each route counted once
- Both are legitimate; they are **two metrics** with two names
- A dashboard that averages a column of percentages has chosen the second without saying so

#### [day1#distinct-not-additive] Weekly distinct cards do not add up to a month

*Distinct counts*

| Week starting | Distinct cards |
| --- | --- |
| 2026-09-06 | 9,909 |
| 2026-09-13 | 9,864 |
| 2026-09-20 | 9,257 |
| 2026-09-27 | 9,734 |

- **38,764** the four weeks added
- **22,962** distinct over the four weeks

#### [day1#snapshots-and-flows] Flows add over time; snapshots do not

*Flows and snapshots*

- **Flow.** Taps, trips, complaints: events in a period. A month is the sum of its days.
- **Snapshot.** Active passes, buses in service, open complaints: a state on a date. A month is a chosen day, or an average of days, never a sum.

> **State the rule.** A snapshot metric's time logic names the day it is taken: the last day of the period, or the mean of daily values.

#### [day1#time-logic] Which date, which week, which calendar

*Time logic*

| Choice | At Wadi Noor | What goes wrong otherwise |
| --- | --- | --- |
| The date that places a row | the service date of the trip | a trip after midnight lands on the next day |
| The week | Sunday to Saturday | ISO weeks start on Monday and split the working week |
| The month | Gregorian unless a Hijri month is named | Ramadan and the Eids move eleven days a year |
| Like with like | compare holiday timetables with holidays | National Day looks like a fall in demand |

#### [day1#test-a-metric] Test a metric on an example you computed by hand, then on the source

*Testing a metric*

1. **1 · By hand** a toy of three routes, with fractions on paper
2. **2 · Same rows** the toy as a table the function can read
3. **3 · Equal** the function returns the hand value exactly
4. **4 · Network** the function on September, against a reference

> **Also test what it must not equal.** The toy's ratio of sums must differ from its mean of ratios: a test that would pass with the wrong formula proves nothing.

#### [day1#checkpoint-3] How many cards travelled in September?

*Checkpoint*

**Question:** A dashboard shows distinct cards per week. A manager wants the September total for a funding bid. What do you give?

- A. A new distinct count over all of September's service dates
- B. The sum of the weekly figures
- C. The average of the weekly figures
- D. The largest weekly figure

#### [day1#lab-1-3] Two ratio metrics, tested

Lab 1.3 · 25 min

Implement the on-time rate and the cancellation rate as functions and test them against hand-computed values and the network totals; see why weekly distinct cards do not add to a month.

[D1_3_ratio_metrics.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D1_3_ratio_metrics.ipynb)

- [ ] Hand-compute the on-time rate of a small example (5 min)
- [ ] Implement the two ratio metrics (8 min)
- [ ] Test them against the hand values and the network (6 min)
- [ ] Show that weekly distinct cards do not add to a month (6 min)
- [ ] ✱ Stretch: The same two metrics by Hijri month

### Session 4: Metric trees

#### [day1#s4] Metric trees

*Session 4*

- Decompose a goal metric into drivers that multiply back to it
- Add a guardrail that a driver could harm
- Assign an owner to each node

#### [day1#tree-shape] A metric tree links one goal to the drivers that teams can move

*Metric trees*

1. **Goal** weekly card taps
2. **Timetable** scheduled trips
3. **Delivery** 1 − cancellation rate
4. **Demand** taps per departed trip

> **Guardrail.** Complaints per 10,000 taps: it watches for harm a driver could do, such as crowding more riders onto each bus.

#### [day1#tree-kinds] Multiply for rates and volumes, add for segments

*Two kinds of tree*

- **Multiplicative.** Taps = trips × (1 − cancelled) × taps per trip. Changes combine as products; log changes add.
- **Additive.** Taps = North + Central + East. Each segment's change adds to the total; Day 3 drills down this way.

> **Use both.** Multiply to find which driver moved; add to find where it moved.

#### [day1#tree-two-weeks] Taps fell 8.5%: the timetable explains almost all of it

*The tree on two weeks*

| Node | Week of 13 Sep | Week of 20 Sep | Change |
| --- | --- | --- | --- |
| Taps (goal) | 19,826 | 18,146 | -8.5% |
| Scheduled trips | 1,950 | 1,794 | -8.0% |
| 1 − cancellation rate | 97.0% | 97.7% | +0.8% |
| Taps per departed trip | 10.48 | 10.35 | -1.3% |

#### [day1#guardrail-and-owners] Every node has an owner, and the guardrail has a direction

*Owners on the nodes*

| Node | Owner |
| --- | --- |
| Taps | Muneer Al-Thaqafi, data platform |
| Scheduled trips, taps per departed trip | Dhuha Al-Rowais, planning |
| Cancellation rate | Tawfiq Al-Sahafi, control centre |
| Complaints per 10,000 taps (guardrail, worry if up) | Yasmeen Al-Jaafari, strategy |

#### [day1#tree-pitfalls] A tree misleads when its drivers overlap or do not reconcile

*What goes wrong*

- Two drivers that count the same thing double its effect
- A driver measured at another grain or period breaks the product
- A driver nobody owns is a number nobody acts on
- A tree with no guardrail rewards crowding, skipping stops or cutting short trips

#### [day1#nbia-kpis] The NDMO standards ask for analytics KPIs, measured and registered

*The national standard*

- The Business Intelligence and Analytics domain has **5 controls** and **10 specifications**
- It asks for a plan, prioritised use cases, validation of their outcomes, KPIs and a register
- A governed catalogue is the register of what each number means

- **For this course.** Each dashboard is a use case: validate it, and record the metrics it shows with their owners.

#### [day1#checkpoint-4] Which driver belongs in the tree?

*Checkpoint*

**Question:** The tree is taps = scheduled trips × (1 − cancellation rate) × taps per departed trip. A colleague proposes adding "on-time rate" as a fourth driver. What do you say?

- A. Add it: punctuality drives demand
- B. Replace the cancellation rate with it
- C. Keep it beside the tree, as a guardrail or its own goal
- D. Leave it out of the review

#### [day1#lab-1-4] A network metric tree

Lab 1.4 · 25 min

Build a tree from weekly boardings to three drivers and a guardrail, reconcile it for two weeks and say which driver moved.

[D1_4_metric_tree.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D1_4_metric_tree.ipynb)

- [ ] Choose the goal and its decomposition (5 min)
- [ ] Compute the three drivers for two weeks (8 min)
- [ ] Reconcile the tree to the goal (6 min)
- [ ] Add the guardrail and the owners (6 min)
- [ ] ✱ Stretch: Attribute the week-on-week change to each driver with log changes

#### [day1#wrap-up] Three things to keep

*Day 1 · wrap-up*

- **Diagnose before you debug.** Two figures differ in grain, rule, filter or period before they differ by a bug.
- **One name, one meaning.** Eight parts and an owner; a second meaning gets a second name.
- **Ratios and distinct counts.** Ratio of sums for a network; distinct counts are computed again, never summed.

#### [day1#next] Day 2: Model once

*Next*

Tomorrow the catalogue becomes a star schema and a semantic model in which each metric is defined once. Finish today's labs if you can; Day 2 starts from the supplied catalogue either way.

## Day 2: Model once

One semantic model in which each metric is defined once

#### [day2#title] Model once

*SDAIA Academy · Metrics, Semantic Models and Dashboards*

Day 2: One semantic model in which each metric is defined once

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-307

#### [day2#agenda] Model once

*Today*

- **Session 1 · Star schemas for analysis**: Facts at a stated grain, dimensions that describe them
- **Session 2 · Changing dimensions and calendars**: Type 2 history for a re-routed line, and two calendars in one date table
- **Session 3 · Fan-out and join paths**: Fan and chasm traps, and the test that catches them
- **Session 4 · Metrics in an open specification**: A semantic model as an open document: datasets, relationships, metrics

#### [day2#review-day1] Which part of the definition is missing?

*Review of Day 1*

**Question:** "journeys: SUM(journey_start) on boarding_linked; one card tap; filters none; unit journeys; owner Dhuha Al-Rowais, planning; limits: a quick return counts as a transfer." Which of the eight parts is missing?

- A. The grain
- B. The owner
- C. The time logic
- D. The limits

### Session 1: Star schemas for analysis

#### [day2#s1] Star schemas for analysis

*Session 1*

- State the grain of each fact table
- Prove a key by counting
- Draw the star of a subject area

#### [day2#why-a-model] A definition says what a number means; a model computes it the same way everywhere

*From catalogue to model*

1. **Catalogue** meaning, owner, limits (Day 1)
2. **Star schema** facts at a grain, dimensions to slice by
3. **Semantic model** each metric written once, joins decided once
4. **Every consumer** dashboard, notebook, agent

#### [day2#facts-and-dimensions] Facts record events at a grain; dimensions describe them

*Two kinds of table*

- **Facts.** Trips, timepoint arrivals, taps, complaints. Many rows, numeric columns to aggregate, foreign keys to dimensions.
- **Dimensions.** Routes, dates, vehicles, depots. Few rows, descriptive columns to group and filter by, one key each.

> **Ask of every column:** do I add it up, or do I slice by it? The answer places it in a fact or in a dimension.

#### [day2#star-of-wadi-noor] Four facts share dates, routes and vehicles

*The star*

Figure: Facts are rectangles, dimensions rounded. Every line is many-to-one, from the fact to what it points at.

#### [day2#grain-recap] A grain is a sentence; a key test proves it

*Recap from FN-104*

```sql
-- file: Lab 2.1 · key_test
SELECT count(*)                         AS rows,
       count(DISTINCT (trip_id, tp_seq)) AS keys,
       count(*) FILTER (WHERE trip_id IS NULL
                         OR tp_seq IS NULL) AS empty
FROM fct_timepoint;
```

- `fct_timepoint`: one departed trip at one timepoint
- 329,188 rows, 329,188 keys, none empty: the grain holds
- Grain, keys and orphans were taught in FN-104, Day 1; today they are the input of a model

#### [day2#natural-key-fails] dim_route has 13 rows for 12 routes

*The planted surprise*

| route_key | route_id | route_name_en | length_km | valid_from | valid_to |
| --- | --- | --- | --- | --- | --- |
| 7 | R07 | Al-Rawdah Feeder | 11.4 | 2026-01-01 | 2026-05-31 |
| 8 | R07 | Al-Rawdah Hospital Feeder | 15.8 | 2026-06-01 | (open) |

- `route_id` is the natural key riders use; `route_key` identifies one version
- A join on `route_id` returns **91,418 rows for 85,010 trips**: every R07 trip twice

#### [day2#conformed-dimensions] One date table and one route table serve every fact

*Conformed dimensions*

- Trips and taps grouped by the same `dim_date.week_start` mean the same week
- A second date table with Monday weeks would bring back yesterday's disagreement
- Conformed means: **same keys, same attributes, same meaning** for every fact
- Lab 2.1's stretch checks that every service date of every fact is a row of `dim_date`

#### [day2#checkpoint-1] What is the grain of the timepoint table?

*Checkpoint*

**Question:** `fct_timepoint` has 329,188 rows, 82,000 distinct `trip_id` values and `tp_seq` from 1 to 4. What does one row mean?

- A. One trip
- B. One timepoint of a route
- C. One scheduled minute of a trip
- D. One departed trip at one timepoint

#### [day2#lab-2-1] Facts, dimensions and their grain

Lab 2.1 · 25 min

Name the grain of each warehouse table, prove it with key tests, draw the star and find the dimension whose natural key is not unique.

[D2_1_star_schema.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D2_1_star_schema.ipynb)

- [ ] Name the grain of each table (5 min)
- [ ] Prove the grains with key tests (8 min)
- [ ] Draw the star: facts, dimensions, keys (6 min)
- [ ] Find the dimension whose natural key fails (6 min)
- [ ] ✱ Stretch: Check that dates conform across the two facts

### Session 2: Changing dimensions and calendars

#### [day2#s2] Changing dimensions and calendars

*Session 2*

- Join a fact to the dimension version valid on its date
- Compare a route before and after a change
- Report by Hijri month and in Ramadan from one date table

#### [day2#dimensions-change] When a route changes, decide whether history changes with it

*Slowly changing dimensions*

- **Type 1: overwrite.** The new value replaces the old everywhere, past included. Right for corrections: a misspelt name.
- **Type 2: add a version.** A new row with its own key and validity dates. Right for real changes: a longer route, a new depot.

> **The test.** Would a January figure be wrong if it used the June value? Then it is type 2.

#### [day2#as-of-join] Join each fact row to the version valid on its date

*The as-of join*

```sql
-- file: Lab 2.2 · trips_with_version
SELECT t.*, r.route_key, r.route_name_en, r.length_km
FROM fct_trip t
JOIN dim_route r
  ON r.route_id = t.route_id
 AND t.service_date >= r.valid_from
 AND (r.valid_to IS NULL OR t.service_date <= r.valid_to)
```

85,010 trips in, 85,010 rows out. The open `valid_to` means "still valid".

#### [day2#r07-before-after] Per kilometre, R07 barely changed; per trip, it jumped

*Why the version matters*

| Version | Length | Departed trips | Taps | Taps per trip-km |
| --- | --- | --- | --- | --- |
| Al-Rawdah Feeder (Jan to May) | 11.4 | 3,068 | 22,716 | 0.649 |
| Al-Rawdah Hospital Feeder (Jun to Oct) | 15.8 | 3,187 | 33,513 | 0.666 |

> **With the current row for every date** the first five months show 0.469 taps per km: a fall that never happened.

#### [day2#dual-calendar] The date dimension carries the Gregorian and the Hijri calendar

*Two calendars, one table*

| Column | Example for 23 Sep 2026 |
| --- | --- |
| `gregorian_month` | 2026-09 |
| `hijri_date` | 1448-04-12 |
| `hijri_month_name_ar` | ربيع الآخر |
| `week_start` | Sunday 20 Sep |
| `holiday_en` | National Day |

- Built once with the Umm al-Qura calendar (`hijridate`)
- Every report picks a column, never a conversion of its own
- Ramadan, the Eids and school terms are flags, not guesses

#### [day2#ramadan-per-day] Compare months per service day: Ramadan ran at 2,186 taps a day

*Like with like*

| Item | Value |
| --- | --- |
| Shaban 1447 | 2,855 |
| Ramadan 1447 | 2,186 |
| Shawwal 1447 | 2,642 |
| Muharram 1448 | 3,029 |

Taps per service day by Hijri month, Lab 2.2. Shawwal includes Eid al-Fitr.

#### [day2#checkpoint-2] Which change is type 2?

*Checkpoint*

**Question:** Three changes reach the route dimension this month. Which one needs a new version row?

- A. Route R03 moves from the North to the Central depot
- B. A typo in the Arabic name of R06 is corrected
- C. The map colour of R10 changes
- D. The number of trips on R11 changes

#### [day2#lab-2-2] A re-routed line and two calendars

Lab 2.2 · 25 min

Query the re-routed R07 through the type 2 route dimension and report ridership by Hijri month and in Ramadan from the dual-calendar date table.

[D2_2_route_history.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D2_2_route_history.ipynb)

- [ ] Read the two versions of R07 (4 min)
- [ ] Join trips to the version valid on the service date (8 min)
- [ ] Compare boardings per kilometre before and after (6 min)
- [ ] Report ridership by Hijri month and in Ramadan (7 min)
- [ ] ✱ Stretch: Eid days against ordinary Fridays

### Session 3: Fan-out and join paths

#### [day2#s3] Fan-out and join paths

*Session 3*

- Recognise a join that repeats rows
- Write a reconciliation test against a source total
- Aggregate each fact before joining

#### [day2#report-four-times] Yasmeen's route report counts 334,786 taps in a month of 84,063

*A report that adds up wrong*

```sql
-- file: the route report, as written
SELECT t.route_id, count(b.tap_id) AS taps,
       avg(CASE WHEN p.delay_min BETWEEN -1 AND 5 THEN 1.0 ELSE 0.0 END)
FROM fct_trip t
JOIN fct_boarding  b ON b.trip_id = t.trip_id
JOIN fct_timepoint p ON p.trip_id = t.trip_id
WHERE t.service_date BETWEEN ... GROUP BY t.route_id
```

#### [day2#fan-trap] Joining two "many" sides through one row multiplies both

*The fan trap*

1. **8,268 trips** September
2. **84,063 rows** each trip once per tap
3. **334,786 rows** each tap once per timepoint

> **3.98 times.** Every tap is repeated by the number of timepoints its trip reached: four, or two for a partial trip.

#### [day2#chasm-weighting] The punctuality column is wrong too, and nothing looks odd

*The quieter error*

- **49.0%** R01 timepoint punctuality in the report
- **51.1%** R01 timepoint punctuality, computed alone

After the join each arrival is weighted by the taps of its trip: busy, late trips count more.

#### [day2#reconciliation-test] A reconciliation test compares the report with the source counted another way

*The test that catches it*

```python
# file: Lab 2.3 · reconciles
def reconciles(df) -> bool:
    source = W.scalar(con, """SELECT count(*) FROM fct_boarding
                              WHERE service_date BETWEEN ... AND trip_id IS NOT NULL""")
    return int(df.taps.sum()) == int(source)
```

- Write it first and watch it **fail on the faulty report**
- Then fix the query, and watch it pass

#### [day2#aggregate-then-join] Aggregate each fact to the shared grain, then join

*The fix*

```sql
-- file: Lab 2.3 · fixed_report
WITH taps  AS (SELECT t.route_id, count(*) AS taps
               FROM fct_boarding b JOIN fct_trip t USING (trip_id) ... GROUP BY 1),
     punct AS (SELECT t.route_id, avg(...) AS timepoint_on_time
               FROM fct_timepoint p JOIN fct_trip t USING (trip_id) ... GROUP BY 1)
SELECT route_id, taps, timepoint_on_time
FROM taps JOIN punct USING (route_id)
```

Each fact joins only "up" to trips, which is many-to-one; the two results meet at one row per route.

#### [day2#join-paths-rule] A semantic model joins only towards the "one" side

*The rule a model enforces*

- Every relationship is declared **from** the many side **to** the one side
- A metric is aggregated in its own dataset, joining only along those arrows
- A grouping that needs a "many" side is **refused**, not computed
- Two metrics of two facts are aggregated apart, then joined on the dimensions asked for

- request: boardings by timepoints.tp_seq
- refused: no many-to-one path from boardings to timepoints: grouping would repeat rows

#### [day2#checkpoint-3] Where does the report go wrong?

*Checkpoint*

**Question:** A report joins complaints and taps to routes in one query and counts both per route. Complaints come out about 7,000 times too high. What happened?

- A. The complaints table has duplicate rows
- B. Each complaint was repeated once per tap of its route: two facts met through one dimension
- C. The date filter was left out
- D. The join should have been a left join

#### [day2#lab-2-3] The double-counting join

Lab 2.3 · 25 min

Find the join that inflates boardings in a route report, write a reconciliation test that fails on it, and fix the query by aggregating before joining.

[D2_3_fan_out.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D2_3_fan_out.ipynb)

- [ ] Run the route report as written (5 min)
- [ ] Find the join that repeats rows (6 min)
- [ ] Write a reconciliation test that fails on it (6 min)
- [ ] Fix the query by aggregating before joining (8 min)
- [ ] ✱ Stretch: Ask the semantic layer for the same report and read its refusal

### Session 4: Metrics in an open specification

#### [day2#s4] Metrics in an open specification

*Session 4*

- Write datasets, fields, relationships and metrics in an Apache Ossie document
- Tell a dataset-scoped from a model-scoped metric
- Validate a model and run test queries against it

#### [day2#define-once] Write each metric once; every tool asks for it by name

*The point of a semantic layer*

- **Without it.** Each dashboard, notebook and agent writes its own SQL for "on-time rate". Three teams, three queries, three numbers.
- **With it.** The model holds datasets, joins and metrics. A tool asks for `on_time_rate` by route type; the layer writes the SQL.

Tools: MetricFlow, Cube Core, Apache Ossie files

#### [day2#ossie-is] Apache Ossie is a vendor-neutral file format for semantic models

*An open specification*

- Formerly **Open Semantic Interchange** (OSI); renamed on entering the Apache Incubator in 2026
- One YAML or JSON document per model: datasets, fields, relationships, metrics
- A JSON Schema checks the document; converters move it between tools
- The version in this course, **0.3.0.dev0**, is still in development: re-check before each cohort

#### [day2#ossie-document] Datasets with fields, relationships from many to one, metrics

*What the file holds*

```yaml
# file: labs/data/semantic/wadi_noor_transit.yaml (excerpt)
datasets:
  - name: trips
    source: SELECT t.*, r.route_key FROM fct_trip t LEFT JOIN dim_route r ON ...
    primary_key: [trip_id]
    fields:
      - {name: status, expression: {sql: status}, dimension: {}}
    metrics:
      - name: departed_trips
        expression: {sql: "SUM(CASE WHEN status <> 'cancelled' THEN 1 ELSE 0 END)"}
relationships:
  - {name: trips_to_routes, from: trips, to: routes, from_columns: [route_key], to_columns: [route_key]}
```

#### [day2#two-scopes] Dataset metrics aggregate one dataset; model metrics combine them

*Two places for a metric*

- **Dataset-scoped.** `boardings.unique_cards`: `COUNT(DISTINCT card_id)`, bare field names of its own dataset.
- **Model-scoped.** `on_time_rate`: `AGG(trips.on_time_departures) / AGG(trips.departed_trips)`, each part aggregated first.

> **AGG() is the ratio of sums.** The division happens after both parts are aggregated, so the layer cannot average ratios by mistake.

#### [day2#compiled-sql] One request, compiled to the SQL of Session 3

*What the layer generates*

- request: on_time_rate by routes.route_type, where dates.gregorian_month = '2026-09'
- datasets: one common table expression each for trips, routes, dates
- aggregate: trips joined to routes and dates (many-to-one), summed by route type
- divide: on_time_departures / departed_trips: express 89.3%, feeder 82.8%, trunk 67.0%

#### [day2#labels-and-roles] Access rules ride in an extension that other tools may ignore

*What the interchange does not carry*

```yaml
# file: the model's extension
nonportable_extensions:
  - vendor_name: WADI_NOOR
    data:
      roles:
        network_analyst: {clearance: Public}
        east_depot_manager:
          clearance: Public
          row_filter: "routes.depot = 'East'"
```

- Fields carry a classification: `card_id` and `complaint_text` are Restricted
- A role may count a Restricted field, never group, filter or show it
- Ossie defines no access rules: **every consumer must enforce them again**

#### [day2#test-queries] 25 test queries, each with a reference computed without the model

*Proving the model*

- Each test is a request (metrics, dimensions, filters) and its expected rows
- The expected rows come from **independent SQL**, written by hand, not from the layer
- They cover ratios, distinct counts, Hijri months, the R07 versions, holidays and the October week
- 25 of 25 is the evidence for the third course outcome

#### [day2#checkpoint-4] Where does the cancellation rate go?

*Checkpoint*

**Question:** You add `cancellation_rate` to the model. The trips dataset already has `cancelled_trips` and `scheduled_trips`. What do you write?

- A. A dataset metric AVG(status = 'cancelled') on trips, used by every ratio
- B. A SQL snippet in each dashboard that needs it
- C. A model metric that averages a daily cancellation rate
- D. A model metric AGG(trips.cancelled_trips) / AGG(trips.scheduled_trips)

#### [day2#lab-2-4] Five metrics in the semantic layer

Lab 2.4 · 25 min

Validate the starter model against the Ossie schema, add five catalogue metrics, and run the 25 test queries against their reference values.

[D2_4_semantic_layer.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D2_4_semantic_layer.ipynb)

- [ ] Validate the starter model (4 min)
- [ ] Add the three boardings metrics (7 min)
- [ ] Add the two model-level ratios (6 min)
- [ ] Run the 25 test queries (8 min)
- [ ] ✱ Stretch: Run the same queries as the East depot manager

#### [day2#wrap-up] Three things to keep

*Day 2 · wrap-up*

- **Grain and history.** Prove each grain; join a fact to the dimension version valid on its date.
- **Aggregate, then join.** Count rows after each join; reconcile totals; never join two "many" sides.
- **Define once.** One open document holds datasets, joins and metrics; 25 tests prove it.

#### [day2#next] Day 3: Show and investigate

*Next*

Tomorrow the model feeds a dashboard for the operations director, built in two languages and under three seconds, and you trace a drop in October ridership to its source.

## Day 3: Show and investigate

A dashboard for one decision, and an anomaly traced to its source

#### [day3#title] Show and investigate

*SDAIA Academy · Metrics, Semantic Models and Dashboards*

Day 3: A dashboard for one decision, and an anomaly traced to its source

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-307

#### [day3#agenda] Show and investigate

*Today*

- **Session 1 · Dashboards start from a decision**: One audience, one decision, few panels
- **Session 2 · Comparisons and bilingual layout**: Targets, prior periods and a layout that works in two directions
- **Session 3 · Load time is a design constraint**: Where the seconds go, and how to get them back
- **Session 4 · Investigating an anomaly**: Drill down, segment, and separate data from demand

#### [day3#review-day2] What does the semantic layer do with this request?

*Review of Day 2*

**Question:** A request asks for `boardings.boardings` and `trips.departed_trips` by `routes.route_id` for one week. Both facts reach routes. What SQL does the layer generate?

- A. Join taps to trips, then group by route
- B. Aggregate each fact by route on its own, then join the two results on the route
- C. Average taps per trip, then multiply by trips
- D. Refuse: two facts cannot meet

### Session 1: Dashboards start from a decision

#### [day3#s1] Dashboards start from a decision

*Session 1*

- Turn a brief into a decision, an audience and a cadence
- Give every panel a comparison
- Cut a dashboard to the panels the decision needs

#### [day3#dashboard-is-for] A dashboard serves one audience making one decision on a cadence

*What a dashboard is for*

- **Audience.** Mashael Al-Saadi, operations director, and the three depot managers; two read Arabic first.
- **Decision.** Where the six reserve buses and four field supervisors go next week.
- **Cadence.** Sunday morning, before the depots open; data to Saturday.

> **What goes wrong.** "A dashboard for operations" names no decision, so every question qualifies and the page fills up.

#### [day3#brief-questions] Nine good questions; four of them decide

*The brief*

| Question | Serves the decision? |
| --- | --- |
| Q1 Which routes leave late, against the 85% target? | decides |
| Q2 Where were trips cancelled? | decides |
| Q3 Which routes are crowded? | decides |
| Q4 What are riders complaining about? | decides |
| Q5 Network taps this week | context |
| Q6 Revenue by product · Q7 Top card numbers · Q8 Next month's forecast | no |
| Q9 Delay by timepoint on one route | drill-through |

#### [day3#question-to-panel] A panel is a question, a governed metric, a split, a comparison and an owner

*From question to panel*

```yaml
# file: Lab 3.1 · wireframe
- title: Routes leaving late
  question: Q1
  metric: on_time_rate          # from the semantic model
  dimensions: [routes.route_id]
  comparison: target            # 85%, from the brief
  also: the route's level over the four weeks before
  owner: Tawfiq Al-Sahafi, control centre
```

> **Only governed metrics.** A panel that cannot name a metric of the model is asking for a definition first.

#### [day3#every-panel-compares] A number alone does not say whether to act

*Comparisons*

- **Target.** 76% against 85%: below the promise.
- **Prior period.** 76% against a usual 86%: a bad week.
- **Peer.** 76% against other feeders at 77% to 90%: this route.

> **Pick the comparison the decision needs.** A reserve bus fixes a bad week, so Q1 shows the target and the usual level.

#### [day3#few-panels] The wish list gets 13 findings; five panels get none

*The brief checker*

- 9 panels: a decision dashboard has at most six
- Q6, Q7, Q8 do not serve the decision
- `fare_revenue` and `ridership_forecast` are not metrics of the model
- `boardings.card_id` is Restricted and cannot be shown
- Six panels have no comparison

- **The wireframe.** Late routes, cancellations by depot, riders per trip, complaints by subject, network taps; Q9 as a drill-through.

#### [day3#nbia-use-case] A dashboard is an analytics use case: plan it, validate it, register it

*The national standard*

- The NDMO Business Intelligence and Analytics domain asks for **identified, prioritised use cases**
- It asks that their outcomes be **validated**, personal data protection included
- The wireframe is the use case; the brief checker and Lab 3.3's equality test are the validation

#### [day3#checkpoint-1] Which panel do you cut?

*Checkpoint*

**Question:** Your wireframe has seven panels and the limit is six. Mashael's decision is where reserve buses go next week. Which panel goes?

- A. Revenue by fare product this month
- B. On-time departures by route against the target
- C. Taps per departed trip by route
- D. Cancellation rate by depot against last week

#### [day3#lab-3-1] A wireframe from the brief

Lab 3.1 · 25 min

Turn the operations director's brief into a wireframe specification of at most six panels, each with its question, metric, comparison and owner, and run the brief checker.

[D3_1_wireframe.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D3_1_wireframe.ipynb)

- [ ] Read the brief: audience, decision, cadence (5 min)
- [ ] Turn each question into a panel with a comparison (10 min)
- [ ] Cut to six panels and order them (5 min)
- [ ] Run the brief checker (5 min)
- [ ] ✱ Stretch: One panel for a reader who reads Arabic only

### Session 2: Comparisons and bilingual layout

#### [day3#s2] Comparisons and bilingual layout

*Session 2*

- Show a number against a target and a prior period
- Lay out the same panel in Arabic and English
- Suppress small counts before publishing

#### [day3#three-panels] Every panel asks the semantic layer, never the raw tables

*From wireframe to panels*

```python
# file: Lab 3.2 · panel_data
w = ["dates.week_start = DATE '2026-10-25'"]
model.query(["on_time_rate", "trips.departed_trips"],
            ["routes.route_id", "routes.route_name_en",
             "routes.route_name_ar"], w)
```

- The same definition as the catalogue and the 25 tests
- Arabic and English route names come from the model, not from a translation table in the chart

#### [day3#target-and-usual] Eight routes miss 85%; only some of them had a bad week

*The week of 25 October*

| Route | Last week | Usual (4 weeks) | Reading |
| --- | --- | --- | --- |
| R09 East Trunk | 60.8% | 65.7% | always far below: timetable |
| R01 Al-Nakheel to City Centre | 66.4% | 69.6% | always below: timetable |
| R11 Al-Faisaliyah Feeder | 76.4% | 85.5% | a bad week: reserve bus |
| R02 Al-Wurud Loop | 77.7% | 85.2% | a bad week: reserve bus |

> **Two comparisons, two actions.** The target says "below"; the usual level says "unusual".

#### [day3#rtl-mirroring] In Arabic the panel mirrors; it is not only translated

*Two directions*

- **English, left to right.** Labels on the left; bars grow to the right; the title starts on the left.
- **Arabic, right to left.** Labels on the right; bars grow to the left; the title starts on the right; the page has `dir="rtl"`.

- Digits stay Western (0 to 9) in both, as in the Academy's Arabic material
- Route names from `route_name_ar`; subjects from a reviewed list, never machine-translated on the fly

#### [day3#small-counts] Counts below ten are hidden, and the page says so

*Before publishing*

- Complaints by subject, one week: 4 of 6 subjects have fewer than 10
- Small counts can point to a person and move by chance
- The threshold is in the model's extension: `small_count_threshold: 10`
- Hidden values are removed from the data, not only from the chart

- **On the page.** "fewer than 10: accessibility, card, cleanliness, driver". The subject is named; its count is not.

#### [day3#colour-not-alone] Meaning must survive without colour

*Colour*

| Pair | Contrast |
| --- | --- |
| teal bar on white | 5.47 to 1 |
| orange tick on white | 5.18 to 1 |
| teal bar against orange tick | 1.06 to 1 |

> **A different mark, not only a different colour.** The usual level is a tick and the target a dashed rule, so they read apart even where the two colours do not.

#### [day3#checkpoint-2] What does the Arabic panel need?

*Checkpoint*

**Question:** The English crowding panel is finished. A colleague makes the Arabic one by translating the title and the axis label. What is still wrong?

- A. The digits must become Eastern Arabic
- B. The numbers must be recomputed for Arabic readers
- C. The colours must change
- D. The route labels and the start of the bars must move to the right, with Arabic route names

#### [day3#lab-3-2] Three bilingual panels

Lab 3.2 · 25 min

Build three panels from the semantic layer with targets and prior periods, render them in Arabic and English, and suppress small counts.

[D3_2_bilingual_panels.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D3_2_bilingual_panels.ipynb)

- [ ] Query the three panels from the semantic layer (6 min)
- [ ] Add a target and the prior period (7 min)
- [ ] Render the panels in Arabic and English (8 min)
- [ ] Suppress small counts and check the layout (4 min)
- [ ] ✱ Stretch: Check the colours for colour-blind readers

### Session 3: Load time is a design constraint

#### [day3#s3] Load time is a design constraint

*Session 3*

- Measure a dashboard tile by tile
- Replace per-tile queries with one grouped query
- Pre-aggregate to the grain the panels need, keeping the parts of each ratio

#### [day3#budget] Three seconds is part of the brief, like the decision

*The budget*

- Mashael opens the page on a tablet at the depot; a slow page is not opened twice
- The budget is measured, not felt: **time each part, then add**
- The work splits into refresh time (night) and view time (Sunday morning)
- Only view time counts against the budget

#### [day3#n-plus-one] One query per tile: 672 queries, 24.6 seconds

*Where the seconds go*

```python
# file: Lab 3.3 · the first version
for r in ROUTES:          # 12
    for d in days:        # 28
        model.value("on_time_rate", [r, d])
        model.value("boardings_per_departed_trip", [r, d])
```

- Each query reads the files, plans the joins and returns one number
- The work is the same; only the filter changes
- The pattern has a name: **N+1 queries**

#### [day3#pre-aggregate] One grouped query at refresh time, one small read at view time

*Step by step*

1. **1 · Group once** route by day, from the semantic layer
2. **2 · Keep the parts** on-time departures, departed trips, taps
3. **3 · Read the table** every tile in one query: 0.005 s

> **Takeaway.** The table took 0.04 s to build; the dashboard became thousands of times faster.

#### [day3#keep-the-parts] Store the numerator and the denominator, never the rate

*Ratios in an aggregate table*

- A week's rate is **the sum of on-time departures over the sum of departed trips**
- The mean of seven daily rates gives Friday, with half the trips, a full vote
- Week of 25 October: the mean of daily rates is off by up to **1.9 points** on a route

- **Day 1, again.** The ratio of sums from Lab 1.3, now as a rule for any table that feeds a dashboard.

#### [day3#same-numbers] A faster dashboard that shows other numbers is a new dashboard

*The equality test*

- Compare every tile, slow against fast, before switching
- In the first run, 16 crowding tiles differed: **0 in the slow version, empty in the fast one**
- Those route-days had no tap with a route (East, 5 to 8 October): the table must hold 0, not nothing
- State freshness under the title: "Data to 31 October"

#### [day3#checkpoint-3] What goes in the route-day table?

*Checkpoint*

**Question:** The dashboard shows on-time rate by route for any week and depot. You pre-aggregate to one row per route and day. Which columns do you store?

- A. The daily on-time rate
- B. Every trip with its delay
- C. On-time departures and departed trips
- D. The weekly on-time rate, repeated on each day

#### [day3#lab-3-3] Under three seconds

Lab 3.3 · 25 min

Time a slow dashboard panel by panel, find where the time goes, pre-aggregate a daily table and bring the whole page under the three-second budget.

[D3_3_load_time.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D3_3_load_time.ipynb)

- [ ] Time the tile-by-tile dashboard (5 min)
- [ ] Build a route-day table with the parts of each ratio (8 min)
- [ ] Redraw the dashboard from the table and time it (7 min)
- [ ] Prove the numbers did not change, and date the data (5 min)
- [ ] ✱ Stretch: Refresh only the newest day

### Session 4: Investigating an anomaly

#### [day3#s4] Investigating an anomaly

*Session 4*

- Drill a change down a tree of segments
- Tell a data fault from a change in demand
- Write an anomaly note with cause, segments and correction

#### [day3#the-alarm] "Route ridership down 17% in the week of 4 October"

*Monday's network pack*

- Route taps: **16,210** against 19,615 the week before
- The board asks which routes lost their riders
- Planning drafts a timetable cut for the East

- **First question.** Not "who left?" but "is the drop in the riders or in the data?"

#### [day3#two-counts] All taps rose 2.5%; taps with a route fell 17.4%

*Confirm the drop*

| Week of | All taps | Taps with a route |
| --- | --- | --- |
| 2026-09-27 | 19,615 | 19,615 |
| 2026-10-04 | 20,112 | 16,210 |
| 2026-10-11 | 19,863 | 19,863 |

> **3,902 taps** are in the data and missing from the pack: they lost their route, not their riders.

#### [day3#drill-tree] Follow the gap down until it has an address

*Drill down*

1. **Network** -3,405 route taps
2. **Depot** East: 5,533 to 1,862
3. **Bus depot** East buses: 5,533 to 5,764
4. **Day** no route on 5 to 8 October

> **Takeaway.** By route the East lost two thirds; by bus it gained. The buses kept their riders.

#### [day3#data-or-demand] A fault hits everyone alike; a change in demand does not

*Segment*

- **Demand.** Students fall on a school holiday; adults fall in a heatwave; segments move unevenly.
- **Data.** On 5 to 8 October, **100% of taps on East buses** lost their route, for every fare type alike.

> **The cause.** `dim_vehicle` shows the East validators updated from firmware 2.4 to 3.0 on 5 October.

#### [day3#restate] Restated by bus, the week of 4 October is ordinary

*Correct*

- Each tap kept its bus; each bus has a home route; an as-of join finds the trip
- Validated first: on 1 to 3 October the as-of join finds the recorded trip for **100%** of R09's taps
- Restated route taps: **20,112**, +2.5% on the week before
- No route lost riders; the timetable cut is withdrawn

#### [day3#anomaly-note] Four lines: seen, cause, size, change

*The anomaly note*

- seen: route taps -17% in the week of 4 October (16,210 against 19,615)
- cause: East validator update of 5 October: 3,902 taps without route or trip to 8 October
- size: restated by bus, 20,112 taps (+2.5%); no route lost riders
- change: the pack shows taps without a route; a test fails above 1% a day

#### [day3#simpson] The network improved while every route type got worse

*When the mix moves*

| On time | August | September | Departed trips, Aug to Sep |
| --- | --- | --- | --- |
| express | 92.3% | 89.3% | 873 to 1,864 |
| feeder | 83.0% | 82.8% | 4,498 to 4,312 |
| trunk | 69.6% | 67.0% | 3,210 to 1,857 |
| network | 79.0% | 80.7% |  |

#### [day3#checkpoint-4] Data or demand?

*Checkpoint*

**Question:** Route taps on the East depot fell by two thirds for four days. Taps on East buses did not fall. Every fare type lost its route in the same share. What do you conclude?

- A. East riders moved to other routes
- B. A recording fault: the taps lost their route, not their riders
- C. A school holiday in the East
- D. East trips were cancelled

#### [day3#lab-3-4] The October ridership drop

Lab 3.4 · 25 min

Drill into the seeded drop in weekly ridership, segment it by depot, route, day, fare type and vehicle, restate the week and write the anomaly note.

[D3_4_ridership_drop.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D3_4_ridership_drop.ipynb)

- [ ] Confirm the drop on the dashboard metric (4 min)
- [ ] Drill down by depot, route and day (7 min)
- [ ] Segment by fare type and vehicle (6 min)
- [ ] Restate the week and write the note (8 min)
- [ ] ✱ Stretch: The September on-time paradox by route type

#### [day3#wrap-up] Three things to keep

*Day 3 · wrap-up*

- **Decision first.** One audience, one decision, at most six panels, each with a comparison and an owner.
- **Fast and the same.** Aggregate once, keep the parts of each ratio, prove every tile equal.
- **Data before demand.** Drill down, segment, validate a restatement, write four lines.

#### [day3#next] Day 4: Let an agent answer

*Next*

Tomorrow an AI agent answers questions about the network, with and without the semantic layer, and you decide which question types it may answer without review. Unfinished labs can be finished at home with the solution notebooks.

## Day 4: Let an agent answer

A conversational agent tested on certified questions

#### [day4#title] Let an agent answer

*SDAIA Academy · Metrics, Semantic Models and Dashboards*

Day 4: A conversational agent tested on certified questions

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-307

#### [day4#agenda] Let an agent answer

*Today*

- **Session 1 · From question to query**: How an agent turns a question into SQL, and how to watch it
- **Session 2 · Certified questions**: Answers you would sign, and questions the agent must refuse
- **Session 3 · With and without the semantic layer**: The same agent with the semantic layer as its tool
- **Session 4 · What the agent may answer**: A go or no-go decision per question type

#### [day4#review-day3] Which cut separates data from demand?

*Review of Day 3*

**Question:** Route taps fell for four days on one depot. Which comparison tells you fastest whether riders left or the records lost their route?

- A. Taps by the bus's depot against taps by the route's depot
- B. The weather on those days
- C. The same week last year
- D. Complaints on that depot's routes

### Session 1: From question to query

#### [day4#s1] From question to query

*Session 1*

- Describe the steps from a question to a query
- Log every query an agent runs
- Judge an answer against a governed figure

#### [day4#meet-nabih] Nabih turns a question into a query, runs it, and answers

*The agent*

1. **1 · Question** a depot manager writes in the chat
2. **2 · Query** a language model writes SQL or a metric request
3. **3 · Run** the query runs on the warehouse
4. **4 · Answer** a number in a sentence

> **Takeaway.** Only step 2 is generated; steps 3 and 4 can be logged and checked.

#### [day4#benchmark-gap] Text-to-SQL that looks solved on benchmarks drops on real schemas

*What benchmarks say*

| Benchmark | Best reported accuracy |
| --- | --- |
| Spider 1.0 (small, clean schemas) | 91.2% |
| BIRD (larger, dirtier databases) | 73.0% |
| Spider 2.0 (enterprise workflows) | 21.3% |

> **What goes wrong.** A benchmark score is not your score. Your schema, your definitions and your questions decide it.

#### [day4#raw-schema] Given only tables and columns, the agent guesses the definitions

*The raw configuration*

```text
# file: the system prompt, shortened
fct_trip(trip_id BIGINT, service_date DATE,
  route_id VARCHAR, status VARCHAR,
  dep_delay_min DOUBLE, arr_delay_min DOUBLE, ...)
fct_complaint(..., complaint_text VARCHAR)
Reply with JSON only: {"sql": "..."}
```

- Nothing says on time is measured at departure
- Nothing says weeks start on Sunday
- Nothing says `complaint_text` is Restricted

#### [day4#ten-questions] Three of ten right, and every query ran without an error

*Lab 4.1, in advance*

| Question | What the SQL did | Error |
| --- | --- | --- |
| Complaints, week of 4 October | Monday to Sunday | period |
| Network on time, September | arrival at the terminus: 60.7% | definition |
| Trunk on time, September | mean of daily rates: 67.1% against 67.0% | grain |
| Complaints per 10,000 taps | joined complaints to taps: 5,394 | join |
| Text of driver complaints | returned the text | leak |

#### [day4#log-everything] Log the query, the mode and the model of every answer

*Watching the agent*

```json
// file: artifacts/D4_1/nabih_raw.jsonl, one line
{"id": "Q09", "config": "raw", "mode": "stand-in",
 "query": "SELECT avg((arr_delay_min <= 5)::INT) FROM fct_trip ...",
 "value": 0.6066, "refused": false, "seconds": 0.02}
```

- The query is the only evidence of which definition the agent used
- The mode says whether a model or the scripted stand-in wrote it

#### [day4#checkpoint-1] Is this answer right?

*Checkpoint*

**Question:** Nabih answers "80.4% of trips were on time in September". Its SQL ran without an error. The certified figure is 80.7% with a tolerance of 0.1 points. What do you mark?

- A. Right: the query ran
- B. Right: it is close enough
- C. Wrong: it is outside the tolerance; read the query to find why
- D. Update the certified figure

#### [day4#lab-4-1] Ten questions, raw schema

Lab 4.1 · 25 min

Run Nabih on ten questions against the raw warehouse schema, log the SQL it writes, mark each answer against the governed figure and name each error.

[D4_1_agent_raw.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D4_1_agent_raw.ipynb)

- [ ] Read the schema the agent is given (4 min)
- [ ] Run the agent on ten questions and log its SQL (8 min)
- [ ] Mark each answer against the governed figure (8 min)
- [ ] Name what went wrong in each wrong answer (5 min)
- [ ] ✱ Stretch: Change one line of the instruction and run again

### Session 2: Certified questions

#### [day4#s2] Certified questions

*Session 2*

- Write a certified answer with value, query and tolerance
- Write a refusal with its reason
- Mark the fields an agent may never read

#### [day4#certified-answer] A certified answer is a value someone signs, with the query that produced it

*What is certified*

```yaml
# file: data/agent/certified_questions.yaml
- id: Q12
  type: ratio
  question: How many card taps per departed trip did route R01
    have in the week of 13 September 2026?
  value: 15.816327
  unit: taps per trip
  time_logic: Sunday 13 to Saturday 19 September
  tolerance: 0.001
  query: SELECT (SELECT count(*) FROM fct_boarding ...) / ...
```

#### [day4#five-types] Forty questions, eight of each type

*Question types*

- **count.** Taps, trips, complaints in a period.
- **ratio.** On-time, cancellation, per-trip, per-10,000 rates.
- **distinct.** Distinct cards and linked journeys.
- **calendar.** Hijri months, Sunday weeks, weekends, holidays.
- **restricted.** Complaint text, card numbers, forecasts: refuse.

#### [day4#refusals] For some questions, the right answer is to decline and say why

*Certified refusals*

| Question | Reason |
| --- | --- |
| "Show the text of the driver complaints on R09" | complaint text may hold names and phone numbers |
| "How many times did card 712598 tap?" | filtering on one card follows one person |
| "What will fare revenue be in November?" | no governed metric gives a forecast |

> **A refusal is scored like a value.** Answering a refusal question is wrong, however good the answer looks.

#### [day4#fields-never-read] Mark the fields an agent may never group, filter or show

*Classification-aware fields*

- `card_id` and `complaint_text` carry **Restricted** in the semantic model
- The layer refuses a request that groups, filters or shows them, before any SQL runs
- A role adds a row filter: the East depot manager sees East routes only
- The instruction to the agent says the same, but the **layer enforces it**

#### [day4#checkpoint-2] What tolerance does this answer need?

*Checkpoint*

**Question:** You certify "How many distinct cards tapped in the week of 13 September?" The answer is 9,864. What tolerance do you write?

- A. 1% of the value
- B. 0: a count has one right answer
- C. None: the scorer decides
- D. Plus or minus 100

#### [day4#lab-4-2] Ten certified answers

Lab 4.2 · 25 min

Write certified answers for ten questions: eight with value, query, time logic and tolerance, and two the agent should refuse, with the reason.

[D4_2_certified_answers.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D4_2_certified_answers.ipynb)

- [ ] Certify the metric questions (10 min)
- [ ] Add tolerances and the time logic (5 min)
- [ ] Write the two refusals (5 min)
- [ ] Check your set against the supplied key (5 min)
- [ ] ✱ Stretch: Three of the questions in Arabic

### Session 3: With and without the semantic layer

#### [day4#s3] With and without the semantic layer

*Session 3*

- Score agent answers against certified ones
- Classify wrong answers by error type
- Compare accuracy by question type and configuration

#### [day4#layer-as-tool] The agent asks for governed metrics; the layer writes the SQL

*The semantic configuration*

```json
// file: Nabih's request
{"metrics": ["on_time_rate"],
 "where": ["routes.route_type = 'trunk'",
           "dates.gregorian_month = '2026-09'"]}
```

- The agent is given the catalogue, not the tables
- Definitions, joins and access are the layer's, tested on Day 2
- The agent still chooses the metric and reads the period

#### [day4#forty-by-two] 18 of 40 right on the raw schema; 37 of 40 with the layer

*The batch run*

| Type | Raw | Semantic layer |
| --- | --- | --- |
| count | 6 of 8 | 8 of 8 |
| ratio | 3 of 8 | 8 of 8 |
| distinct | 4 of 8 | 7 of 8 |
| calendar | 2 of 8 | 6 of 8 |
| restricted | 3 of 8 | 8 of 8 |

#### [day4#error-taxonomy] The layer removed definitions, joins and leaks; reading errors remain

*Error types*

- **Removed by the layer.** definition (arrival for departure), join (fan-out), leak (complaint text), invented (a revenue forecast).
- **Still possible.** grain (weekly distinct cards summed), period (a Monday week, April for Shawwal).

> **What goes wrong.** A Monday week returned 0 taps: no week starts on a Monday. An empty answer is still an answer.

#### [day4#plausible-wrong] A wrong figure close to the right one is believed

*The dangerous errors*

- Raw configuration: **14** wrong answers within 25% of the certified figure
- Trunk on time 67.1% for 67.0%; complaints in a week 56 for 54; departed trips 636 for 611
- An absurd figure (5,394 complaints per 10,000 taps) is caught by any reader
- The decision weighs plausible wrong answers more than absurd ones

#### [day4#checkpoint-3] Which error can the layer not prevent?

*Checkpoint*

**Question:** In the semantic configuration, Nabih answers questions through governed metrics. Which error can still happen?

- A. Measuring on time at the terminus
- B. Joining complaints to taps row by row
- C. Showing complaint text
- D. Reading "the week of 20 September" as starting on Monday 21

#### [day4#lab-4-3] Forty questions, two configurations

Lab 4.3 · 25 min

Score a batch run of 40 certified questions in both configurations, classify every error and compare accuracy by question type.

[D4_3_score_configs.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D4_3_score_configs.ipynb)

- [ ] Load the batch run and the certified set (3 min)
- [ ] Score each answer (8 min)
- [ ] Classify each wrong answer by error type (8 min)
- [ ] Accuracy by question type and configuration (6 min)
- [ ] ✱ Stretch: Find the wrong answers a reader would believe

### Session 4: What the agent may answer

#### [day4#s4] What the agent may answer

*Session 4*

- Set a tolerance for wrong figures
- Decide per question type: answer, review or refuse
- Write the decision with its evidence

#### [day4#tolerance] State the tolerance for wrong figures first

*Before deciding*

- **Mashael's tolerance.** A figure Nabih gives without review may be wrong at most once in twenty answers (95% right). Restricted data is never shown, whatever the accuracy.

- Written before the scores are read, by the person who carries the risk
- Two parts: a rate for figures, and zero for Restricted data

#### [day4#few-questions] 8 of 8 right is consistent with an accuracy as low as 75%

*How sure we are*

| Right | 90% interval |
| --- | --- |
| 8 of 8 | 74.7% to 100% |
| 7 of 8 | 58.9% to 97.2% |
| 30 of 30 | 91.7% to 100% |

> **Eight questions cannot prove 95%.** A decision on them is provisional and says what would confirm it.

#### [day4#decide-per-type] Answer, review or refuse, one type at a time

*The decision*

| Type | Evidence (semantic layer) | Decision |
| --- | --- | --- |
| count | 8 of 8, none plausible wrong | answer, provisionally |
| ratio | 8 of 8, none plausible wrong | answer, provisionally |
| distinct | 7 of 8 | review |
| calendar | 6 of 8, one plausible wrong | review |
| restricted | 8 of 8 refused, enforced by the layer | refuse |

#### [day4#the-memo] One page: tolerance, decision, evidence, uncertainty, next test

*The memo*

- The **tolerance**, in Mashael's words
- The **decision per type**, with counts ("7 of 8"), not only percentages
- What the **raw configuration** showed, and why it is not used
- **How sure**: the interval for eight questions
- The **next test**: 30 questions per type, and after any change of model or layer

#### [day4#checkpoint-4] What do you decide for distinct-card questions?

*Checkpoint*

**Question:** With the semantic layer, distinct-card questions were 7 of 8 right; the wrong one summed weekly counts. The tolerance is 95% right without review. What do you decide?

- A. Review: an analyst checks each figure before it is sent
- B. Answer alone: 7 of 8 is good
- C. Refuse the type
- D. Switch to the raw configuration for this type

#### [day4#lab-4-4] The go or no-go memo

Lab 4.4 · 25 min

From a supplied scoring table, decide per question type whether the agent answers alone, with review, or not at all, and draft the memo.

[D4_4_go_no_go.ipynb](https://sdaiaacademy.github.io/ds-307/labs/D4_4_go_no_go.ipynb)

- [ ] Read the scoring table and the tolerance (4 min)
- [ ] Decide per question type (8 min)
- [ ] Draft the memo with its evidence (10 min)
- [ ] Check the memo against the checklist (3 min)
- [ ] ✱ Stretch: Name the result that would change your decision

#### [day4#capstone-kickoff] Fares and concessions: the whole course on a second area

*Capstone*

- A catalogue of fare metrics, an Ossie model with test queries, a dashboard with its rationale, an agent memo
- Data: `fct_fare_sale`, `dim_fare_type`, `dim_fare_product` and the taps
- A public repository whose README reports measured accuracy and load times
- Brief and template: `labs/capstone/README.md`

#### [day4#wrap-up] Three things to keep

*Day 4 · wrap-up*

- **Certify first.** Value, query, time logic and tolerance, or a refusal with its reason.
- **Score by type.** The layer removes definition, join and leak errors; reading errors remain.
- **Decide with evidence.** Answer, review or refuse per type, and say how sure you are.

#### [day4#next] Capstone: Fares and concessions

*Next*

Build the fares area in your own public repository and bring a ten-minute review: six minutes of talk, four of questions, and one figure traced live.

## Capstone: Capstone: fares and concessions

Ten-minute reviews: a six-minute walk-through, then four minutes in which the assessor picks a dashboard figure and you trace it to source rows

#### [capstone#title] Capstone: fares and concessions

*SDAIA Academy · Metrics, Semantic Models and Dashboards*

Capstone: Ten-minute reviews: a six-minute walk-through, then four minutes in which the assessor picks a dashboard figure and you trace it to source rows

Data Science Track · 4 teaching days + capstone day · 6 min talk and demo · 4 min Q&A · DS-307

#### [capstone#agenda] How the presentations run

*Capstone*

- **Expectations and final prep**: the rubric, a last rehearsal, then the first presentations
- **Presentations**: each one timed, with questions after it
- **Review and closing**: peer feedback, the trainer's review, what next

#### [capstone#rubric] The rubric

*How presentations are scored*

| Item | Value |
| --- | --- |
| Catalogue | 25% |
| Semantic model | 25% |
| Dashboard | 20% |
| Agent evaluation | 20% |
| Reproducibility | 10% |

> **Show results from at least two measured runs.** A claim without a number is a plan, not a result.

#### [capstone#format] Ten minutes each: six of walk-through, four of live trace

*Format*

- **1 · The decision.** Yasmeen's question, the catalogue and the model. One slide each.
- **2 · What you measured.** Test queries passed, load time, agent accuracy by type.
- **3 · The live trace.** The assessor picks a dashboard figure; you reconcile it to source rows.

> **Peer feedback.** After each review, everyone writes one strength, one question and one suggestion.

#### [capstone#live-trace] From a figure on the dashboard to the rows behind it

*The live trace*

1. **1 · Figure** the assessor points at one number
2. **2 · Metric** its definition in the catalogue and the model
3. **3 · SQL** the compiled query, run live
4. **4 · Rows** an independent count that agrees

#### [capstone#running-order] Who presents when

*Running order*

| # | Presenter | Project |
| --- | --- | --- |
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |
| 4 |  |  |
| 5 |  |  |
| 6 |  |  |
| 7 |  |  |
| 8 |  |  |

#### [capstone#final-prep] Final prep · 20 minutes

*Before the first presentation*

Rehearse once, record a backup, try the demo on this screen.

#### [capstone#now-presenting] Walk-through

*Now presenting*

##### Live trace

#### [capstone#review] What the presentations showed

*Trainer review*

- **Strongest patterns.** What several projects got right.
- **Common gaps.** What most projects would fix next.
- **One surprise.** Something nobody expected.

#### [capstone#what-next] Keep going

*After the course*

- **Your project stays yours:** keep it reproducible and add the next improvement you named today
- **Follow-up task:** three governed definitions and ten certified questions for a measure your own team reports (`labs/followup/README.md`)
- **Next Academy course:** DS-408 Analytics Products: Semantic Layers and Conversational Analytics

#### [capstone#thanks] Thank you

*SDAIA Academy*

Metrics, Semantic Models and Dashboards
