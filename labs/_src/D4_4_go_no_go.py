# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0", "jsonschema>=4.23"]
# ///
# %% [markdown]
# # Lab 4.4 · The go or no-go memo
#
# Day 4 · Session 4 (What the agent may answer) · 25 min. Mashael wants Nabih in the depot managers' chat. From the
# scoring table of the batch run and her stated tolerance, you decide for each question type whether Nabih answers
# alone, answers with review, or refuses, and you write the memo that carries the decision.
#
# **AI-off for the decision.** An assistant may tidy your sentences; the decisions and the evidence are yours.
#
# **Reference state.** `data/agent/scoring_table.csv` (accuracy by question type and configuration, with 90%
# intervals and the count of plausible wrong answers).
#
# **Tasks**
# - [ ] 1 · Read the scoring table and the tolerance (4')
# - [ ] 2 · Decide per question type (8')
# - [ ] 3 · Draft the memo with its evidence (10')
# - [ ] 4 · Check the memo against the checklist (3')
# - [ ] ✱ Stretch · Name the result that would change your decision

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
OUT = W.lab_dir("D4_4")

# %% [markdown]
# ## 1 · Read the scoring table and the tolerance (4')

# %%
table = pd.read_csv("data/agent/scoring_table.csv")
W.show(table)
TOLERANCE = ("A figure Nabih gives without review may be wrong at most once in twenty answers (95% right). "
             "Restricted data is never shown, whatever the accuracy.")
print("\nMashael's tolerance:", TOLERANCE)

# %% [markdown]
# 🔍 Read the `low90` column of the semantic rows. Eight of eight right is consistent with a true accuracy as low as
# 75%: eight questions cannot prove 95%. The decision must say so.
#
# The decision rule agreed with Mashael:
#
# - **refuse**: the type asks for Restricted data or for something no governed metric answers;
# - **answer**: every answer of the type was right in the semantic configuration, with no plausible wrong answer;
#   allowed while the certified set grows to 30 questions per type, and withdrawn at the first wrong figure;
# - **review**: otherwise; an analyst checks each figure before it is sent.
#
# ✏️ **Exercise** · Decide for each type, with the semantic configuration (the raw one is not a candidate).

# %%
def decide(table: pd.DataFrame) -> dict:
    sem = table[table.config == "semantic"].set_index("type")
    # BEGIN SOLUTION
    out = {}
    for t, r in sem.iterrows():
        if t == "restricted":
            out[t] = "refuse"
        elif r.correct == r.questions and r.plausible_wrong == 0:
            out[t] = "answer"
        else:
            out[t] = "review"
    return out
    # END SOLUTION


# %%
try:
    decisions = decide(table)
except NotImplementedError:
    decisions = {"count": "answer", "ratio": "answer", "distinct": "review", "calendar": "review", "restricted": "refuse"}
print(decisions)
W.check(decisions == {"count": "answer", "ratio": "answer", "distinct": "review", "calendar": "review",
                      "restricted": "refuse"}, "the decisions follow the rule")

# %% [markdown]
# ## 3 · Draft the memo with its evidence (10')
#
# One page: the decision per type with its evidence as counts, how uncertain the evidence is, what the raw
# configuration showed, and when the decision is tested again.
#
# ✏️ **Exercise** · Write the memo in `memo()`.

# %%
def memo() -> str:
    # BEGIN SOLUTION
    sem = table[table.config == "semantic"].set_index("type")
    raw = table[table.config == "raw"].set_index("type")
    line = lambda t: f"{sem.loc[t, 'correct']} of {sem.loc[t, 'questions']} right"  # noqa: E731
    return f"""# Nabih in the depot managers' chat: decision by question type

To: Mashael Al-Saadi, operations director. From: network analytics. Data to 31 October 2026.

**Tolerance.** {TOLERANCE}

**Decision.** Nabih answers through the semantic layer only. The raw configuration is not used: it got
{int(raw.correct.sum())} of 40 right, leaked Restricted complaint text and card data in 4 answers, and gave
{int(raw.plausible_wrong.sum())} wrong figures a reader would believe.

| Question type | Semantic layer | Decision |
|---|---|---|
| count | {line('count')} | answer |
| ratio | {line('ratio')} | answer |
| distinct | {line('distinct')} (summed weekly distinct cards) | review |
| calendar | {line('calendar')} (wrong week start, Gregorian for Hijri) | review |
| restricted | {line('restricted')} refused; the layer enforces it | refuse |

**How sure we are.** Eight questions per type is little evidence: 8 of 8 is consistent with an accuracy as low as
75% (90% interval). "Answer" is therefore provisional.

**Next test.** We grow the certified set to 30 questions per type by 30 November and re-test every month and after
any change of model or semantic layer. A single wrong figure in a type moves it to review at once.
"""
    # END SOLUTION


# %%
try:
    text = memo()
except NotImplementedError:
    text = ""
(OUT / "memo.md").write_text(text, encoding="utf-8")
print(text)

# %% [markdown]
# ## 4 · Check the memo against the checklist (3')

# %%
findings = A.memo_findings(text, decisions, table)
print("\n".join("- " + f for f in findings) or "no findings")
W.check(not findings, "the memo passes the checklist")

# %% [markdown]
# ## ✱ Stretch · Name the result that would change your decision
#
# For each "answer" type, how many right answers out of 30 would keep the 90% interval's lower end above 90%?

# %%
for k in range(30, 24, -1):
    lo, hi = A.wilson(k, 30)
    print(f"{k} of 30: interval {lo:.1%} to {hi:.1%}")

# %% [markdown]
# ## Checkpoint
#
# 1. Ratio questions were 8 of 8 right. Why is "answer" still provisional?
#    <details><summary>Answer</summary>Eight questions allow a true accuracy as low as 75%; the decision stands only
#    while the larger test is run.</details>
# 2. Why is "refuse" the decision for Restricted questions even though the agent refused all eight?
#    <details><summary>Answer</summary>The tolerance for showing Restricted data is zero; the type is closed by rule,
#    and the layer enforces it.</details>
# 3. What would you tell a depot manager who asks why distinct-card questions take longer?
#    <details><summary>Answer</summary>One answer in eight was wrong in a way a reader would not see, so an analyst
#    checks those figures before they are sent.</details>
#
# **Carry forward.** The capstone repeats this evaluation on the fares and concessions area.
