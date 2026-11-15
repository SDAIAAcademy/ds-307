# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0"]
# ///
# %% [markdown]
# # Pre-work · Five warm-up queries
#
# Guided self-study before Day 1, about two hours with the reading. You meet the warehouse of Wadi Noor Transit and
# check that the SQL this course assumes (joins, grouping, window functions) is at your fingertips. Then run
# `00_setup_check.ipynb`.
#
# **Reading.** The case study in the course README; the data dictionary `data/catalogue/data_dictionary.md`.
#
# **Tasks**
# - [ ] 1 · Count the rows of each fact table
# - [ ] 2 · Trips by status in September
# - [ ] 3 · The five routes with the most card taps
# - [ ] 4 · Taps per day, with the day of the week from the date table
# - [ ] 5 · Each card's previous tap, with a window function
# - [ ] Entry quiz · six questions

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

# %% [markdown]
# ## 1 · Count the rows of each fact table
#
# ✏️ **Exercise** · Return a dict of table name to row count for `fct_trip`, `fct_timepoint`, `fct_boarding` and
# `fct_complaint`.

# %%
def fact_counts() -> dict:
    # BEGIN SOLUTION
    return {t: W.scalar(con, f"SELECT count(*) FROM {t}") for t in ("fct_trip", "fct_timepoint", "fct_boarding", "fct_complaint")}
    # END SOLUTION


try:
    fc = fact_counts()
    print(fc)
    W.check(fc.get("fct_complaint") == 2400, "2,400 complaints")
except NotImplementedError:
    print("task 1 not done")

# %% [markdown]
# ## 2 · Trips by status in September
#
# ✏️ **Exercise** · Count September trips by `status` (operated, partial, cancelled).

# %%
def by_status():
    # BEGIN SOLUTION
    return W.df(con, """SELECT status, count(*) AS trips FROM fct_trip
                        WHERE service_date BETWEEN DATE '2026-09-01' AND DATE '2026-09-30' GROUP BY 1 ORDER BY 2 DESC""")
    # END SOLUTION


try:
    st = by_status()
    W.show(st)
    W.check(set(st.status) == {"operated", "partial", "cancelled"}, "three statuses")
except NotImplementedError:
    print("task 2 not done")

# %% [markdown]
# ## 3 · The five routes with the most card taps
#
# ✏️ **Exercise** · Join `fct_boarding` to `dim_route` for the English route name. Careful: route R07 has two rows in
# `dim_route`. Count each tap once.

# %%
def top_routes():
    # BEGIN SOLUTION
    return W.df(con, """SELECT b.route_id, any_value(r.route_name_en) AS name, count(*) AS taps
                        FROM fct_boarding b JOIN dim_route r ON r.route_id = b.route_id AND r.is_current
                        GROUP BY 1 ORDER BY 3 DESC LIMIT 5""")
    # END SOLUTION


try:
    tr = top_routes()
    W.show(tr)
    total = W.scalar(con, "SELECT count(*) FROM fct_boarding WHERE route_id = 'R01'")
    W.check(int(tr.loc[tr.route_id == "R01", "taps"].iloc[0]) == total, "R01 counted once per tap")
except NotImplementedError:
    print("task 3 not done")

# %% [markdown]
# ## 4 · Taps per day, with the day of the week from the date table
#
# ✏️ **Exercise** · Average taps per day for each `day_of_week_en`, from `dim_date`. Which day is quietest?

# %%
def per_weekday():
    # BEGIN SOLUTION
    return W.df(con, """SELECT d.day_of_week_en, count(*) / count(DISTINCT b.service_date) AS taps_per_day
                        FROM fct_boarding b JOIN dim_date d ON d.date = b.service_date GROUP BY 1 ORDER BY 2""")
    # END SOLUTION


try:
    wd = per_weekday()
    W.show(wd.round(0))
    W.check(wd.day_of_week_en.iloc[0] == "Friday", "Friday is the quietest day: the weekend timetable")
except NotImplementedError:
    print("task 4 not done")

# %% [markdown]
# ## 5 · Each card's previous tap, with a window function
#
# ✏️ **Exercise** · For each tap of card 712598 on 1 October, show the time of the same card's previous tap with
# `lag()`.

# %%
def previous_tap():
    # BEGIN SOLUTION
    return W.df(con, """SELECT tap_ts, route_id, lag(tap_ts) OVER (PARTITION BY card_id ORDER BY tap_ts) AS previous_tap
                        FROM fct_boarding WHERE card_id = 712598 AND service_date = DATE '2026-10-01' ORDER BY tap_ts""")
    # END SOLUTION


try:
    pt = previous_tap()
    W.show(pt)
    W.check(len(pt) > 0 and pt.previous_tap.isna().iloc[0], "the first tap of the day has no previous tap on that day")
except NotImplementedError:
    print("task 5 not done")

# %% [markdown]
# ## Entry quiz
#
# Answer before you open the answers. If you miss two or more, revise joins and window functions (FN-104, Day 1 and
# Day 2) before the course.
#
# 1. A join from 85,010 trips to a route table returns 91,418 rows. What is the most likely cause?
#    <details><summary>Answer</summary>The route table has more than one row for some route_id (a history), so those
#    trips matched twice.</details>
# 2. `WHERE status <> 'cancelled'` and `WHERE NOT status = 'cancelled'`: do they differ when status is NULL?
#    <details><summary>Answer</summary>No; both drop the NULL rows, because a comparison with NULL is unknown.</details>
# 3. Why is `count(DISTINCT card_id)` for a month not the sum of the four weekly counts?
#    <details><summary>Answer</summary>A card that tapped in several weeks is counted once in the month and once in
#    each week.</details>
# 4. What does `lag(x) OVER (PARTITION BY card_id ORDER BY tap_ts)` return for the first tap of a card?
#    <details><summary>Answer</summary>NULL: there is no earlier row in that partition.</details>
# 5. You average 30 daily on-time rates to get the month. When is that wrong?
#    <details><summary>Answer</summary>When days have different numbers of trips: the month's rate is the sum of
#    on-time trips over the sum of trips.</details>
# 6. A LEFT JOIN from routes to complaints, then `WHERE c.category = 'late'`. What happens to routes without late
#    complaints?
#    <details><summary>Answer</summary>They disappear: the filter on the right table turns the left join into an inner
#    join. Put the condition in the ON clause to keep them.</details>
