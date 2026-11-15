# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0"]
# ///
# %% [markdown]
# # Lab 1.2 · Four ridership definitions
#
# Day 1 · Session 2 (Anatomy of a metric definition) · 25 min. "Ridership" means four different numbers at Wadi Noor
# Transit. You count all four for the week of 13 to 19 September 2026, write each as a governed definition that
# someone else can compute, run the peer checklist and reconcile every definition to the source totals.
#
# **AI-tutor.** An assistant may explain an error message; it does not write the definitions.
#
# **Reference state.** The warehouse through `W.db()`; `data/catalogue/data_dictionary.md` and
# `data/catalogue/business_questions.md` (questions 1 to 4).
#
# **Tasks**
# - [ ] 1 · Count four ridership numbers for one week (6')
# - [ ] 2 · Write the four definitions in the catalogue template (8')
# - [ ] 3 · Run the peer checklist (5')
# - [ ] 4 · Reconcile each definition to the source totals (6')
# - [ ] ✱ Stretch · Add the Arabic name and a limits line to each definition

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
con = W.db()
W.linked_view(con)   # boarding_linked: every tap, with journey_start = 1 when the card made no tap in the hour before
WEEK = ("2026-09-13", "2026-09-19")
print(Path("data/catalogue/business_questions.md").read_text(encoding="utf-8").split("\n5.")[0])

# %% [markdown]
# ## 1 · Count four ridership numbers for one week (6')
#
# ✏️ **Exercise** · Return the four numbers for service dates 13 to 19 September: card taps, different cards,
# linked journeys (use `boarding_linked.journey_start`) and card-days (one card on one day counts once).

# %%
def four_counts(con) -> dict:
    wk = f"service_date BETWEEN DATE '{WEEK[0]}' AND DATE '{WEEK[1]}'"
    # BEGIN SOLUTION
    return {
        "taps": W.scalar(con, f"SELECT count(*) FROM fct_boarding WHERE {wk}"),
        "unique_cards": W.scalar(con, f"SELECT count(DISTINCT card_id) FROM fct_boarding WHERE {wk}"),
        "journeys": W.scalar(con, f"SELECT sum(journey_start) FROM boarding_linked WHERE {wk}"),
        "rider_days": W.scalar(con, f"SELECT count(DISTINCT (card_id, service_date)) FROM fct_boarding WHERE {wk}"),
    }
    # END SOLUTION


# %%
try:
    counts = four_counts(con)
except NotImplementedError:
    counts = W.reference("d1_2_counts")
for k, v in counts.items():
    print(f"{k:14s} {int(v):>8,}")
W.check(counts["unique_cards"] < counts["rider_days"] < counts["journeys"] < counts["taps"],
        "cards < card-days < journeys < taps: four words, four different numbers")

# %% [markdown]
# 🔍 There are 60% more taps than cards. Which one would you put in a press release as "riders last week", and
# which would you refuse to?
#
# ## 2 · Write the four definitions in the catalogue template (8')
#
# Every definition has ten fields: `name`, `question`, `formula` (one SQL aggregate), `table` (where the formula
# runs), `grain`, `filters`, `time_logic`, `unit`, `owner` ("Name, role") and `limits`. The owners: Muneer
# Al-Thaqafi (data platform lead) for taps and cards, Dhuha Al-Rowais (network planning) for journeys, Yasmeen
# Al-Jaafari (strategy and finance) for card-days.
#
# ✏️ **Exercise** · Write `DEFINITIONS` as YAML text, one block per number, inside `my_definitions()`.

# %%
def my_definitions() -> list[dict]:
    # BEGIN SOLUTION
    DEFINITIONS = """
- name: taps
  question: How many card taps did the network record in the period?
  formula: COUNT(tap_id)
  table: fct_boarding
  grain: one card tap at a validator (fct_boarding)
  filters: none; taps that could not be attributed to a route or trip are counted
  time_logic: service_date; weeks run Sunday to Saturday
  unit: taps
  owner: Muneer Al-Thaqafi, data platform lead
  limits: counts taps, not people; a rider who changes bus taps twice
- name: unique_cards
  question: How many different cards travelled in the period?
  formula: COUNT(DISTINCT card_id)
  table: fct_boarding
  grain: one card tap at a validator (fct_boarding)
  filters: none
  time_logic: service_date; distinct within the period asked for, so weeks do not add up to a month
  unit: cards
  owner: Muneer Al-Thaqafi, data platform lead
  limits: a card is not a person; never shown below 10
- name: journeys
  question: How many journeys did riders make, counting a transfer as part of one journey?
  formula: SUM(journey_start)
  table: boarding_linked
  grain: one card tap, with journey_start = 1 when the card made no tap in the 60 minutes before
  filters: none
  time_logic: service_date of the tap; the 60-minute look-back crosses midnight
  unit: journeys
  owner: Dhuha Al-Rowais, network planning manager
  limits: a return trip within 60 minutes counts as a transfer
- name: rider_days
  question: How many card-days were there in the period?
  formula: COUNT(DISTINCT (card_id, service_date))
  table: fct_boarding
  grain: one card tap at a validator (fct_boarding)
  filters: none
  time_logic: service_date; additive across days
  unit: card-days
  owner: Yasmeen Al-Jaafari, strategy and finance analyst
  limits: used for the day-pass review; not a count of people
"""
    # END SOLUTION
    return yaml.safe_load(DEFINITIONS)


# %%
try:
    defs = my_definitions()
except NotImplementedError:
    defs = W.reference("d1_2_definitions")
print(W.yaml_dump(defs[:1]))

# %% [markdown]
# ## 3 · Run the peer checklist (5')
#
# `W.lint()` is the checklist a colleague runs before a definition enters the catalogue. Fix every finding it prints,
# then exchange definitions with your neighbour: could they compute your number without asking you anything?

# %%
names = [d["name"] for d in defs]
W.check(sorted(names) == sorted(counts), "one definition for each of the four numbers")
for d in defs:
    probs = W.lint(d)
    W.check(not probs, f"{d['name']}: " + ("passes the checklist" if not probs else "; ".join(probs)))

# %% [markdown]
# ## 4 · Reconcile each definition to the source totals (6')
#
# A definition reconciles when its formula, run as written, gives the number you counted from the source. A second
# test: the taps of every route plus the taps with no route add up to all taps.

# %%
for d in defs:
    got = W.measure(con, d, *WEEK)
    W.check(int(got) == int(counts[d["name"]]), f"{d['name']}: the formula gives {int(got):,}, the source {int(counts[d['name']]):,}")
by_route = W.df(con, f"""SELECT coalesce(route_id, '(none)') AS route_id, count(*) AS taps FROM fct_boarding
                         WHERE service_date BETWEEN DATE '{WEEK[0]}' AND DATE '{WEEK[1]}' GROUP BY 1 ORDER BY 1""")
W.check(int(by_route.taps.sum()) == int(counts["taps"]), "taps by route add up to the total")

# %% [markdown]
# ## ✱ Stretch · Arabic names and limits
#
# Add `label_ar` to each definition, and one more sentence to `limits` that names a decision the number should not be
# used for. Compare with `data/catalogue/metric_catalogue.yaml`, the governed catalogue of Day 2.

# %%
catalogue = {m["name"]: m for m in W.yaml_load("data/catalogue/metric_catalogue.yaml")["metrics"]}
for d in defs:
    print(f"{d['name']:14s} label_ar: {d.get('label_ar', '(not yet)')} | catalogue: {catalogue[d['name']]['label_ar']}")

# %% [markdown]
# ## Checkpoint
#
# 1. A director asks for "riders last week". Which of the four numbers answers, and what do you say about it?
#    <details><summary>Answer</summary>None exactly: cards are the nearest to people but a card is not a person.
#    Give unique cards, say what it counts, and never call taps "riders".</details>
# 2. Why must a definition name its `table` and `grain`, when the formula already names the columns?
#    <details><summary>Answer</summary>The same formula on another table, or on a join, counts other rows. The grain
#    says what one counted row is.</details>
# 3. Your journeys definition and a colleague's differ only in the look-back (60 against 90 minutes). Same metric?
#    <details><summary>Answer</summary>No: two definitions, two names, one owner each. The catalogue keeps one.</details>
#
# **Carry forward.** The four definitions join the governed catalogue, `data/catalogue/metric_catalogue.yaml`, which
# Day 2 starts from.
