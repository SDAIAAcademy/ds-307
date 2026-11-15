# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0", "jsonschema>=4.23", "altair>=5.5", "hijridate>=2.5"]
# ///
# %% [markdown]
# # Lab 0 · Setup check
#
# Run this notebook **before Day 1** (about 5 minutes). It checks:
#
# - the packages and the synthetic warehouse of Wadi Noor Transit,
# - that the semantic model validates and answers a test query,
# - that a query over all card taps runs fast enough on your machine,
# - the model key for Day 4, if you have one (optional).
#
# Everything runs on a laptop CPU or on Colab. Nothing downloads a model: Day 4 uses a free hosted model on OpenRouter
# when you have a key, and a scripted stand-in otherwise.
#
# **Optional, for Day 4:** create a free OpenRouter key at <https://openrouter.ai/keys> and put it in `labs/.env`
# (copy `.env.example`), or on Colab in the 🔑 Secrets panel as `OPENROUTER_API_KEY` with notebook access on.

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

# %% [markdown]
# ## 1 · Packages and the warehouse

# %%
import platform
from importlib.metadata import PackageNotFoundError, version

import pandas as pd
import wnt as W

rows = []
for name in ["duckdb", "pandas", "pyarrow", "pyyaml", "jsonschema", "altair", "hijridate"]:
    try:
        rows.append((name, version(name)))
    except PackageNotFoundError:
        rows.append((name, "MISSING"))
print("Python", platform.python_version(), "|", platform.system())
W.show(pd.DataFrame(rows, columns=["package", "version"]))
W.check(all(v != "MISSING" for _, v in rows), "all packages installed")

con = W.db()
counts = {t: W.scalar(con, f"SELECT count(*) FROM {t}") for t in W.TABLES}
W.show(pd.DataFrame(counts.items(), columns=["table", "rows"]))
W.check(counts["fct_trip"] > 80_000 and counts["fct_boarding"] > 800_000, "the Wadi Noor Transit warehouse is ready")

# %% [markdown]
# ## 2 · The semantic model

# %%
import wnt_semantic as S

model = S.Model(S.load("data/semantic/wadi_noor_transit.yaml"), con)
otr = model.value("on_time_rate", ["dates.gregorian_month = '2026-09'"])
print(f"on-time departures, September 2026: {W.pct(otr)}")
W.check(abs(otr - 0.8065) < 0.001, "the semantic model validates and answers")

# %% [markdown]
# ## 3 · Speed on this machine

# %%
_, secs = W.timed(lambda: W.scalar(con, "SELECT count(DISTINCT card_id) FROM fct_boarding"), repeat=3)
print(f"distinct cards over all taps: {secs:.2f} s")
W.check(secs < 3, "fast enough for the labs" if secs < 3 else "slow: run the labs with WNT_QUICK=1")

# %% [markdown]
# ## 4 · The model key for Day 4 (optional)
#
# With a key, Nabih sends one question to a free model. Without one, the labs use the scripted stand-in and say so
# in every answer. A refused key (`401`) is reported and the stand-in takes over.

# %%
import wnt_agent as A

nabih = A.Agent("semantic", con, model)
ans = nabih.ask({"id": "Q01", "question": "How many card taps were recorded in September 2026?"})
print("mode:", ans["mode"], "|", ans["llm"], "|", ans["value"], "|", ans["note"] or "")
W.check(ans["value"] == 84063, "Nabih answered Q01 through the semantic layer")
if ans["mode"] == "stand-in":
    print("No working key: Day 4 runs with the scripted stand-in. That is enough for every lab.")
