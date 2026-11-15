# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0", "jsonschema>=4.23"]
# ///
# %% [markdown]
# # Lab 4.3 · Forty questions, two configurations
#
# Day 4 · Session 3 (With and without the semantic layer) · 25 min. Nabih answered the 40 certified questions twice:
# once writing SQL against the raw warehouse, once asking the semantic layer for governed metrics. You score both
# runs, classify every wrong answer and compare accuracy by question type.
#
# **AI-tutor.** An assistant may help with pandas; the classification rules are yours.
#
# **Reference state.** `data/agent/batch_run.csv` (the batch run) and `data/agent/certified_questions.yaml`. The
# batch run was produced by the scripted stand-in (see Lab 4.1): the queries ran for real, the step from words to
# query was scripted. With a model key, `rerun_live()` below produces your own batch run.
#
# **Tasks**
# - [ ] 1 · Load the batch run and the certified set (3')
# - [ ] 2 · Score each answer (8')
# - [ ] 3 · Classify each wrong answer by error type (8')
# - [ ] 4 · Accuracy by question type and configuration (6')
# - [ ] ✱ Stretch · Find the wrong answers a reader would believe

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

import pandas as pd
import wnt as W
import wnt_agent as A
OUT = W.lab_dir("D4_3")

# %% [markdown]
# ## 1 · Load the batch run and the certified set (3')

# %%
batch = pd.read_csv("data/agent/batch_run.csv", dtype={"value": str})
CERT = {q["id"]: q for q in W.yaml_load("data/agent/certified_questions.yaml")["questions"]}
print(len(batch), "answers ·", batch.config.value_counts().to_dict(), "· mode:", batch["mode"].unique().tolist())
W.show(batch[["id", "type", "config", "value", "refused"]].head(6))


def rerun_live():
    """With OPENROUTER_API_KEY set: your own batch run of the 40 questions (about 80 model calls; free models are
    rate-limited, so allow several minutes)."""
    import wnt_semantic as S
    con = W.db()
    model = S.Model(S.load("data/semantic/wadi_noor_transit.yaml"), con)
    rows = []
    for cfg in ("raw", "semantic"):
        nabih = A.Agent(cfg, con, model if cfg == "semantic" else None, log=OUT / "batch_live.jsonl")
        for c in CERT.values():
            a = nabih.ask(c)
            rows.append({"id": c["id"], "type": c["type"], "config": cfg, "mode": a["mode"], "value": a["value"],
                         "refused": a["refused"], "query": str(a["query"]), "note": a["note"] or ""})
    return pd.DataFrame(rows).astype({"value": str})


# batch = rerun_live()   # uncomment with a key

# %% [markdown]
# ## 2 · Score each answer (8')
#
# ✏️ **Exercise** · Add a column `correct`: a refusal where one is certified, or a number within the tolerance.
# `value` is text in the file (some answers are text); convert with care.

# %%
def number(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def score_all(batch: pd.DataFrame) -> pd.Series:
    # BEGIN SOLUTION
    out = []
    for r in batch.itertuples():
        c = CERT[r.id]
        if c.get("refuse"):
            out.append(bool(r.refused))
        else:
            v = number(r.value)
            out.append(not r.refused and v is not None and abs(v - c["value"]) <= c["tolerance"] + 1e-9)
    return pd.Series(out, index=batch.index)
    # END SOLUTION


# %%
try:
    batch["correct"] = score_all(batch)
except NotImplementedError:
    batch["correct"] = [A.score({"value": number(r.value), "refused": r.refused}, CERT[r.id]) for r in batch.itertuples()]
print(batch.groupby("config").correct.agg(["sum", "count"]))
ref = pd.DataFrame(W.reference("d4_scored"))
if (batch["mode"] == "stand-in").all():
    W.check((batch.correct.values == ref.correct.values).all(), "your scores agree with the reference scores")

# %% [markdown]
# ## 3 · Classify each wrong answer by error type (8')
#
# Read the query of each wrong answer. The types are those of Lab 4.1 (`A.ERROR_TYPES`). A rule that reads the query
# is a start; check what it gets wrong.
#
# ✏️ **Exercise** · Write `classify(row)` returning one error type for a wrong answer.

# %%
wrong = batch[~batch.correct].copy()
for r in wrong.itertuples():
    print(f"{r.id} {r.config:8s} {CERT[r.id]['question'][:70]}\n    {str(r.query)[:150]}")


def classify(r) -> str:
    q, c = str(r.query), CERT[r.id]
    # BEGIN SOLUTION
    if c.get("refuse"):
        return "invented" if "fare_sar" in q or "forecast" in c["question"].lower() or "will" in c["question"] else "leak"
    if "count(c.complaint_id)" in q or ("JOIN fct_complaint" in q and "fct_boarding" in q):
        return "join"
    if "sum(c)" in q or "avg(r)" in q or '"reduce": "sum"' in q or "reduce" in q:
        return "grain"
    if "arr_delay_min" in q or "coalesce(" in q or ("count(*)" in q and "journey" in c["question"]) \
            or ("DISTINCT card_id" in q and "journey" in c["question"]):
        return "definition"
    if "dayofweek" in q or ("status" not in q and "departed" in c["question"]) or \
            ("fct_trip WHERE route_id" in q and "status" not in q):
        return "filter"
    return "period"
    # END SOLUTION


# %%
try:
    wrong["error"] = [classify(r) for r in wrong.itertuples()]
except NotImplementedError:
    key = W.reference("d4_errors")
    wrong["error"] = [key[f"{r.id}/{r.config}"] for r in wrong.itertuples()]
key = W.reference("d4_errors")
if (batch["mode"] == "stand-in").all():
    agree = sum(e == key.get(f"{r.id}/{r.config}") for r, e in zip(wrong.itertuples(), wrong.error))
    W.check(agree >= 0.8 * len(wrong), f"{agree} of {len(wrong)} classifications agree with the key")
print(pd.crosstab(wrong.error, wrong.config))

# %% [markdown]
# ## 4 · Accuracy by question type and configuration (6')
#
# ✏️ **Exercise** · Build the table: one row per question type, one column per configuration, the share right.

# %%
def accuracy_table(batch):
    # BEGIN SOLUTION
    return batch.pivot_table(index="type", columns="config", values="correct", aggfunc="mean").round(3)
    # END SOLUTION


# %%
try:
    acc = accuracy_table(batch)
except NotImplementedError:
    acc = batch.pivot_table(index="type", columns="config", values="correct", aggfunc="mean").round(3)
W.show(acc.reset_index())
acc.to_csv(OUT / "accuracy.csv")
W.check((acc["semantic"] >= acc["raw"]).all(), "the semantic layer is at least as accurate on every type")
print("overall:", batch.groupby("config").correct.mean().round(3).to_dict())

# %% [markdown]
# 🔍 The layer removed every leak: the agent asked for `complaints.complaint_text` and the layer refused. It did not
# remove every error: Q23 summed weekly distinct counts, and Q27 and Q32 asked for the wrong period. Those are
# errors in reading the question, which a layer cannot catch.
#
# ## ✱ Stretch · Find the wrong answers a reader would believe
#
# A wrong figure within 25% of the right one looks normal on a slide. Count them by configuration.

# %%
batch["plausible_wrong"] = [A.plausible({"value": number(r.value), "refused": r.refused}, CERT[r.id])
                            for r in batch.itertuples()]
W.show(batch[batch.plausible_wrong][["id", "config", "value"]].assign(
    certified=lambda d: d.id.map(lambda i: CERT[i]["value"])))

# %% [markdown]
# ## Checkpoint
#
# 1. The raw configuration got 18 of 40 right and the semantic one 37. Which errors did the layer remove?
#    <details><summary>Answer</summary>Definitions, joins and leaks: the layer computes the governed metric and
#    enforces the Restricted fields. Errors in reading the period or the grain of the question remain.</details>
# 2. Why score by question type rather than one overall figure?
#    <details><summary>Answer</summary>The decision is per type: counts may be safe while calendar questions are
#    not.</details>
# 3. Why are plausible wrong answers worse than absurd ones?
#    <details><summary>Answer</summary>An absurd figure is caught by the reader; a plausible one is believed and
#    acted on.</details>
#
# **Carry forward.** Lab 4.4 turns this table into a decision.
