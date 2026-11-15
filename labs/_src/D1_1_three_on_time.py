# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0"]
# ///
# %% [markdown]
# # Lab 1.1 · Three on-time figures
#
# Day 1 · Session 1 (Why three reports disagree) · 25 min. The September reports of Wadi Noor Transit give three
# on-time figures: 80.7%, 66.0% and 58.4%. You reproduce each from the rule its owner wrote, walk from one figure to
# another one rule at a time, and write the diagnosis that names the cause of each difference.
#
# **AI-off.** Write the queries and the diagnosis yourself; this is the skill the supervised check asks for.
#
# **Reference state.** The warehouse in `data/warehouse/` through `W.db()`, and `data/reports/three_reports.yaml`.
#
# **Tasks**
# - [ ] 1 · Compute the operations figure from its rule (6')
# - [ ] 2 · Compute the planning and board figures (7')
# - [ ] 3 · Walk from one figure to the next, one rule at a time (8')
# - [ ] 4 · Write the diagnosis: one cause per difference (4')
# - [ ] ✱ Stretch · Which figure answers the question the operations director asks every Sunday?

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
REPORTS = W.yaml_load("data/reports/three_reports.yaml")
for key, r in REPORTS.items():
    print(f"{key:10s} {r['published']:>6s}  {r['owner']}\n           {r['rule_as_written']}\n")

# %% [markdown]
# ## 1 · Compute the operations figure from its rule (6')
#
# `fct_trip` has one row per scheduled trip: `status` (operated, partial, cancelled), `dep_delay_min` (minutes late
# leaving the first timepoint, negative when early) and `arr_delay_min` (minutes late at the terminus).
#
# ✏️ **Exercise** · Write `operations_figure()`: Tawfiq's rule for September 2026, as a share between 0 and 1.

# %%
def operations_figure(con) -> float:
    # BEGIN SOLUTION
    return W.scalar(con, """
        SELECT avg(CASE WHEN dep_delay_min BETWEEN -1 AND 5 THEN 1.0 ELSE 0.0 END)
        FROM fct_trip
        WHERE status <> 'cancelled' AND service_date BETWEEN DATE '2026-09-01' AND DATE '2026-09-30'""")
    # END SOLUTION


# %%
try:
    ops = operations_figure(con)
except NotImplementedError:
    ops = W.reference("d1_1_figures")["operations"]
print(f"operations: {W.pct(ops)}  (published {REPORTS['operations']['published']})")
W.check(W.pct(ops) == REPORTS["operations"]["published"], "your query reproduces the published operations figure")

# %% [markdown]
# ## 2 · Compute the planning and board figures (7')
#
# `fct_timepoint` has one row per departed trip at each of its four timepoints, with `delay_min` empty where the trip
# never arrived. `dim_date` maps each `date` to its Hijri month: `hijri_month_key` is `'1448-04'` for Rabi al-Thani 1448.
#
# ✏️ **Exercise** · Write `planning_figure()` and `board_figure()` from Dhuha's and Yasmeen's rules.

# %%
def planning_figure(con) -> float:
    # BEGIN SOLUTION
    return W.scalar(con, """
        SELECT avg(CASE WHEN p.delay_min BETWEEN -1 AND 5 THEN 1.0 ELSE 0.0 END)
        FROM fct_timepoint p JOIN fct_trip t USING (trip_id)
        WHERE p.delay_min IS NOT NULL AND t.service_date BETWEEN DATE '2026-09-01' AND DATE '2026-09-30'""")
    # END SOLUTION


def board_figure(con) -> float:
    # BEGIN SOLUTION
    return W.scalar(con, """
        SELECT avg(CASE WHEN t.status = 'operated' AND t.arr_delay_min <= 5 THEN 1.0 ELSE 0.0 END)
        FROM fct_trip t JOIN dim_date d ON d.date = t.service_date
        WHERE d.hijri_month_key = '1448-04'""")
    # END SOLUTION


# %%
try:
    plan, board = planning_figure(con), board_figure(con)
except NotImplementedError:
    ref = W.reference("d1_1_figures")
    plan, board = ref["planning"], ref["board"]
print(f"planning: {W.pct(plan)}  board: {W.pct(board)}")
W.check(W.pct(plan) == REPORTS["planning"]["published"], "your query reproduces the planning figure")
W.check(W.pct(board) == REPORTS["board"]["published"], "your query reproduces the board figure")

# %% [markdown]
# ## 3 · Walk from one figure to the next, one rule at a time (8')
#
# `on_time()` below computes an on-time share from five rules. With its defaults it is the operations figure.
# Change one rule at a time and watch the figure move: that is a reconciliation walk.
#
# | Rule | Values |
# |---|---|
# | `unit` | `"trip"` or `"timepoint"` (every recorded timepoint arrival) |
# | `point` | `"first"` (leaving the first timepoint) or `"terminal"` (arriving at the terminus); trips only |
# | `early` | minutes early still counted on time (`-1`), or `None` for any early arrival |
# | `cancelled` | `"exclude"` (not in the denominator) or `"fail"` (in the denominator, never on time); trips only |
# | `period` | `("gregorian", "2026-09")` or `("hijri", "1448-04")` |

# %%
def on_time(con, unit="trip", point="first", early=-1, cancelled="exclude", period=("gregorian", "2026-09"), late=5):
    cal = "gregorian_month" if period[0] == "gregorian" else "hijri_month_key"
    low = f"BETWEEN {early} AND {late}" if early is not None else f"<= {late}"
    if unit == "timepoint":
        return W.scalar(con, f"""
            SELECT avg(CASE WHEN p.delay_min {low} THEN 1.0 ELSE 0.0 END)
            FROM fct_timepoint p JOIN fct_trip t USING (trip_id) JOIN dim_date d ON d.date = t.service_date
            WHERE p.delay_min IS NOT NULL AND d.{cal} = '{period[1]}'""")
    delay, ran = ("dep_delay_min", "status <> 'cancelled'") if point == "first" else ("arr_delay_min", "status = 'operated'")
    where = "status <> 'cancelled'" if cancelled == "exclude" else "TRUE"
    return W.scalar(con, f"""
        SELECT avg(CASE WHEN {ran} AND {delay} {low} THEN 1.0 ELSE 0.0 END)
        FROM fct_trip t JOIN dim_date d ON d.date = t.service_date
        WHERE {where} AND d.{cal} = '{period[1]}'""")


print(f"defaults = operations: {W.pct(on_time(con))}")

# %% [markdown]
# ✏️ **Exercise** · Fill `walk_to_board()`: the rule changes, in order, that take the operations rules to the board
# rules. Each item is a label and the keyword arguments **after** that change (they accumulate).

# %%
def walk_to_board() -> list[tuple[str, dict]]:
    # BEGIN SOLUTION
    return [
        ("measured at the terminus, not the first stop", dict(point="terminal")),
        ("early arrivals count as on time", dict(point="terminal", early=None)),
        ("cancelled trips count as late", dict(point="terminal", early=None, cancelled="fail")),
        ("Hijri month Rabi al-Thani, not September", dict(point="terminal", early=None, cancelled="fail",
                                                          period=("hijri", "1448-04"))),
    ]
    # END SOLUTION


# %%
try:
    walk = walk_to_board()
except NotImplementedError:
    walk = [(s["label"], s["rules"] | ({"period": tuple(s["rules"]["period"])} if "period" in s["rules"] else {}))
            for s in W.reference("d1_1_walk")]
prev = ops
print(f"{'start: operations rules':48s} {W.pct(prev):>7s}")
for label, rules in walk:
    now = on_time(con, **rules)
    print(f"{label:48s} {W.pct(now):>7s}  ({100 * (now - prev):+.1f} points)")
    prev = now
W.check(abs(prev - board) < 1e-9, "the walk ends exactly on the board figure")
W.check(len(walk) == 4, "four rules separate the operations and the board figures")
step_tp = on_time(con, unit="timepoint")
W.check(abs(step_tp - plan) < 1e-9, f"one rule separates operations from planning: the unit ({W.pct(step_tp)})")

# %% [markdown]
# 🔍 Look at the size of each step. Would the steps be the same size in another order? Try swapping two of them.
#
# ## 4 · Write the diagnosis: one cause per difference (4')
#
# ✏️ **Exercise** · Name the causes with the words of this list: `grain`, `point measured`, `tolerance`,
# `cancelled trips`, `period`.

# %%
def diagnosis() -> dict:
    # BEGIN SOLUTION
    return {
        "operations vs planning": ["grain"],
        "operations vs board": ["point measured", "tolerance", "cancelled trips", "period"],
    }
    # END SOLUTION


# %%
try:
    mine = diagnosis()
except NotImplementedError:
    mine = W.reference("d1_1_diagnosis")
key = W.reference("d1_1_diagnosis")
for pair, causes in key.items():
    W.check(sorted(mine.get(pair, [])) == sorted(causes), f"{pair}: {', '.join(causes)}")

# %% [markdown]
# ## ✱ Stretch · Which figure answers the operations director's question?
#
# Mashael Al-Saadi asks every Sunday: "Are buses leaving when the timetable says, so riders can rely on them?"
# Write two sentences: which figure, and what she must read beside it so that cancellations do not hide.

# %%
STRETCH = """
"""
print(STRETCH.strip() or "✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. The planning figure is almost 15 points below the operations figure for the same month. Is planning's figure wrong?
#    <details><summary>Answer</summary>No. It counts timepoint arrivals, not trips, so later timepoints, where
#    delays have built up, weigh in. A different grain answers a different question.</details>
# 2. The board counts a cancelled trip as late. What does that make its figure sensitive to?
#    <details><summary>Answer</summary>Cancellations: a day with many cancelled trips lowers it even if every bus that
#    ran was punctual.</details>
# 3. Why can two analysts walking the same gap report different sizes for each step?
#    <details><summary>Answer</summary>The steps interact; the size of each depends on the order of the walk. State the
#    order with the table.</details>
#
# **Carry forward.** Your diagnosis table is the LO1 evidence: save it with your notes. Lab 1.2 writes definitions
# that would have prevented it.
