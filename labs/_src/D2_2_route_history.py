# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0"]
# ///
# %% [markdown]
# # Lab 2.2 · A re-routed line and two calendars
#
# Day 2 · Session 2 (Changing dimensions and calendars) · 25 min. Route R07 was extended to Al-Rawdah Hospital on
# 1 June 2026, and `dim_route` keeps both versions (type 2). You join trips to the version valid on their service date,
# compare R07 before and after per kilometre, and report ridership by Hijri month and in Ramadan from `dim_date`.
#
# **AI-tutor.** An assistant may explain an error; the joins are yours.
#
# **Reference state.** The warehouse through `W.db()`.
#
# **Tasks**
# - [ ] 1 · Read the two versions of R07 (4')
# - [ ] 2 · Join trips to the version valid on the service date (8')
# - [ ] 3 · Compare boardings per kilometre before and after (6')
# - [ ] 4 · Report ridership by Hijri month and in Ramadan (7')
# - [ ] ✱ Stretch · Eid days against ordinary Fridays

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
# ## 1 · Read the two versions of R07 (4')

# %%
W.show(W.df(con, """SELECT route_key, route_id, route_name_en, route_name_ar, length_km, stop_count, valid_from, valid_to,
                           is_current FROM dim_route WHERE route_id = 'R07'"""))

# %% [markdown]
# 🔍 What changed, and what stayed? `route_id` is the natural key (riders and timetables use it); `route_key` is the
# surrogate key of one version; `valid_from` and `valid_to` say when each version was true.
#
# ## 2 · Join trips to the version valid on the service date (8')
#
# ✏️ **Exercise** · Write `trips_with_version()`: the SQL of every trip with the `route_key`, `route_name_en` and
# `length_km` of the version valid on its `service_date` (an open `valid_to` means "still valid").

# %%
def trips_with_version() -> str:
    # BEGIN SOLUTION
    return """
        SELECT t.*, r.route_key, r.route_name_en, r.length_km
        FROM fct_trip t
        JOIN dim_route r ON r.route_id = t.route_id
         AND t.service_date >= r.valid_from
         AND (r.valid_to IS NULL OR t.service_date <= r.valid_to)"""
    # END SOLUTION


# %%
try:
    sql = trips_with_version()
except NotImplementedError:
    sql = """SELECT t.*, r.route_key, r.route_name_en, r.length_km FROM fct_trip t JOIN dim_route r ON r.route_id = t.route_id
             AND t.service_date >= r.valid_from AND (r.valid_to IS NULL OR t.service_date <= r.valid_to)"""
con.execute(f"CREATE OR REPLACE VIEW trip_v AS {sql}")
n_trips, n_joined = W.scalar(con, "SELECT count(*) FROM fct_trip"), W.scalar(con, "SELECT count(*) FROM trip_v")
W.check(n_joined == n_trips, f"one row per trip after the join: {n_joined:,} of {n_trips:,}")
W.check(W.scalar(con, "SELECT count(DISTINCT route_key) FROM trip_v WHERE route_id = 'R07'") == 2, "R07 trips reach both versions")
W.check(W.scalar(con, "SELECT max(service_date) FROM trip_v WHERE route_key = 7").isoformat() == "2026-05-31",
        "the old version ends on 31 May")

# %% [markdown]
# ## 3 · Compare boardings per kilometre before and after (6')
#
# Taps per departed-trip kilometre, for each version of R07. A report that used the current row for every date would
# divide January's taps by June's length.
#
# ✏️ **Exercise** · Return one row per version: name, length, departed trips, taps, and taps per departed-trip km.

# %%
def r07_per_km(con):
    # BEGIN SOLUTION
    return W.df(con, """
        WITH trips AS (SELECT route_key, route_name_en, length_km, count(*) AS departed_trips
                       FROM trip_v WHERE route_id = 'R07' AND status <> 'cancelled' GROUP BY ALL),
             taps AS (SELECT t.route_key, count(*) AS taps
                      FROM fct_boarding b JOIN trip_v t USING (trip_id) WHERE t.route_id = 'R07' GROUP BY 1)
        SELECT route_name_en, length_km, departed_trips, taps, taps / (departed_trips * length_km) AS taps_per_km
        FROM trips JOIN taps USING (route_key) ORDER BY length_km""")
    # END SOLUTION


# %%
try:
    per_km = r07_per_km(con)
except NotImplementedError:
    import pandas as pd
    per_km = pd.DataFrame(W.reference("d2_2_r07"))
    per_km["taps_per_km"] = per_km.taps / (per_km.departed_trips * per_km.length_km)
W.show(per_km)
ref = W.reference("d2_2_r07")
W.check([int(x) for x in per_km.taps] == [r["taps"] for r in ref], "taps per version match the reference")
wrong = per_km.taps.iloc[0] / (per_km.departed_trips.iloc[0] * 15.8)
print(f"with the current length for January to May: {wrong:.3f} taps per km instead of {per_km.taps_per_km.iloc[0]:.3f}")

# %% [markdown]
# 🔍 Taps per trip rose after the extension; taps per kilometre is the fairer comparison of a longer route. Which
# number would you show planning, and with what sentence?
#
# ## 4 · Report ridership by Hijri month and in Ramadan (7')
#
# `dim_date` carries both calendars. Months have different numbers of service days, so compare taps per day.
#
# ✏️ **Exercise** · Taps per service day for each Hijri month (`hijri_month_key`, `hijri_month_name_en`), and the
# mean taps per day in Ramadan against the 30 days that follow it.

# %%
def hijri_months(con):
    # BEGIN SOLUTION
    return W.df(con, """
        SELECT d.hijri_month_key, any_value(d.hijri_month_name_en) AS month_name,
               count(*) / count(DISTINCT b.service_date) AS taps_per_day
        FROM fct_boarding b JOIN dim_date d ON d.date = b.service_date GROUP BY 1 ORDER BY 1""")
    # END SOLUTION


def ramadan_vs_after(con) -> tuple[float, float]:
    # BEGIN SOLUTION
    ram = W.scalar(con, """SELECT count(*) / count(DISTINCT b.service_date) FROM fct_boarding b
                           JOIN dim_date d ON d.date = b.service_date WHERE d.is_ramadan""")
    end = W.scalar(con, "SELECT max(date) FROM dim_date WHERE is_ramadan")
    after = W.scalar(con, f"""SELECT count(*) / count(DISTINCT service_date) FROM fct_boarding
                              WHERE service_date > DATE '{end}' AND service_date <= DATE '{end}' + 30""")
    return ram, after
    # END SOLUTION


# %%
try:
    hm = hijri_months(con)
    ram, after = ramadan_vs_after(con)
except NotImplementedError:
    import pandas as pd
    hm = pd.DataFrame(W.reference("d2_2_hijri"))
    ram, after = None, None
W.show(hm)
ref = W.reference("d2_2_hijri")
W.check(len(hm) == len(ref) and all(W.close(a, b["taps_per_day"]) for a, b in zip(hm.taps_per_day, ref)),
        "taps per day by Hijri month match the reference")
if ram is not None:
    print(f"Ramadan: {ram:,.0f} taps per day | the 30 days after: {after:,.0f}")
    W.check(ram < after, "Ramadan has fewer taps per day than the 30 days after it")

# %% [markdown]
# ## ✱ Stretch · Eid days against ordinary Fridays
#
# Eid days run a holiday timetable. Compare taps per day on Eid al-Fitr and Eid al-Adha with the mean of ordinary
# Fridays (no holiday).

# %%
def eid_vs_friday(con):
    # BEGIN SOLUTION
    return W.df(con, """
        SELECT coalesce(d.holiday_en, 'ordinary ' || d.day_of_week_en) AS day_kind,
               count(*) / count(DISTINCT b.service_date) AS taps_per_day
        FROM fct_boarding b JOIN dim_date d ON d.date = b.service_date
        WHERE d.holiday_en LIKE 'Eid%' OR (d.holiday_en IS NULL AND d.day_of_week_en = 'Friday')
        GROUP BY 1 ORDER BY 1""")
    # END SOLUTION


try:
    W.show(eid_vs_friday(con))
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. A report divides each month's R07 taps by the route's current length. Which months are wrong, and in which
#    direction?
#    <details><summary>Answer</summary>January to May: the current length (15.8 km) is longer than the route was
#    (11.4 km), so taps per km are understated before the change.</details>
# 2. Why compare Ramadan with the days after it in taps per day, not in taps per month?
#    <details><summary>Answer</summary>A Hijri month has 29 or 30 days and a Gregorian month 28 to 31; taps per day
#    removes the length of the period.</details>
# 3. A type 1 change overwrites the old value. When would that be right for a route?
#    <details><summary>Answer</summary>To correct an error (a misspelt name), where history should never have held the
#    wrong value. A real change of the route is type 2.</details>
#
# **Carry forward.** The as-of join is the `source` of the trips and boardings datasets in the semantic model of
# Lab 2.4.
