# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0", "jsonschema>=4.23"]
# ///
# %% [markdown]
# # Lab 3.3 · Under three seconds
#
# Day 3 · Session 3 (Load time is a design constraint) · 25 min. The first version of the operations dashboard draws a grid of
# tiles, one per route and day for the last four weeks, and sends one query per tile. Mashael's brief allows three
# seconds. You time it, find where the time goes, build a route-day table that keeps the parts of each ratio, and show
# that the fast dashboard gives the same numbers.
#
# **AI-tutor.** An assistant may explain a DuckDB plan; the timings and the equality test are yours.
#
# **Reference state.** The semantic model `data/semantic/wadi_noor_transit.yaml` and the reference route-day table
# `data/reference/d3_3_route_day.json`.
#
# **Tasks**
# - [ ] 1 · Time the tile-by-tile dashboard (5')
# - [ ] 2 · Build a route-day table with the parts of each ratio (8')
# - [ ] 3 · Redraw the dashboard from the table and time it (7')
# - [ ] 4 · Prove the numbers did not change, and date the data (5')
# - [ ] ✱ Stretch · Refresh only the newest day

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

import json
import pandas as pd
import wnt as W
import wnt_semantic as S
con = W.db()
model = S.Model(S.load("data/semantic/wadi_noor_transit.yaml"), con)
BUDGET = W.yaml_load("data/dashboard/brief.yaml")["load_time_budget_seconds"]
DAYS = pd.date_range("2026-10-04", "2026-10-31").strftime("%Y-%m-%d").tolist()
DAYS = W.pick(DAYS, DAYS[-7:])           # quick mode (WNT_QUICK=1): the last week only
ROUTES = sorted(model.query(["trips.scheduled_trips"], ["routes.route_id"]).route_id)
OUT = W.lab_dir("D3_3")
print(len(ROUTES), "routes x", len(DAYS), "days =", len(ROUTES) * len(DAYS), "tiles; budget", BUDGET, "s")

# %% [markdown]
# ## 1 · Time the tile-by-tile dashboard (5')
#
# This is the first version, as it was handed over. Each tile asks the semantic layer for one route and one day.

# %%
def slow_dashboard(days):
    tiles = []
    for r in ROUTES:
        for d in days:
            w = [f"routes.route_id = '{r}'", f"dates.date = DATE '{d}'"]
            tiles.append({"route_id": r, "date": d, "on_time_rate": model.value("on_time_rate", w),
                          "boardings_per_departed_trip": model.value("boardings_per_departed_trip", w)})
    return pd.DataFrame(tiles)


slow, t_slow = W.timed(slow_dashboard, DAYS)
print(f"tile by tile: {t_slow:.1f} s for {2 * len(slow)} queries")
W.check(t_slow > BUDGET, f"the first version misses the {BUDGET}-second budget")

# %% [markdown]
# 🔍 Each query reads the parquet files again, plans the joins again and returns one number. The work is the same for
# every tile; only the filter changes. That is the N+1 pattern.
#
# ## 2 · Build a route-day table with the parts of each ratio (8')
#
# One query, grouped by route and day. Keep the **numerator and denominator** of each ratio, never the ratio itself:
# a week's rate is the sum of on-time departures over the sum of departed trips, not the mean of seven daily rates.
#
# ✏️ **Exercise** · Create the table `route_day` in DuckDB with `route_id`, `date`, `departed_trips`,
# `on_time_departures` and `boardings`, from the semantic layer (`model.compile()` gives the SQL). A route-day
# with no tap must hold 0 taps, not an empty value: the tile-by-tile version says 0.

# %%
def build_route_day(days):
    where = [f"dates.date BETWEEN DATE '{days[0]}' AND DATE '{days[-1]}'", "routes.route_id IS NOT NULL"]
    # BEGIN SOLUTION
    sql = model.compile(["trips.departed_trips", "trips.on_time_departures", "boardings.boardings"],
                        ["routes.route_id", "dates.date"], where)
    con.execute(f"""CREATE OR REPLACE TABLE route_day AS SELECT route_id, date, departed_trips, on_time_departures,
                    coalesce(boardings, 0) AS boardings FROM ({sql})""")
    # END SOLUTION
    return con.sql("SELECT * FROM route_day").df()


# %%
try:
    route_day, t_build = W.timed(build_route_day, DAYS)
except NotImplementedError:
    ref = pd.DataFrame(W.reference("d3_3_route_day"))
    ref = ref[ref.date.isin(DAYS)]
    con.register("ref_route_day", ref)
    con.execute("CREATE OR REPLACE TABLE route_day AS SELECT route_id, date::DATE AS date, departed_trips, "
                "on_time_departures, boardings FROM ref_route_day")
    route_day, t_build = con.sql("SELECT * FROM route_day").df(), float("nan")
print(f"route_day: {len(route_day)} rows, built in {t_build:.2f} s")
W.check(len(route_day) == len(ROUTES) * len(DAYS), "one row per route and day")
W.check({"departed_trips", "on_time_departures", "boardings"} <= set(route_day.columns), "the parts of both ratios are kept")

# %% [markdown]
# ## 3 · Redraw the dashboard from the table and time it (7')
#
# ✏️ **Exercise** · Compute every tile from `route_day` in **one** query.

# %%
def fast_dashboard():
    # BEGIN SOLUTION
    return con.sql("""SELECT route_id, strftime(date, '%Y-%m-%d') AS date,
                             on_time_departures / departed_trips AS on_time_rate,
                             boardings / departed_trips AS boardings_per_departed_trip
                      FROM route_day ORDER BY route_id, date""").df()
    # END SOLUTION


# %%
try:
    fast, t_fast = W.timed(fast_dashboard, repeat=3)
except NotImplementedError:
    fast, t_fast = slow, t_slow
total = t_build + t_fast if t_build == t_build else t_fast
print(f"from the table: {t_fast:.3f} s (plus {t_build:.2f} s to build the table once, at refresh time)")
W.check(t_fast < BUDGET, f"the dashboard loads in {t_fast:.3f} s, under the {BUDGET}-second budget")
W.check(t_slow / max(t_fast, 1e-6) >= 5, f"{t_slow / max(t_fast, 1e-6):.0f} times faster than tile by tile")
(OUT / "timings.json").write_text(json.dumps({"tiles": len(slow), "tile_by_tile_s": round(t_slow, 3),
                                             "build_table_s": round(t_build, 3) if t_build == t_build else None,
                                             "from_table_s": round(t_fast, 4)}, indent=1) + "\n", encoding="utf-8")

# %% [markdown]
# ## 4 · Prove the numbers did not change, and date the data (5')
#
# A faster dashboard that shows different numbers is a new dashboard. Compare tile by tile, then compare a weekly
# rate re-aggregated from the parts with the semantic layer's own weekly rate, and with the mean of the daily rates.
#
# ✏️ **Exercise** · Write `weekly_from_parts()` to return the on-time rate of each route for the week of 25 October
# from `route_day`.

# %%
both = slow.merge(fast, on=["route_id", "date"], suffixes=("_slow", "_fast"))


def same(a, b):   # equal, or empty in both (a route-day with no tap with a route)
    return (pd.isna(a) and pd.isna(b)) or (not pd.isna(a) and not pd.isna(b) and W.close(a, b))


W.check(all(same(a, b) for a, b in zip(both.on_time_rate_slow, both.on_time_rate_fast)), "every on-time tile is equal")
W.check(all(same(a, b) for a, b in zip(both.boardings_per_departed_trip_slow, both.boardings_per_departed_trip_fast)),
        "every crowding tile is equal")
zero = both[both.boardings_per_departed_trip_slow == 0]
print(f"{len(zero)} route-days with no tap with a route:", ", ".join(sorted(set(zero.route_id))) or "none",
      "(the East validator fault of Lab 3.4)")


def weekly_from_parts():
    # BEGIN SOLUTION
    return con.sql("""SELECT route_id, sum(on_time_departures) / sum(departed_trips) AS on_time_rate
                      FROM route_day WHERE date BETWEEN DATE '2026-10-25' AND DATE '2026-10-31'
                      GROUP BY 1 ORDER BY 1""").df()
    # END SOLUTION


try:
    wk = weekly_from_parts()
except NotImplementedError:
    wk = model.query(["on_time_rate"], ["routes.route_id"], ["dates.week_start = DATE '2026-10-25'"])
gov = model.query(["on_time_rate"], ["routes.route_id"], ["dates.week_start = DATE '2026-10-25'"])
mean_daily = con.sql("""SELECT route_id, avg(on_time_departures / departed_trips) AS mean_of_days FROM route_day
                        WHERE date BETWEEN DATE '2026-10-25' AND DATE '2026-10-31' GROUP BY 1 ORDER BY 1""").df()
cmp = gov.merge(wk, on="route_id", suffixes=("_model", "_parts")).merge(mean_daily, on="route_id")
W.show(cmp.round(4))
W.check(all(W.close(a, b) for a, b in zip(cmp.on_time_rate_model, cmp.on_time_rate_parts)),
        "the rate from the parts equals the governed weekly rate")
gap = (cmp.mean_of_days - cmp.on_time_rate_model).abs().max()
print(f"the mean of daily rates is off by up to {100 * gap:.1f} points: Fridays have half the trips but a full vote")

latest = W.scalar(con, "SELECT max(date) FROM route_day")
print("Data to", latest, "· refreshed nightly after the control-centre export")

# %% [markdown]
# A dashboard states how fresh it is. "Data to 31 October" under the title tells Mashael that Saturday's trips are in.
#
# ## ✱ Stretch · Refresh only the newest day
#
# Rebuild only the rows of the last day (delete them, insert them again from the semantic layer) and time it against
# the full build.

# %%
def refresh_last_day():
    d = DAYS[-1]
    con.execute(f"DELETE FROM route_day WHERE date = DATE '{d}'")
    sql = model.compile(["trips.departed_trips", "trips.on_time_departures", "boardings.boardings"],
                        ["routes.route_id", "dates.date"], [f"dates.date = DATE '{d}'", "routes.route_id IS NOT NULL"])
    con.execute(f"INSERT INTO route_day BY NAME {sql}")


_, t_inc = W.timed(refresh_last_day)
print(f"refresh of one day: {t_inc:.2f} s")
W.check(W.scalar(con, "SELECT count(*) FROM route_day") == len(ROUTES) * len(DAYS), "the table has the same rows after the refresh")

# %% [markdown]
# ## Checkpoint
#
# 1. Why store `on_time_departures` and `departed_trips` instead of the daily on-time rate?
#    <details><summary>Answer</summary>A rate cannot be added or averaged across days; the parts can, so any week or
#    depot is re-aggregated exactly.</details>
# 2. The fast dashboard is 50 times faster but a tile differs from the slow one. Ship it?
#    <details><summary>Answer</summary>No. Find the difference first: a faster wrong number is worse than a slow right
#    one.</details>
# 3. What does "Data to 31 October" protect against?
#    <details><summary>Answer</summary>A reader taking a stale or half-loaded day for a real drop.</details>
#
# **Carry forward.** Lab 3.4 investigates a drop that is in the data, not in the dashboard.
