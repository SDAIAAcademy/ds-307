# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0"]
# ///
# %% [markdown]
# # Lab 1.4 · A network metric tree
#
# Day 1 · Session 4 (Metric trees) · 25 min. The network goal is weekly card taps. You split it into three drivers
# that multiply back to it exactly, compute them for the weeks starting 13 and 20 September, add a guardrail and the
# owners, and say which driver moved the goal.
#
# **AI-tutor.** An assistant may explain an error; the tree is yours.
#
# **Reference state.** The warehouse through `W.db()` and the governed catalogue `data/catalogue/metric_catalogue.yaml`.
#
# **Tasks**
# - [ ] 1 · Choose the goal and its decomposition (5')
# - [ ] 2 · Compute the three drivers for two weeks (8')
# - [ ] 3 · Reconcile the tree to the goal (6')
# - [ ] 4 · Add the guardrail and the owners (6')
# - [ ] ✱ Stretch · Attribute the week-on-week change to each driver with log changes

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

import math
import wnt as W
con = W.db()
WEEKS = ["2026-09-13", "2026-09-20"]
catalogue = {m["name"]: m for m in W.yaml_load("data/catalogue/metric_catalogue.yaml")["metrics"]}

# %% [markdown]
# ## 1 · Choose the goal and its decomposition (5')
#
# A multiplicative tree: **taps = scheduled trips × (1 − cancellation rate) × taps per departed trip**. The first
# driver is the timetable (planning), the second the delivery of it (control centre), the third the demand on each
# bus that ran. Check the algebra: scheduled × (1 − cancelled/scheduled) is the departed trips.
#
# ✏️ **Exercise** · Write the tree as a dictionary: the goal, the three drivers (catalogue names) and how they combine.

# %%
def tree_spec() -> dict:
    # BEGIN SOLUTION
    return {"goal": "taps", "drivers": ["scheduled_trips", "cancellation_rate", "taps_per_departed_trip"],
            "combine": "scheduled_trips * (1 - cancellation_rate) * taps_per_departed_trip"}
    # END SOLUTION


# %%
try:
    spec = tree_spec()
except NotImplementedError:
    spec = {"goal": "taps", "drivers": ["scheduled_trips", "cancellation_rate", "taps_per_departed_trip"],
            "combine": "scheduled_trips * (1 - cancellation_rate) * taps_per_departed_trip"}
W.check(all(d in catalogue for d in [spec["goal"], *spec["drivers"]]), "the goal and every driver are governed catalogue metrics")

# %% [markdown]
# ## 2 · Compute the three drivers for two weeks (8')
#
# ✏️ **Exercise** · `week_values(con, week_start)` returns the goal and the three drivers for the seven service days
# from `week_start`. Each ratio is a ratio of sums, each fact counted at its own grain.

# %%
def week_values(con, week_start: str) -> dict:
    span = f"service_date BETWEEN DATE '{week_start}' AND DATE '{week_start}'::DATE + 6"
    # BEGIN SOLUTION
    taps = W.scalar(con, f"SELECT count(*) FROM fct_boarding WHERE {span}")
    sched = W.scalar(con, f"SELECT count(*) FROM fct_trip WHERE {span}")
    cancelled = W.scalar(con, f"SELECT count(*) FROM fct_trip WHERE status = 'cancelled' AND {span}")
    return {"taps": taps, "scheduled_trips": sched, "cancellation_rate": cancelled / sched,
            "taps_per_departed_trip": taps / (sched - cancelled)}
    # END SOLUTION


# %%
try:
    values = {w: week_values(con, w) for w in WEEKS}
except NotImplementedError:
    values = {w: {k: v for k, v in W.reference("d1_4_tree")[w].items() if k != "complaints_per_10k_taps"} for w in WEEKS}
for w in WEEKS:
    v = values[w]
    print(f"week of {w}: taps {v['taps']:,} | scheduled {v['scheduled_trips']:,} | cancelled {W.pct(v['cancellation_rate'])}"
          f" | taps per departed trip {v['taps_per_departed_trip']:.2f}")
ref = W.reference("d1_4_tree")
W.check(all(W.close(values[w][k], ref[w][k]) for w in WEEKS for k in values[w]), "the drivers match the reference")

# %% [markdown]
# ## 3 · Reconcile the tree to the goal (6')
#
# A tree you cannot reconcile is a list of numbers. Multiply the drivers back and compare with the goal.

# %%
for w in WEEKS:
    v = values[w]
    rebuilt = eval(spec["combine"], {}, v)
    W.check(abs(rebuilt - v["taps"]) < 1e-6, f"week of {w}: the drivers multiply back to {rebuilt:,.0f} taps")
change = {k: values[WEEKS[1]][k] / values[WEEKS[0]][k] - 1 for k in values[WEEKS[0]]}
change["1 - cancellation_rate"] = (1 - values[WEEKS[1]]["cancellation_rate"]) / (1 - values[WEEKS[0]]["cancellation_rate"]) - 1
for k in ["taps", "scheduled_trips", "1 - cancellation_rate", "taps_per_departed_trip"]:
    print(f"{k:24s} {100 * change[k]:+.1f}%")

# %% [markdown]
# 🔍 Which driver moved the goal? Look at `dim_date` for the week of 20 September before you answer.
#
# ## 4 · Add the guardrail and the owners (6')
#
# A guardrail is a metric a driver could improve at its expense: pushing more riders onto each bus could raise
# complaints. Use `complaints_per_10k_taps`.
#
# ✏️ **Exercise** · Complete `nodes()`: every node of the tree with its owner from the catalogue, and the guardrail
# with its value in both weeks and the direction that would worry you.

# %%
def nodes(con) -> dict:
    # BEGIN SOLUTION
    out = {n: {"owner": catalogue[n]["owner"]} for n in [spec["goal"], *spec["drivers"]]}
    g = {}
    for w in WEEKS:
        span = f"BETWEEN DATE '{w}' AND DATE '{w}'::DATE + 6"
        g[w] = 10000 * W.scalar(con, f"SELECT count(*) FROM fct_complaint WHERE received_date {span}") / \
            W.scalar(con, f"SELECT count(*) FROM fct_boarding WHERE service_date {span}")
    out["complaints_per_10k_taps"] = {"owner": catalogue["complaints_per_10k_taps"]["owner"], "role": "guardrail",
                                      "values": g, "worry_if": "up"}
    return out
    # END SOLUTION


# %%
try:
    tree = nodes(con)
except NotImplementedError:
    tree = {n: {"owner": catalogue[n]["owner"]} for n in [spec["goal"], *spec["drivers"]]}
    tree["complaints_per_10k_taps"] = {"owner": catalogue["complaints_per_10k_taps"]["owner"], "role": "guardrail",
                                       "values": {w: ref[w]["complaints_per_10k_taps"] for w in WEEKS}, "worry_if": "up"}
for n, info in tree.items():
    print(f"{n:24s} {info['owner']}" + (f"  guardrail {info['values']}" if info.get("role") else ""))
W.check(all("owner" in v for v in tree.values()), "every node has an owner")
gr = tree["complaints_per_10k_taps"]
W.check(all(W.close(gr["values"][w], ref[w]["complaints_per_10k_taps"]) for w in WEEKS), "the guardrail values match")

# %% [markdown]
# ## ✱ Stretch · Attribute the change to each driver with log changes
#
# In a product, the log changes add: ln(taps₂/taps₁) = Σ ln(driver₂/driver₁). Each driver's share of the change is its
# log change over the total.

# %%
def log_shares() -> dict:
    # BEGIN SOLUTION
    a, b = values[WEEKS[0]], values[WEEKS[1]]
    parts = {"scheduled_trips": math.log(b["scheduled_trips"] / a["scheduled_trips"]),
             "1 - cancellation_rate": math.log((1 - b["cancellation_rate"]) / (1 - a["cancellation_rate"])),
             "taps_per_departed_trip": math.log(b["taps_per_departed_trip"] / a["taps_per_departed_trip"])}
    total = math.log(b["taps"] / a["taps"])
    return {k: v / total for k, v in parts.items()}
    # END SOLUTION


try:
    shares = log_shares()
    for k, s in shares.items():
        print(f"{k:24s} {100 * s:6.1f}% of the change")
    W.check(abs(sum(shares.values()) - 1) < 1e-9, "the shares add up to 100%")
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. Taps fell 8% between the two weeks. A manager says "demand is down". What does the tree say?
#    <details><summary>Answer</summary>The timetable fell 8% (National Day ran a holiday timetable); taps per trip
#    barely moved. Fewer buses, not fewer riders per bus.</details>
# 2. Why put the cancellation rate in the tree as (1 − rate), not as the rate?
#    <details><summary>Answer</summary>So the drivers multiply back to the goal: scheduled × (1 − rate) is the
#    departed trips.</details>
# 3. What makes complaints per 10,000 taps a guardrail and not a driver?
#    <details><summary>Answer</summary>It is not part of the product. It watches for harm a driver could cause:
#    crowding more riders onto each bus raises taps per trip and complaints.</details>
#
# **Carry forward.** The tree's nodes are metrics of Day 2's semantic model; Day 3's dashboard opens with them.
