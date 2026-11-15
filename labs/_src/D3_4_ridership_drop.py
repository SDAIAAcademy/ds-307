# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0", "jsonschema>=4.23"]
# ///
# %% [markdown]
# # Lab 3.4 · The October ridership drop
#
# Day 3 · Session 4 (Investigating an anomaly) · 25 min. Monday's network pack shows route ridership down 17% in the
# week of 4 October, and the board asks which routes lost their riders. You confirm the drop, drill down until it has
# an address, segment it, find the cause, restate the week and write a four-line anomaly note.
#
# **AI-tutor.** An assistant may suggest the next cut; the conclusion and the note are yours.
#
# **Reference state.** The warehouse in `data/warehouse/` and the semantic model `data/semantic/wadi_noor_transit.yaml`.
#
# **Tasks**
# - [ ] 1 · Confirm the drop on the dashboard metric (4')
# - [ ] 2 · Drill down by depot, route and day (7')
# - [ ] 3 · Segment by fare type and vehicle (6')
# - [ ] 4 · Restate the week and write the note (8')
# - [ ] ✱ Stretch · The September on-time paradox by route type

# %%
import os, sys, subprocess
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    REPO_URL = "https://github.com/SDAIAAcademy/ds-307.git"
    if not Path("/content/ds-307").exists():
        subprocess.run(["git", "clone", "-q", REPO_URL, "/content/ds-307"], check=True)
    os.chdir("/content/ds-307/labs")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-colab.txt"], check=True)
else:
    while not Path("wnt.py").exists() and Path.cwd() != Path.cwd().parent:
        os.chdir("..")  # solutions/ notebooks run from labs/
sys.path.insert(0, os.getcwd())

import pandas as pd
import wnt as W
import wnt_semantic as S
con = W.db()
model = S.Model(S.load("data/semantic/wadi_noor_transit.yaml"), con)
OUT = W.lab_dir("D3_4")
WEEKS = ["dates.week_start BETWEEN DATE '2026-09-06' AND DATE '2026-10-25'"]

# %% [markdown]
# ## 1 · Confirm the drop on the dashboard metric (4')
#
# The pack counts taps **with a route** (it groups by route). The governed metric `boardings.boardings` counts every
# tap. Put the two side by side, week by week.
#
# ✏️ **Exercise** · Return a frame with `week_start`, `taps` (all taps) and `route_taps` (taps with a route), from the
# semantic layer.

# %%
def weekly():
    # BEGIN SOLUTION
    allt = model.query(["boardings.boardings"], ["dates.week_start"], WEEKS).rename(columns={"boardings": "taps"})
    rt = model.query(["boardings.boardings"], ["dates.week_start"], WEEKS + ["routes.route_id IS NOT NULL"]).rename(
        columns={"boardings": "route_taps"})
    return allt.merge(rt, on="week_start")
    # END SOLUTION


# %%
try:
    wk = weekly()
except NotImplementedError:
    wk = pd.DataFrame(W.reference("d3_4_weekly"))
wk["week_start"] = pd.to_datetime(wk.week_start).dt.strftime("%Y-%m-%d")
wk["route_change"] = wk.route_taps.pct_change()
wk["all_change"] = wk.taps.pct_change()
W.show(wk.round(3))
oct4 = wk.set_index("week_start").loc["2026-10-04"]
W.check(round(oct4.route_change, 2) == -0.17, f"the pack's figure: route taps {W.pct(oct4.route_change)} in the week of 4 October")
W.check(oct4.all_change > 0, f"all taps: {W.pct(oct4.all_change)}; the riders did not leave")

# %% [markdown]
# 🔍 Two counts of the same week disagree by 3,900 taps. Before asking "who left?", ask "which taps lost their route?"
#
# ## 2 · Drill down by depot, route and day (7')
#
# ✏️ **Exercise** · Count the taps of the week before and the week of 4 October by the **route's** depot, then by the
# **bus's** depot (`vehicles.depot`). A tap without a route has no route depot, but its bus still has one.

# %%
def by_depot():
    span = ["dates.week_start IN (DATE '2026-09-27', DATE '2026-10-04')"]
    # BEGIN SOLUTION
    route = model.query(["boardings.boardings"], ["routes.depot", "dates.week_start"], span)
    bus = model.query(["boardings.boardings"], ["vehicles.depot", "dates.week_start"], span)
    route = route.pivot(index="depot", columns="week_start", values="boardings").fillna(0)
    bus = bus.pivot(index="depot", columns="week_start", values="boardings")
    route.index = route.index.fillna("(no route)")
    return route, bus
    # END SOLUTION


# %%
try:
    route_dep, bus_dep = by_depot()
    route_dep.columns = bus_dep.columns = ["week_before", "week_of_4_october"]
except NotImplementedError:
    route_dep = pd.DataFrame(W.reference("d3_4_by_depot")).set_index("depot")
    bus_dep = None
print("by the route's depot:"); W.show(route_dep.reset_index())
if bus_dep is not None:
    print("\nby the bus's depot:"); W.show(bus_dep.reset_index())
    W.check(bus_dep.loc["East", "week_of_4_october"] > 0.95 * bus_dep.loc["East", "week_before"],
            "East buses carried as many taps as the week before")
W.check(route_dep.loc["East", "week_of_4_october"] < 0.5 * route_dep.loc["East", "week_before"],
        "by route, the East depot lost two thirds of its taps")

# %% [markdown]
# The East routes, one by one, and then by day for East buses only: the taps, and how many of them have a route.

# %%
W.show(model.query(["boardings.boardings"], ["routes.route_id", "dates.week_start"],
                   ["dates.week_start IN (DATE '2026-09-27', DATE '2026-10-04')", "routes.depot = 'East'"])
       .pivot(index="route_id", columns="week_start", values="boardings").reset_index())
days = W.df(con, """SELECT b.service_date AS day, count(*) AS east_bus_taps, count(b.route_id) AS with_route
                    FROM fct_boarding b JOIN dim_vehicle v USING (vehicle_id)
                    WHERE v.depot = 'East' AND b.service_date BETWEEN DATE '2026-10-01' AND DATE '2026-10-10'
                    GROUP BY 1 ORDER BY 1""")
W.show(days)
gap_days = days.loc[days.with_route == 0, "day"].astype(str).tolist()
W.check(gap_days == ["2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08"], f"no route on {gap_days[0]} to {gap_days[-1]}")

# %% [markdown]
# ## 3 · Segment by fare type and vehicle (6')
#
# A real loss of riders hits some groups more than others (students on a school holiday, for example). A recording
# fault hits everyone on the affected equipment alike.
#
# ✏️ **Exercise** · Compute, for the four days, the share of East-bus taps without a route by fare type, and list the
# validator firmware of the East buses.

# %%
def segments():
    # BEGIN SOLUTION
    fare = W.df(con, """SELECT b.fare_type, avg((b.route_id IS NULL)::INT) AS share_without_route, count(*) AS taps
                        FROM fct_boarding b JOIN dim_vehicle v USING (vehicle_id)
                        WHERE v.depot = 'East' AND b.service_date BETWEEN DATE '2026-10-05' AND DATE '2026-10-08'
                        GROUP BY 1 ORDER BY 1""")
    firmware = W.df(con, "SELECT depot, validator_firmware, count(*) AS buses FROM dim_vehicle GROUP BY ALL ORDER BY 1")
    return fare, firmware
    # END SOLUTION


# %%
try:
    fare, firmware = segments()
except NotImplementedError:
    fare, firmware = None, W.df(con, "SELECT depot, validator_firmware, count(*) AS buses FROM dim_vehicle GROUP BY ALL ORDER BY 1")
if fare is not None:
    W.show(fare)
    W.check(fare.share_without_route.min() == 1.0, "every fare type lost its route alike: a recording fault, not a rider change")
W.show(firmware)
W.check(firmware.query("depot == 'East'").validator_firmware.str.contains("5 October").all(),
        "the East validators were updated on 5 October")

# %% [markdown]
# ## 4 · Restate the week and write the note (8')
#
# The taps kept their bus. Each bus has a home route (`dim_vehicle.home_route`); an as-of join on the bus and the tap
# time finds the trip the bus was running. Validate the as-of join on days where the trip is known before trusting it.
#
# ✏️ **Exercise** · Restate the route of the taps without one, and count route taps per week again.

# %%
ASOF = """SELECT b.tap_id, b.trip_id AS recorded_trip, t.trip_id AS found_trip, t.route_id AS found_route
          FROM fct_boarding b ASOF JOIN fct_trip t ON b.vehicle_id = t.vehicle_id AND b.tap_ts >= t.sched_departure
          WHERE b.service_date BETWEEN DATE '{a}' AND DATE '{b}' AND b.vehicle_id LIKE 'V-R09%'"""
check = W.df(con, ASOF.format(a="2026-10-01", b="2026-10-03"))
hit = (check.recorded_trip == check.found_trip).mean()
W.check(hit > 0.9, f"on 1 to 3 October the as-of join finds the recorded trip for {W.pct(hit)} of R09's taps")


def restated():
    # BEGIN SOLUTION
    return W.df(con, """SELECT d.week_start, count(coalesce(b.route_id, v.home_route)) AS restated_route_taps
                        FROM fct_boarding b JOIN dim_vehicle v USING (vehicle_id) JOIN dim_date d ON d.date = b.service_date
                        WHERE d.week_start BETWEEN DATE '2026-09-06' AND DATE '2026-10-25' GROUP BY 1 ORDER BY 1""")
    # END SOLUTION


# %%
try:
    rs = restated()
except NotImplementedError:
    rs = pd.DataFrame(W.reference("d3_4_restated"))
rs["week_start"] = pd.to_datetime(rs.week_start).dt.strftime("%Y-%m-%d")
rs["change"] = rs.restated_route_taps.pct_change()
W.show(rs.round(3))
W.check(abs(rs.set_index("week_start").loc["2026-10-04", "change"]) < 0.05, "restated, the week of 4 October is an ordinary week")

# %% [markdown]
# ✏️ **Exercise** · Write the note: what was seen, the cause, the size, what changes. Four lines; no blame.

# %%
def anomaly_note() -> str:
    # BEGIN SOLUTION
    return (
        "Seen: route taps fell 17% in the week of 4 October (16,210 against 19,615).\n"
        "Cause: the East depot validator update of 5 October wrote 3,902 taps without route or trip until 8 October; "
        "the buses, cards and fares are intact.\n"
        "Size: restated by bus, the week had 20,112 taps (+2.5%); no route lost riders.\n"
        "Change: the pack shows taps without a route as their own line; data platform adds a test that fails when "
        "more than 1% of a day's taps have no route."
    )
    # END SOLUTION


try:
    note = anomaly_note()
except NotImplementedError:
    note = ""
(OUT / "anomaly_note.md").write_text(note + "\n", encoding="utf-8")
W.check(len(note.splitlines()) == 4, "the note has four lines")
W.check(any(ch.isdigit() for ch in note), "the note gives the size in numbers")

# %% [markdown]
# ## ✱ Stretch · The September on-time paradox by route type
#
# The network on-time rate rose from August to September, while every route type got worse. Show it with the semantic
# layer, and say what changed in the mix.

# %%
mix = model.query(["on_time_rate", "trips.departed_trips"], ["routes.route_type", "dates.gregorian_month"],
                  ["dates.gregorian_month IN ('2026-08', '2026-09')"])
W.show(mix.pivot(index="route_type", columns="gregorian_month", values=["on_time_rate", "departed_trips"]).round(3).reset_index())
print(model.query(["on_time_rate"], ["dates.gregorian_month"], ["dates.gregorian_month IN ('2026-08', '2026-09')"]).round(3))

# %% [markdown]
# ## Checkpoint
#
# 1. Why compare the bus's depot with the route's depot?
#    <details><summary>Answer</summary>The bus kept its depot when the tap lost its route; if riders had left, both
#    counts would fall.</details>
# 2. Every fare type lost its route in the same proportion. What does that rule out?
#    <details><summary>Answer</summary>A change in rider behaviour, which hits groups unevenly (students on a holiday,
#    for example); equal loss points at the equipment.</details>
# 3. Why validate the as-of join on days when the trip is recorded?
#    <details><summary>Answer</summary>A restatement is a model of the missing data; it is trusted only after it
#    reproduces data you already have.</details>
#
# **Carry forward.** Day 4 puts an AI agent on top of the semantic layer: it must not repeat the pack's mistake.
