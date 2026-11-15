# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0"]
# ///
# %% [markdown]
# # Lab 1.3 · Two ratio metrics, tested
#
# Day 1 · Session 3 (Ratios, distinct counts and time logic) · 25 min. You implement `on_time_rate` and
# `cancellation_rate` exactly as the catalogue defines them, test them on a small example you compute by hand, then
# on the September network, and show why four weekly counts of distinct cards do not add up to four weeks.
#
# **AI-tutor.** An assistant may explain an error; the hand computation is yours.
#
# **Reference state.** The warehouse through `W.db()` and the two entries of `data/catalogue/metric_catalogue.yaml`.
#
# **Tasks**
# - [ ] 1 · Hand-compute the on-time rate of a small example (5')
# - [ ] 2 · Implement the two ratio metrics (8')
# - [ ] 3 · Test them against the hand values and the network (6')
# - [ ] 4 · Show that weekly distinct cards do not add to a month (6')
# - [ ] ✱ Stretch · The same two metrics by Hijri month

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
cat = {m["name"]: m for m in W.yaml_load("data/catalogue/metric_catalogue.yaml")["metrics"]}
for n in ("on_time_rate", "cancellation_rate"):
    print(f"{n}: {cat[n]['formula']}\n   filters: {cat[n]['filters']}\n   time: {cat[n]['time_logic']}\n")

# %% [markdown]
# ## 1 · Hand-compute the on-time rate of a small example (5')
#
# Three routes on one day: route A departed 100 trips, 90 on time; route B departed 10, 5 on time; route C departed
# 40, 30 on time. Two more trips of route C were cancelled.
#
# ✏️ **Exercise** · With a pen first, then here: the network on-time rate as a ratio of sums, the mean of the three
# route rates, and the cancellation rate. Write fractions, not rounded numbers.

# %%
def hand_values() -> dict:
    # BEGIN SOLUTION
    return {"ratio_of_sums": (90 + 5 + 30) / (100 + 10 + 40),
            "mean_of_ratios": (90 / 100 + 5 / 10 + 30 / 40) / 3,
            "cancellation_rate": 2 / (100 + 10 + 40 + 2)}
    # END SOLUTION


# %%
# The same example as rows, so a function can be tested on it
con.execute("""CREATE OR REPLACE TABLE toy_trip AS
    SELECT route_id, DATE '2026-09-01' AS service_date,
           CASE WHEN i > departed THEN 'cancelled' ELSE 'operated' END AS status,
           CASE WHEN i > departed THEN NULL WHEN i <= on_time THEN 2.0 ELSE 9.0 END AS dep_delay_min, i AS trip_id
    FROM (VALUES ('A', 100, 90, 100), ('B', 10, 5, 10), ('C', 40, 30, 42)) v(route_id, departed, on_time, scheduled),
         range(1, 1000) r(i)
    WHERE i <= scheduled""")
try:
    hand = hand_values()
except NotImplementedError:
    hand = {"ratio_of_sums": 125 / 150, "mean_of_ratios": (0.9 + 0.5 + 0.75) / 3, "cancellation_rate": 2 / 152}
print({k: round(v, 4) for k, v in hand.items()})

# %% [markdown]
# ## 2 · Implement the two ratio metrics (8')
#
# ✏️ **Exercise** · Both functions take a start and an end service date (inclusive) and a table name, so the same
# code runs on `toy_trip` and on `fct_trip`. Follow the catalogue: a ratio of sums over the period.

# %%
def on_time_rate(con, start: str, end: str, table: str = "fct_trip") -> float:
    # BEGIN SOLUTION
    return W.scalar(con, f"""
        SELECT sum(CASE WHEN status <> 'cancelled' AND dep_delay_min BETWEEN -1 AND 5 THEN 1 ELSE 0 END)
             / sum(CASE WHEN status <> 'cancelled' THEN 1 ELSE 0 END)
        FROM {table} WHERE service_date BETWEEN DATE '{start}' AND DATE '{end}'""")
    # END SOLUTION


def cancellation_rate(con, start: str, end: str, table: str = "fct_trip") -> float:
    # BEGIN SOLUTION
    return W.scalar(con, f"""
        SELECT sum(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) / count(trip_id)
        FROM {table} WHERE service_date BETWEEN DATE '{start}' AND DATE '{end}'""")
    # END SOLUTION


# %% [markdown]
# ## 3 · Test them against the hand values and the network (6')

# %%
try:
    toy_otr, toy_cr = on_time_rate(con, "2026-09-01", "2026-09-01", "toy_trip"), cancellation_rate(con, "2026-09-01", "2026-09-01", "toy_trip")
    sep_otr, sep_cr = on_time_rate(con, "2026-09-01", "2026-09-30"), cancellation_rate(con, "2026-09-01", "2026-09-30")
except NotImplementedError:
    toy_otr, toy_cr = 125 / 150, 2 / 152
    ref = W.reference("d1_3_network")
    sep_otr, sep_cr = ref["on_time_rate"], ref["cancellation_rate"]
W.check(W.close(toy_otr, hand["ratio_of_sums"]), f"toy: on_time_rate {toy_otr:.4f} equals the hand ratio of sums")
W.check(not W.close(toy_otr, hand["mean_of_ratios"], 1e-3), f"toy: and differs from the mean of route rates {hand['mean_of_ratios']:.4f}")
W.check(W.close(toy_cr, hand["cancellation_rate"]), f"toy: cancellation_rate {toy_cr:.4f} equals the hand value")
ref = W.reference("d1_3_network")
W.check(W.close(sep_otr, ref["on_time_rate"]), f"September network on_time_rate {W.pct(sep_otr)}")
W.check(W.close(sep_cr, ref["cancellation_rate"]), f"September network cancellation_rate {W.pct(sep_cr)}")
print(f"the mean of the twelve route rates would say {W.pct(ref['mean_of_route_rates'])}: small routes count as much as big ones")

# %% [markdown]
# ## 4 · Show that weekly distinct cards do not add to a month (6')
#
# ✏️ **Exercise** · Return the distinct cards of each of the four weeks that start on Sunday 6, 13, 20 and 27
# September, and the distinct cards of the whole four weeks (6 September to 3 October).

# %%
def weekly_and_total(con) -> tuple[dict, int]:
    # BEGIN SOLUTION
    weeks = dict(con.execute("""
        SELECT d.week_start::VARCHAR, count(DISTINCT b.card_id)
        FROM fct_boarding b JOIN dim_date d ON d.date = b.service_date
        WHERE d.week_start BETWEEN DATE '2026-09-06' AND DATE '2026-09-27' GROUP BY 1 ORDER BY 1""").fetchall())
    total = W.scalar(con, """SELECT count(DISTINCT card_id) FROM fct_boarding
                             WHERE service_date BETWEEN DATE '2026-09-06' AND DATE '2026-10-03'""")
    return weeks, total
    # END SOLUTION


# %%
try:
    weeks, total = weekly_and_total(con)
except NotImplementedError:
    ref = W.reference("d1_3_weekly_cards")
    weeks, total = ref["weeks"], ref["four_weeks"]
for w, n in weeks.items():
    print(f"week of {w}: {n:,} cards")
print(f"sum of the four weeks {sum(weeks.values()):,} | distinct over the four weeks {total:,}")
W.check(sum(weeks.values()) > total, "the weekly counts add up to more than the four-week count: the same cards travel every week")
W.check(total == W.reference("d1_3_weekly_cards")["four_weeks"], "the four-week count matches the reference")

# %% [markdown]
# 🔍 A dashboard shows weekly unique cards and a "month total" computed by summing the weeks. How far off is it?
#
# ## ✱ Stretch · The same two metrics by Hijri month
#
# Use `dim_date.hijri_month_key` to compute both metrics for Rabi al-Awwal (`1448-03`) and Rabi al-Thani (`1448-04`).

# %%
def by_hijri_month(con):
    # BEGIN SOLUTION
    return W.df(con, """
        SELECT d.hijri_month_key,
               sum((t.status <> 'cancelled' AND t.dep_delay_min BETWEEN -1 AND 5)::INT) / sum((t.status <> 'cancelled')::INT) AS on_time_rate,
               avg((t.status = 'cancelled')::INT) AS cancellation_rate
        FROM fct_trip t JOIN dim_date d ON d.date = t.service_date
        WHERE d.hijri_month_key IN ('1448-03', '1448-04') GROUP BY 1 ORDER BY 1""")
    # END SOLUTION


try:
    W.show(by_hijri_month(con))
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. Route B has 10 trips at 50% on time; route A has 100 at 90%. Why does the mean of route rates understate the
#    network?
#    <details><summary>Answer</summary>It gives route B the same weight as route A, although it carries a tenth of the
#    trips. The ratio of sums weights each trip once.</details>
# 2. When is a mean of ratios the right answer?
#    <details><summary>Answer</summary>When the question is about the typical route, not the network: "how does a route
#    usually do?". Then say so in the name.</details>
# 3. Why can a dashboard not add weekly unique cards to get a month?
#    <details><summary>Answer</summary>Distinct counts are not additive: a card that travels every week is counted
#    once per week in the sum and once in the month.</details>
#
# **Carry forward.** The two functions are the tests of Day 2: the semantic layer must return the same values.
