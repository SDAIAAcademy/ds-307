# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0", "jsonschema>=4.23", "altair>=5.5"]
# ///
# %% [markdown]
# # Lab 3.1 · A wireframe from the brief
#
# Day 3 · Session 1 (Dashboards start from a decision) · 25 min. Mashael Al-Saadi, the operations director, wrote a
# brief with nine questions. You turn it into a wireframe specification: the decision in one sentence, at most six
# panels, each with its question, governed metric, comparison and owner. Then the brief checker reviews it.
#
# **AI-off.** The choice of panels is the design skill; make it yourself.
#
# **Reference state.** `data/dashboard/brief.yaml` and the semantic model `data/semantic/wadi_noor_transit.yaml`.
#
# **Tasks**
# - [ ] 1 · Read the brief: audience, decision, cadence (5')
# - [ ] 2 · Turn each question into a panel with a comparison (10')
# - [ ] 3 · Cut to six panels and order them (5')
# - [ ] 4 · Run the brief checker (5')
# - [ ] ✱ Stretch · One panel for a reader who reads Arabic only

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

import yaml
import wnt as W
import wnt_semantic as S
import wnt_dash as D
con = W.db()
model = S.Model(S.load("data/semantic/wadi_noor_transit.yaml"), con)
brief = W.yaml_load("data/dashboard/brief.yaml")

# %% [markdown]
# ## 1 · Read the brief: audience, decision, cadence (5')

# %%
for k in ("owner", "audience", "decision", "cadence", "load_time_budget_seconds", "targets"):
    print(f"{k}: {brief[k]}")
print()
for q in brief["questions"]:
    print(f"{q['id']}  {q['text']}")

# %% [markdown]
# 🔍 Which questions change where a reserve bus goes on Sunday? Mark each in your head: decides, gives context, drills
# down, or does not belong here. The brief's own marks are in `brief.yaml`; read them after you decide.
#
# The metrics you may use (the semantic model's catalogue):

# %%
print(model.describe())

# %% [markdown]
# ## 2 · Turn each question into a panel with a comparison (10')
#
# A panel is a question, a governed metric, the dimensions it is split by, a comparison (`target`, `prior_period` or
# `peer`) and the owner who answers for the number.
#
# ## 3 · Cut to six panels and order them (5')
#
# Keep the panels the decision needs, the context panel if there is room, and leave out the rest. Order them as the
# director reads: the decision drivers first.
#
# ✏️ **Exercise** · Write the wireframe as YAML in `WIREFRAME` (tasks 2 and 3 together).

# %%
def wireframe() -> dict:
    # BEGIN SOLUTION
    WIREFRAME = """
decision: Where to place the six reserve buses and the four field supervisors next week, by depot and route.
panels:
  - title: Routes leaving late
    question: Q1
    metric: on_time_rate
    dimensions: [routes.route_id]
    comparison: target
    also: the route's level over the four weeks before
    owner: Tawfiq Al-Sahafi, control centre
  - title: Trips that did not run
    question: Q2
    metric: cancellation_rate
    dimensions: [routes.depot]
    comparison: prior_period
    owner: Tawfiq Al-Sahafi, control centre
  - title: Riders per trip (crowding)
    question: Q3
    metric: boardings_per_departed_trip
    dimensions: [routes.route_id]
    comparison: prior_period
    owner: Dhuha Al-Rowais, network planning
  - title: Complaints by subject
    question: Q4
    metric: complaints.complaints
    dimensions: [complaints.category]
    comparison: prior_period
    owner: Yasmeen Al-Jaafari, strategy and finance
  - title: Network taps
    question: Q5
    metric: boardings.boardings
    dimensions: []
    comparison: prior_period
    owner: Muneer Al-Thaqafi, data platform
drill_through: Q9, average delay by timepoint, opened from a route in the first panel
left_out: [Q6 revenue belongs to finance, Q7 card numbers are Restricted, Q8 a forecast is not this decision]
"""
    # END SOLUTION
    return yaml.safe_load(WIREFRAME)


# %%
try:
    spec = wireframe()
except NotImplementedError:
    spec = W.reference("d3_1_wireframe")
for i, p in enumerate(spec["panels"], 1):
    print(f"{i}. {p['title']:28s} {p['question']}  {p['metric']:30s} by {', '.join(p['dimensions']) or '(none)':18s} vs {p['comparison']}")

# %% [markdown]
# ## 4 · Run the brief checker (5')
#
# First, the director's own wish list: one panel per question. Then yours.

# %%
wish = {"decision": brief["decision"], "panels": [
    {"title": q["id"], "question": q["id"], "metric": m, "dimensions": d, "comparison": c, "owner": "?"}
    for q, m, d, c in zip(brief["questions"],
                          ["on_time_rate", "cancellation_rate", "boardings_per_departed_trip", "complaints.complaints",
                           "boardings.boardings", "fare_revenue", "boardings.unique_cards", "ridership_forecast",
                           "timepoint_on_time_rate"],
                          [["routes.route_id"], ["routes.depot"], ["routes.route_id"], ["complaints.category"], [], [],
                           ["boardings.card_id"], [], ["timepoints.tp_seq"]],
                          ["target", "prior_period", None, None, "prior_period", None, None, None, None])]}
print("The wish list:")
for f in D.check_wireframe(wish, brief, model):
    print("  -", f)
print("\nYour wireframe:")
findings = D.check_wireframe(spec, brief, model)
print("  " + ("\n  ".join(findings) if findings else "no findings"))
W.check(not findings, "the wireframe passes the brief checker")
W.check(len(spec["panels"]) <= 6, f"{len(spec['panels'])} panels")
W.check(spec["panels"][0]["question"] in ("Q1", "Q2", "Q3"), "the first panel serves the decision directly")

# %% [markdown]
# ## ✱ Stretch · A panel for a reader who reads Arabic only
#
# Add `title_ar` to each panel and check that every route the first panel shows has an Arabic name in the model
# (`routes.route_name_ar`).

# %%
def arabic_titles() -> dict:
    # BEGIN SOLUTION
    return {"Routes leaving late": "خطوط تنطلق متأخرة", "Trips that did not run": "رحلات لم تُسيَّر",
            "Riders per trip (crowding)": "الركاب لكل رحلة (الازدحام)", "Complaints by subject": "الشكاوى حسب الموضوع",
            "Network taps": "نقرات الشبكة"}
    # END SOLUTION


try:
    for p in spec["panels"]:
        print(p["title"], "|", arabic_titles()[p["title"]])
    print(model.query(["boardings.boardings"], ["routes.route_id", "routes.route_name_ar"], ["routes.is_current"]).head(3))
except NotImplementedError:
    print("✱ Stretch not attempted")

# %% [markdown]
# ## Checkpoint
#
# 1. Q6 (revenue by product) is a good question. Why is it not on this dashboard?
#    <details><summary>Answer</summary>It does not change where a reserve bus goes on Sunday. It belongs to a finance
#    dashboard with its own audience and decision.</details>
# 2. Why must every panel carry a comparison?
#    <details><summary>Answer</summary>A number alone does not say whether to act. Against a target, the week before or
#    a peer route, it says "worse than expected here".</details>
# 3. Why name an owner on each panel?
#    <details><summary>Answer</summary>When a figure is questioned in the meeting, someone answers for its definition;
#    it is the owner from the catalogue.</details>
#
# **Carry forward.** The first three panels are built in Lab 3.2; the load-time budget is met in Lab 3.3.
