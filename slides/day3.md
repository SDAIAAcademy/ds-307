---
course: "Metrics, Semantic Models and Dashboards"
code: "DS-307"
version: "2027.1.0"
deck: "day3"
day: 3
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-307/slides/day3.html"
---

# Metrics, Semantic Models and Dashboards

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
