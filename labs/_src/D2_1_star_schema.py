# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0"]
# ///
# %% [markdown]
# # Lab 2.1 · Facts, dimensions and their grain
#
# Day 2 · Session 1 (Star schemas for analysis) · 25 min. Before a semantic model can define a metric once, every
# table needs a stated grain and a proven key. You name the grain of each warehouse table, prove it by counting, write
# the star (which fact reaches which dimension through which key) and find the dimension whose natural key fails.
#
# **AI-off.** The grain sentences and key tests are yours; the supervised check asks for them.
#
# **Reference state.** The warehouse through `W.db()` and `data/catalogue/data_dictionary.md`.
#
# **Tasks**
# - [ ] 1 · Name the grain of each table (5')
# - [ ] 2 · Prove the grains with key tests (8')
# - [ ] 3 · Draw the star: facts, dimensions, keys (6')
# - [ ] 4 · Find the dimension whose natural key fails (6')
# - [ ] ✱ Stretch · Check that dates conform across the two facts

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
TABLES = ["fct_trip", "fct_timepoint", "fct_boarding", "fct_complaint", "dim_route", "dim_date", "dim_vehicle"]
for t in TABLES:
    cols = [r[0] for r in con.execute(f"DESCRIBE {t}").fetchall()]
    print(f"{t:14s} {W.scalar(con, f'SELECT count(*) FROM {t}'):>8,} rows  {', '.join(cols[:9])}{' ...' if len(cols) > 9 else ''}")

# %% [markdown]
# ## 1 · Name the grain of each table (5')
#
# ✏️ **Exercise** · For each table, the columns you believe identify one row. Write the grain sentence as a comment.

# %%
def grain_keys() -> dict:
    # BEGIN SOLUTION
    return {
        "fct_trip": ["trip_id"],                # one scheduled trip
        "fct_timepoint": ["trip_id", "tp_seq"],  # one departed trip at one timepoint
        "fct_boarding": ["tap_id"],             # one card tap
        "fct_complaint": ["complaint_id"],      # one complaint
        "dim_route": ["route_id"],              # one route ... or is it? Task 4
        "dim_date": ["date"],                   # one day
        "dim_vehicle": ["vehicle_id"],          # one bus
    }
    # END SOLUTION


# %%
try:
    keys = grain_keys()
except NotImplementedError:
    keys = W.reference("d2_1_keys") | {"dim_route": ["route_id"]}
print(keys)

# %% [markdown]
# ## 2 · Prove the grains with key tests (8')
#
# A key holds when the number of rows equals the number of distinct key values and no key column is empty.
#
# ✏️ **Exercise** · Write `key_test(con, table, cols)` returning rows, distinct keys and rows with an empty key column.

# %%
def key_test(con, table: str, cols: list[str]) -> dict:
    # BEGIN SOLUTION
    k = ", ".join(cols)
    nulls = " OR ".join(f"{c} IS NULL" for c in cols)
    return {"rows": W.scalar(con, f"SELECT count(*) FROM {table}"),
            "distinct": W.scalar(con, f"SELECT count(*) FROM (SELECT DISTINCT {k} FROM {table})"),
            "null_keys": W.scalar(con, f"SELECT count(*) FROM {table} WHERE {nulls}")}
    # END SOLUTION


# %%
def _fallback(con, table, cols):
    k = ", ".join(cols)
    return {"rows": W.scalar(con, f"SELECT count(*) FROM {table}"),
            "distinct": W.scalar(con, f"SELECT count(*) FROM (SELECT DISTINCT {k} FROM {table})"),
            "null_keys": W.scalar(con, f"SELECT count(*) FROM {table} WHERE " + " OR ".join(f"{c} IS NULL" for c in cols))}


results = {}
for t, cols in keys.items():
    try:
        r = key_test(con, t, cols)
    except NotImplementedError:
        r = _fallback(con, t, cols)
    results[t] = r
    holds = r["rows"] == r["distinct"] and r["null_keys"] == 0
    print(f"{'holds ' if holds else 'FAILS '} {t:14s} {str(cols):28s} rows {r['rows']:>8,} distinct {r['distinct']:>8,} empty {r['null_keys']}")
W.check(results["fct_timepoint"]["rows"] == results["fct_timepoint"]["distinct"], "fct_timepoint: one row per trip and timepoint")
W.check(results["fct_boarding"]["null_keys"] == 0, "fct_boarding: every tap has an id")

# %% [markdown]
# 🔍 `fct_boarding.trip_id` has empty values too. Does that break the key of `fct_boarding`? (No: `trip_id` is a
# foreign key there, not the key. Note it for Day 3.)
#
# ## 3 · Draw the star: facts, dimensions, keys (6')
#
# ✏️ **Exercise** · For each fact, the dimensions it reaches and the column pair of each join
# (`(fact column, dimension, dimension column)`). Ignore `dim_route` until task 4.

# %%
def star() -> dict:
    # BEGIN SOLUTION
    return {
        "fct_trip": [("service_date", "dim_date", "date"), ("vehicle_id", "dim_vehicle", "vehicle_id")],
        "fct_boarding": [("service_date", "dim_date", "date"), ("vehicle_id", "dim_vehicle", "vehicle_id"),
                         ("trip_id", "fct_trip", "trip_id")],
        "fct_timepoint": [("trip_id", "fct_trip", "trip_id")],
        "fct_complaint": [("received_date", "dim_date", "date")],
    }
    # END SOLUTION


# %%
try:
    s = star()
except NotImplementedError:
    s = {"fct_trip": [("service_date", "dim_date", "date")], "fct_boarding": [("service_date", "dim_date", "date")]}
for fact, links in s.items():
    for fc, dim, dc in links:
        orphans = W.scalar(con, f"SELECT count(*) FROM {fact} f WHERE f.{fc} IS NOT NULL AND NOT EXISTS "
                                f"(SELECT 1 FROM {dim} d WHERE d.{dc} = f.{fc})")
        many = W.scalar(con, f"SELECT count(*) FROM (SELECT {dc} FROM {dim} GROUP BY 1 HAVING count(*) > 1)")
        W.check(orphans == 0 and many == 0, f"{fact}.{fc} -> {dim}.{dc}: {orphans} orphans, {many} repeated keys on the one side")

# %% [markdown]
# ## 4 · Find the dimension whose natural key fails (6')
#
# ✏️ **Exercise** · Show the rows of `dim_route` that share a `route_id`, and return the column that is the real key.

# %%
def route_key_column(con) -> str:
    # BEGIN SOLUTION
    W.show(W.df(con, """SELECT route_key, route_id, route_name_en, length_km, valid_from, valid_to, is_current
                        FROM dim_route WHERE route_id IN (SELECT route_id FROM dim_route GROUP BY 1 HAVING count(*) > 1)"""))
    return "route_key"
    # END SOLUTION


# %%
try:
    rk = route_key_column(con)
except NotImplementedError:
    rk = "route_key"
r_id, r_key = _fallback(con, "dim_route", ["route_id"]), _fallback(con, "dim_route", [rk])
W.check(r_id["rows"] > r_id["distinct"], f"route_id is not a key of dim_route: {r_id['rows']} rows, {r_id['distinct']} routes")
W.check(r_key["rows"] == r_key["distinct"], f"{rk} is: one row per version of a route")
naive = W.scalar(con, "SELECT count(*) FROM fct_trip t JOIN dim_route r USING (route_id)")
W.check(naive > results["fct_trip"]["rows"], f"a join on route_id returns {naive:,} rows for {results['fct_trip']['rows']:,} trips")

# %% [markdown]
# ## ✱ Stretch · Do the dates conform?
#
# A conformed dimension means the same thing to every fact that uses it. Check that every service date of
# `fct_trip` and `fct_boarding` and every received date of `fct_complaint` is a row of `dim_date`, and that the two
# facts cover the same days.

# %%
def conformed(con) -> dict:
    # BEGIN SOLUTION
    return {f: W.scalar(con, f"SELECT count(DISTINCT {c}) FROM {f} WHERE {c} NOT IN (SELECT date FROM dim_date)")
            for f, c in [("fct_trip", "service_date"), ("fct_boarding", "service_date"), ("fct_complaint", "received_date")]}
    # END SOLUTION


try:
    print(conformed(con))
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. `fct_timepoint` has 329,188 rows. Why is `trip_id` alone not its key?
#    <details><summary>Answer</summary>A departed trip has up to four timepoints; the grain is one trip at one
#    timepoint, so the key is (trip_id, tp_seq).</details>
# 2. What happens to trip counts when `fct_trip` joins `dim_route` on `route_id`?
#    <details><summary>Answer</summary>Every R07 trip matches two versions and is counted twice. Join on the version
#    valid on the service date (Session 2), or on a surrogate `route_key`.</details>
# 3. Is `fct_boarding` a fact of its own, or a detail of `fct_trip`?
#    <details><summary>Answer</summary>A fact of its own, at a finer grain (one tap). It reaches trips many-to-one, so
#    a trip metric must never be summed over taps.</details>
#
# **Carry forward.** The keys and the star are the datasets and relationships of the semantic model in Lab 2.4.
