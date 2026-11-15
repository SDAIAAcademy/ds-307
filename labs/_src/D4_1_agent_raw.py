# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0", "jsonschema>=4.23"]
# ///
# %% [markdown]
# # Lab 4.1 · Ten questions, raw schema
#
# Day 4 · Session 1 (From question to query) · 25 min. Nabih, the network's analytics assistant, is given the
# warehouse schema and nothing else. You ask it ten questions, log every query it runs, mark each answer against the
# certified figure and name what went wrong.
#
# **AI-off for you.** Nabih is the AI here; the marking and the diagnosis are yours.
#
# **Reference state.** The warehouse, `data/agent/certified_questions.yaml` (the certified answers) and, when no model
# key is set, `data/agent/stand_in.yaml` (the scripted stand-in; see the note in task 2).
#
# **Tasks**
# - [ ] 1 · Read the schema the agent is given (4')
# - [ ] 2 · Run the agent on ten questions and log its SQL (8')
# - [ ] 3 · Mark each answer against the governed figure (8')
# - [ ] 4 · Name what went wrong in each wrong answer (5')
# - [ ] ✱ Stretch · Change one line of the instruction and run again

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

import json
import pandas as pd
import wnt as W
import wnt_agent as A
con = W.db()
CERT = {q["id"]: q for q in W.yaml_load("data/agent/certified_questions.yaml")["questions"]}
TEN = [CERT[i] for i in W.reference("d4_lab_4_1")]
OUT = W.lab_dir("D4_1")
LOG = OUT / "nabih_raw.jsonl"
LOG.unlink(missing_ok=True)

# %% [markdown]
# ## 1 · Read the schema the agent is given (4')
#
# This is the whole system prompt of the raw configuration: an instruction and the tables with their columns.

# %%
nabih = A.Agent("raw", con, log=LOG)
print(nabih.system)
print("\nmode:", nabih.mode, "·", "a free hosted model (the key is checked at the first call)" if nabih.live else "the scripted stand-in (no OPENROUTER_API_KEY)")

# %% [markdown]
# 🔍 Compare it with what an analyst learnt on Days 1 and 2. What does the agent not know?
#
# ✏️ **Exercise** · List at least three facts the agent would need and the schema does not give.

# %%
def missing_facts() -> list[str]:
    # BEGIN SOLUTION
    return [
        "on time means 1 minute early to 5 minutes late at the first timepoint, over departed trips only",
        "weeks start on Sunday; the weekend is Friday and Saturday",
        "a journey links taps of one card within 60 minutes; distinct cards do not add across weeks",
        "complaint_text and card_id are Restricted and must not be shown",
        "Hijri months come from dim_date, not from Gregorian months",
    ]
    # END SOLUTION


try:
    facts = missing_facts()
except NotImplementedError:
    facts = []
W.check(len(facts) >= 3, f"{len(facts)} missing facts named")

# %% [markdown]
# ## 2 · Run the agent on ten questions and log its SQL (8')
#
# **About the two modes.** With `OPENROUTER_API_KEY` in `labs/.env`, each question goes to a free hosted model
# (`google/gemma-4-31b-it:free` by default) and the SQL it writes runs here. Without a key, a **scripted stand-in**
# supplies the SQL written for each certified question in `data/agent/stand_in.yaml`; the SQL still runs for real.
# The log records the mode of every answer, so a result never hides how it was produced.
#
# ✏️ **Exercise** · Ask Nabih the ten questions; every call is appended to `artifacts/D4_1/nabih_raw.jsonl`.

# %%
def run_ten() -> list[dict]:
    # BEGIN SOLUTION
    return [nabih.ask(q) for q in TEN]
    # END SOLUTION


# %%
try:
    answers = run_ten()
except NotImplementedError:
    answers = [nabih.ask(q) for q in TEN]
logged = [json.loads(line) for line in LOG.read_text(encoding="utf-8").splitlines()]
W.check(len(logged) == 10, f"{len(logged)} calls logged, each with its query and mode")
for a in answers:
    q = a["query"] if isinstance(a["query"], str) else json.dumps(a["query"])
    print(f"{a['id']}  {a['question']}\n     {('REFUSED: ' + a['note']) if a['refused'] else q}\n     -> {str(a['value'])[:60]}")

# %% [markdown]
# ## 3 · Mark each answer against the governed figure (8')
#
# A certified answer has a value and a tolerance (0 for counts, 0.001 for rates), or says the agent must refuse.
#
# ✏️ **Exercise** · Write `mark(ans, cert)`: True when a refusal was expected and given, or when the value is within
# the tolerance.

# %%
def mark(ans: dict, cert: dict) -> bool:
    # BEGIN SOLUTION
    if cert.get("refuse"):
        return bool(ans["refused"])
    if ans["refused"] or ans["value"] is None or isinstance(ans["value"], str):
        return False
    return abs(float(ans["value"]) - cert["value"]) <= cert["tolerance"] + 1e-9
    # END SOLUTION


# %%
try:
    marks = {a["id"]: mark(a, CERT[a["id"]]) for a in answers}
except NotImplementedError:
    marks = {a["id"]: A.score(a, CERT[a["id"]]) for a in answers}
table = pd.DataFrame([{"id": a["id"], "answer": str(a["value"])[:24], "certified": CERT[a["id"]].get("value", "refuse"),
                       "right": marks[a["id"]]} for a in answers])
W.show(table)
W.check(all(marks[a["id"]] == A.score(a, CERT[a["id"]]) for a in answers), "your marks agree with the scorer")
print(f"right: {sum(marks.values())} of 10")

# %% [markdown]
# ## 4 · Name what went wrong in each wrong answer (5')
#
# The error types (`A.ERROR_TYPES`):

# %%
for k, v in A.ERROR_TYPES.items():
    print(f"{k:11s} {v}")

# %% [markdown]
# ✏️ **Exercise** · For each wrong answer, read its SQL and name the error type.

# %%
def diagnose() -> dict:
    # BEGIN SOLUTION
    return {"Q03": "period", "Q04": "filter", "Q09": "definition", "Q10": "grain", "Q13": "join",
            "Q23": "grain", "Q33": "leak"}
    # END SOLUTION


# %%
try:
    named = diagnose()
except NotImplementedError:
    named = {}
wrong = [i for i, ok in marks.items() if not ok]
W.check(set(wrong) <= set(named), f"every wrong answer has an error type ({len(set(wrong) & set(named))} of {len(wrong)})")
if nabih.mode == "stand-in":
    key = W.reference("d4_errors")
    agree = sum(named.get(i) == key.get(f"{i}/raw") for i in wrong)
    W.check(agree >= len(wrong) - 1, f"{agree} of {len(wrong)} diagnoses agree with the key")
else:
    print("live mode: the model's errors differ from the stand-in's, so there is no key; compare with a neighbour")

# %% [markdown]
# 🔍 Which wrong answers would a director believe? Q10 is 67.1% against a certified 67.0%: off by more than the
# tolerance, and nobody would notice.
#
# ## ✱ Stretch · Change one line of the instruction and run again
#
# Add one line to `nabih.system` (for example the definition of on time) and ask the ten questions again. This needs
# a model key: the stand-in replays the same SQL whatever the instruction says.

# %%
if nabih.live:
    nabih.system += "\nOn time means a departed trip left the first timepoint between 1 minute early and 5 minutes late."
    again = [nabih.ask(q) for q in TEN]
    print("right after the change:", sum(A.score(a, CERT[a["id"]]) for a in again), "of 10")
else:
    print("✱ Stretch needs a working OPENROUTER_API_KEY in labs/.env (a free key from openrouter.ai)")

# %% [markdown]
# ## Checkpoint
#
# 1. The agent's SQL ran without error and returned a number. Why is that not evidence the answer is right?
#    <details><summary>Answer</summary>Valid SQL can compute another measure, period or grain; only the comparison with
#    a certified figure says whether it is right.</details>
# 2. Why log the query of every answer?
#    <details><summary>Answer</summary>The query is the only way to see which definition the agent used, and to
#    diagnose the error type.</details>
# 3. Q33 returned the complaint text. Whose failure is it?
#    <details><summary>Answer</summary>The configuration's: a raw schema gives the agent no way to know what is
#    Restricted, and nothing stops it. Session 2 adds certified refusals; Session 3 adds a layer that enforces them.</details>
#
# **Carry forward.** Lab 4.2 writes the certified answers this lab used.
