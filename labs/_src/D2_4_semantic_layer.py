# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0", "jsonschema>=4.23"]
# ///
# %% [markdown]
# # Lab 2.4 · Five metrics in the semantic layer
#
# Day 2 · Session 4 (Metrics in an open specification) · 25 min. The semantic model of Wadi Noor Transit is an
# Apache Ossie document. The starter has the datasets, fields and relationships, and lacks five catalogue metrics. You
# validate it against the Ossie schema, add the five metrics, and run the 25 test queries against their reference
# values: the evidence for the third course outcome.
#
# **AI-tutor.** An assistant may explain a validation error; the metric definitions are yours.
#
# **Reference state.** `data/semantic/model_starter.yaml`, `data/semantic/test_queries.yaml`, the catalogue
# `data/catalogue/metric_catalogue.yaml`, and the course compiler `wnt_semantic.py` (a stand-in for a semantic-layer
# engine such as MetricFlow or Cube).
#
# **Tasks**
# - [ ] 1 · Validate the starter model (4')
# - [ ] 2 · Add the three boardings metrics (7')
# - [ ] 3 · Add the two model-level ratios (6')
# - [ ] 4 · Run the 25 test queries (8')
# - [ ] ✱ Stretch · Run the same queries as the East depot manager

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

import copy
import yaml
import wnt as W
import wnt_semantic as S
con = W.db()
starter = S.load("data/semantic/model_starter.yaml")
TESTS = W.yaml_load("data/semantic/test_queries.yaml")["tests"]
print(f"{starter['name']}: {len(starter['datasets'])} datasets, {len(starter['relationships'])} relationships, "
      f"{len(starter['metrics'])} model metrics; {len(TESTS)} test queries")

# %% [markdown]
# ## 1 · Validate the starter model (4')
#
# `S.validate()` checks the document against the Ossie JSON Schema (version 0.3.0.dev0, copied in
# `data/semantic/`), then the course's rules: names used once, relationships that name declared fields, dataset-scoped
# metrics that stay in their dataset.

# %%
print(S.validate(starter) or "valid")
broken = copy.deepcopy(starter)
broken["datasets"][0]["fields"][0].pop("expression")
print("a field without an expression:", S.validate(broken)[0])
W.check(S.validate(starter) == [], "the starter model is a valid Ossie document")

# %% [markdown]
# 🔍 Open `data/semantic/model_starter.yaml` beside this notebook. Find the `boardings` dataset: its fields are there,
# its metrics are not. Find `nonportable_extensions` at the end: the roles live there, because Ossie defines no access
# rules.
#
# ## 2 · Add the three boardings metrics (7')
#
# A dataset-scoped metric uses the dataset's fields by their bare names. Take the formulas from the catalogue:
# `boardings` (taps, including unattributed ones), `unique_cards` and `journeys`.
#
# ✏️ **Exercise** · Write the three metrics as YAML in `BOARDINGS_METRICS`.

# %%
def boardings_metrics() -> list[dict]:
    # BEGIN SOLUTION
    BOARDINGS_METRICS = """
- name: boardings
  expression: {sql: COUNT(tap_id)}
  description: Card taps, including taps that could not be attributed to a route
  datatype: Integer
- name: unique_cards
  expression: {sql: COUNT(DISTINCT card_id)}
  description: Distinct cards that tapped in the period asked for. Not additive across periods.
  datatype: Integer
- name: journeys
  expression: {sql: SUM(journey_start)}
  description: Linked journeys; a tap within 60 minutes of the same card's previous tap is a transfer
  datatype: Integer
"""
    # END SOLUTION
    return yaml.safe_load(BOARDINGS_METRICS)


# %%
def reference_metrics(names, scope):
    full = S.load("data/semantic/wadi_noor_transit.yaml")
    pool = next(d for d in full["datasets"] if d["name"] == "boardings")["metrics"] if scope == "boardings" else full["metrics"]
    return [m for m in pool if m["name"] in names]


model_doc = copy.deepcopy(starter)
try:
    bm = boardings_metrics()
except NotImplementedError:
    bm = reference_metrics({"boardings", "unique_cards", "journeys"}, "boardings")
next(d for d in model_doc["datasets"] if d["name"] == "boardings")["metrics"] = bm
W.check(S.validate(model_doc) == [], "the model is still valid with the boardings metrics")
m = S.Model(model_doc, con)
print(m.query(["boardings.boardings", "boardings.unique_cards", "boardings.journeys"], [], ["dates.week_start = DATE '2026-09-13'"]))

# %% [markdown]
# ## 3 · Add the two model-level ratios (6')
#
# `on_time_rate` and `cancellation_rate` are ratios of two trip metrics that already exist
# (`trips.on_time_departures`, `trips.departed_trips`, `trips.cancelled_trips`, `trips.scheduled_trips`). A
# model-scoped metric reads a dataset metric with `AGG(dataset.metric)`, so each part is aggregated before the
# division: a ratio of sums, never a mean of ratios.
#
# ✏️ **Exercise** · Write the two metrics as YAML in `RATIOS`.

# %%
def ratio_metrics() -> list[dict]:
    # BEGIN SOLUTION
    RATIOS = """
- name: on_time_rate
  expression: {sql: AGG(trips.on_time_departures) / AGG(trips.departed_trips)}
  description: Share of departed trips that left the first timepoint between 1 minute early and 5 minutes late
  datatype: Decimal
- name: cancellation_rate
  expression: {sql: AGG(trips.cancelled_trips) / AGG(trips.scheduled_trips)}
  description: Share of scheduled trips that did not run
  datatype: Decimal
"""
    # END SOLUTION
    return yaml.safe_load(RATIOS)


# %%
try:
    rm = ratio_metrics()
except NotImplementedError:
    rm = reference_metrics({"on_time_rate", "cancellation_rate"}, "model")
model_doc["metrics"] = rm + model_doc["metrics"]
W.check(S.validate(model_doc) == [], "the model is valid with all five metrics")
m = S.Model(model_doc, con)
print(m.compile(["on_time_rate"], ["routes.route_type"], ["dates.gregorian_month = '2026-09'"]))

# %% [markdown]
# 🔍 Read the SQL above: one common table expression per dataset, the trips aggregated by route type, the division
# last. Where is the as-of join to the route version?
#
# ## 4 · Run the 25 test queries (8')

# %%
results = S.run_tests(m, TESTS)
passed = int(results.passed.sum())
W.check(passed == 25, f"{passed} of 25 test queries return their reference values")
out = W.lab_dir("D2_4") / "wadi_noor_transit.yaml"
W.yaml_dump(model_doc, out)
print("your model:", out.relative_to(Path.cwd()))

# %% [markdown]
# ## ✱ Stretch · The East depot manager
#
# The model's extension defines a second role, `east_depot_manager`, whose rows are limited to East routes. Run test
# t02 as that role, and try to group complaints by their text as the network analyst.

# %%
east = S.Model(model_doc, con, role="east_depot_manager")
print(east.query(["boardings.boardings"], ["routes.depot"], ["dates.gregorian_month = '2026-09'"]))
try:
    m.query(["complaints.complaints"], ["complaints.complaint_text"])
except S.AccessDenied as e:
    print("refused:", e)

# %% [markdown]
# ## Checkpoint
#
# 1. Why is `unique_cards` a dataset-scoped metric and `on_time_rate` a model-scoped one?
#    <details><summary>Answer</summary>unique_cards aggregates one dataset's own field; on_time_rate combines two
#    aggregated metrics with AGG(), which the specification allows only at model scope.</details>
# 2. Another tool imports this file and ignores `nonportable_extensions`. What does it lose?
#    <details><summary>Answer</summary>The roles and the classification labels: the access rules travel with the
#    file but only the course compiler enforces them. Every consumer must enforce them again.</details>
# 3. A test query fails by 0.3%. Is the model wrong, or the reference?
#    <details><summary>Answer</summary>Find out before changing either: compare the SQL the model compiled with the
#    reference query, filter by filter. A test is evidence only if its reference was computed independently.</details>
#
# **Carry forward.** `data/semantic/wadi_noor_transit.yaml`, the reference model, is the starting state of Days 3 and 4.
