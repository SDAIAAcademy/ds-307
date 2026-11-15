# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0", "jsonschema>=4.23"]
# ///
# %% [markdown]
# # Lab 2.3 · The double-counting join
#
# Day 2 · Session 3 (Fan-out and join paths) · 25 min. Yasmeen's September route report puts card taps beside
# timepoint punctuality in one query. Its taps add up to about four times the network's. You find the join that repeats
# rows, write a reconciliation test that fails on it, and fix the query by aggregating each fact before joining.
#
# **AI-tutor.** An assistant may explain an error; the diagnosis is yours.
#
# **Reference state.** The warehouse through `W.db()`.
#
# **Tasks**
# - [ ] 1 · Run the route report as written (5')
# - [ ] 2 · Find the join that repeats rows (6')
# - [ ] 3 · Write a reconciliation test that fails on it (6')
# - [ ] 4 · Fix the query by aggregating before joining (8')
# - [ ] ✱ Stretch · Ask the semantic layer for the same report and read its refusal

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

import wnt as W
con = W.db()
SEP = "BETWEEN DATE '2026-09-01' AND DATE '2026-09-30'"

# %% [markdown]
# ## 1 · Run the route report as written (5')

# %%
REPORT = f"""
SELECT t.route_id, count(b.tap_id) AS taps,
       avg(CASE WHEN p.delay_min BETWEEN -1 AND 5 THEN 1.0 ELSE 0.0 END) AS timepoint_on_time
FROM fct_trip t
JOIN fct_boarding b ON b.trip_id = t.trip_id
JOIN fct_timepoint p ON p.trip_id = t.trip_id
WHERE t.service_date {SEP} AND p.delay_min IS NOT NULL
GROUP BY t.route_id ORDER BY t.route_id"""
report = W.df(con, REPORT)
W.show(report)
print(f"report total taps: {int(report.taps.sum()):,}")

# %% [markdown]
# ## 2 · Find the join that repeats rows (6')
#
# Count the rows after each join, starting from the trips of September. A join that keeps the row count goes to the
# "one" side; a join that multiplies it goes to a "many" side.
#
# ✏️ **Exercise** · Return the row counts of: the September trips; trips joined to taps; that joined to timepoints.

# %%
def row_counts(con) -> dict:
    # BEGIN SOLUTION
    return {
        "trips": W.scalar(con, f"SELECT count(*) FROM fct_trip WHERE service_date {SEP}"),
        "trips x taps": W.scalar(con, f"SELECT count(*) FROM fct_trip t JOIN fct_boarding b ON b.trip_id = t.trip_id WHERE t.service_date {SEP}"),
        "trips x taps x timepoints": W.scalar(con, f"""SELECT count(*) FROM fct_trip t JOIN fct_boarding b ON b.trip_id = t.trip_id
                                                       JOIN fct_timepoint p ON p.trip_id = t.trip_id
                                                       WHERE t.service_date {SEP} AND p.delay_min IS NOT NULL"""),
    }
    # END SOLUTION


# %%
try:
    rc = row_counts(con)
except NotImplementedError:
    rc = W.reference("d2_3_rowcounts")
for k, v in rc.items():
    print(f"{k:28s} {v:>10,}")
ratio = rc["trips x taps x timepoints"] / rc["trips x taps"]
W.check(ratio > 3, f"the timepoint join repeats each tap {ratio:.2f} times on average: a fan-out")

# %% [markdown]
# 🔍 Why 3.98 and not exactly 4? (Partial trips reached only two timepoints.) And the punctuality column: is it still
# a share of timepoint arrivals? (No: each arrival is now weighted by the taps of its trip. Two facts met through
# trips: a chasm trap.)
#
# ## 3 · Write a reconciliation test that fails on it (6')
#
# ✏️ **Exercise** · `reconciles(df)` returns True when the taps of a route report add up to the September taps that
# have a trip, counted directly in `fct_boarding`.

# %%
def reconciles(df) -> bool:
    # BEGIN SOLUTION
    source = W.scalar(con, f"SELECT count(*) FROM fct_boarding WHERE service_date {SEP} AND trip_id IS NOT NULL")
    return int(df.taps.sum()) == int(source)
    # END SOLUTION


# %%
try:
    failed = not reconciles(report)
except NotImplementedError:
    failed = True
W.check(failed, "the test fails on Yasmeen's report, as it should")

# %% [markdown]
# ## 4 · Fix the query by aggregating before joining (8')
#
# ✏️ **Exercise** · Aggregate taps per route and timepoint punctuality per route separately, then join the two
# results on `route_id`.

# %%
def fixed_report() -> str:
    # BEGIN SOLUTION
    return f"""
    WITH taps AS (SELECT t.route_id, count(*) AS taps
                  FROM fct_boarding b JOIN fct_trip t ON t.trip_id = b.trip_id
                  WHERE t.service_date {SEP} GROUP BY 1),
         punct AS (SELECT t.route_id, avg(CASE WHEN p.delay_min BETWEEN -1 AND 5 THEN 1.0 ELSE 0.0 END) AS timepoint_on_time
                   FROM fct_timepoint p JOIN fct_trip t ON t.trip_id = p.trip_id
                   WHERE t.service_date {SEP} AND p.delay_min IS NOT NULL GROUP BY 1)
    SELECT route_id, taps, timepoint_on_time FROM taps JOIN punct USING (route_id) ORDER BY route_id"""
    # END SOLUTION


# %%
try:
    fixed = W.df(con, fixed_report())
except NotImplementedError:
    import pandas as pd
    fixed = pd.DataFrame(W.reference("d2_3_fixed"))
both = report.merge(fixed, on="route_id", suffixes=("_report", "_fixed"))
both["inflation"] = both.taps_report / both.taps_fixed
W.show(both)
try:
    ok = reconciles(fixed)
except NotImplementedError:
    ok = int(fixed.taps.sum()) == W.scalar(con, f"SELECT count(*) FROM fct_boarding WHERE service_date {SEP} AND trip_id IS NOT NULL")
W.check(ok, "the fixed report reconciles to the source")
ref = W.reference("d2_3_fixed")
W.check([int(x) for x in fixed.taps] == [r["taps"] for r in ref], "taps per route match the reference")
W.check(all(W.close(a, r["timepoint_on_time"]) for a, r in zip(fixed.timepoint_on_time, ref)), "punctuality per route matches")

# %% [markdown]
# ## ✱ Stretch · Ask the semantic layer for the same report
#
# The semantic model joins only along many-to-one relationships. Ask it for taps grouped by timepoint number, a
# grouping that would need the fan-out, and read what it says.

# %%
import wnt_semantic as S
model = S.Model(S.load("data/semantic/wadi_noor_transit.yaml"), con)
try:
    model.query(["boardings.boardings"], ["timepoints.tp_seq"], ["dates.gregorian_month = '2026-09'"])
except S.JoinPathError as e:
    print("refused:", e)
W.show(model.query(["boardings.boardings", "timepoint_on_time_rate"], ["routes.route_id"], ["dates.gregorian_month = '2026-09'"]))

# %% [markdown]
# ## Checkpoint
#
# 1. A join from trips to taps keeps the trip-level columns. Why can you still not sum `sched_minutes` after it?
#    <details><summary>Answer</summary>Each trip now appears once per tap; a trip column summed over taps counts each
#    trip as many times as it had taps.</details>
# 2. What makes a reconciliation test useful?
#    <details><summary>Answer</summary>It compares the report with a total computed another way, directly from the
#    source, and it fails on the faulty query.</details>
# 3. Two facts share a dimension. When is it safe to put their metrics side by side?
#    <details><summary>Answer</summary>When each is aggregated to the shared grain first (route, day) and the results
#    are joined on that grain.</details>
#
# **Carry forward.** "Aggregate each fact, then join" is exactly what the semantic layer of Lab 2.4 does for every
# request.
