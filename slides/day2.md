---
course: "Metrics, Semantic Models and Dashboards"
code: "DS-307"
version: "2027.1.0"
deck: "day2"
day: 2
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-307/slides/day2.html"
---

# Metrics, Semantic Models and Dashboards

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
