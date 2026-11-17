---
course: "Metrics, Semantic Models and Dashboards"
code: "DS-307"
version: "2027.1.0"
deck: "day1"
day: 1
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-307/slides/day1.html"
---

# Metrics, Semantic Models and Dashboards

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
