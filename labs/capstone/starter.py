# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0", "jsonschema>=4.23"]
# ///
"""The capstone starter: validate the fares model, run its test queries, time the dashboard, score the agent.

    cd labs
    uv run python capstone/starter.py validate                 # the model against the Ossie schema and the course rules
    uv run python capstone/starter.py test                     # capstone/test_queries.example.yaml (yours: --tests)
    uv run python capstone/starter.py time                     # the load time of the example dashboard query
    uv run python capstone/starter.py score                    # the agent on capstone/certified.example.yaml

Each command takes --model (default capstone/fares_model_starter.yaml). Every result is also written to
capstone/results/, so the numbers in your README are backed by committed files. Search for CAPSTONE: to see what
you replace.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABS = HERE.parent
sys.path.insert(0, str(LABS))

import wnt as W  # noqa: E402
import wnt_agent as A  # noqa: E402
import wnt_semantic as S  # noqa: E402

RESULTS = HERE / "results"


def _model(path, con, role="fares_analyst"):
    return S.Model(S.load(path), con, role=role)


def cmd_validate(a):
    errs = S.validate(S.load(a.model))
    print("\n".join(errs) if errs else f"{a.model}: valid")
    return 1 if errs else 0


def cmd_test(a):
    con = W.db()
    tests = W.yaml_load(a.tests)["tests"]
    res = S.run_tests(_model(a.model, con), tests)
    RESULTS.mkdir(exist_ok=True)
    res.to_csv(RESULTS / "test_queries.csv", index=False, lineterminator="\n")
    print(f"{int(res.passed.sum())} of {len(res)} test queries pass")
    return 0 if res.passed.all() else 1


def dashboard(model):
    """CAPSTONE: replace with the queries of your dashboard's first screen."""
    return [model.query(["sales.passes_sold", "sales.pass_revenue_sar"], ["sales.product", "dates.gregorian_month"],
                        ["dates.gregorian_month >= '2026-08'"])]


def cmd_time(a):
    con = W.db()
    model = _model(a.model, con)
    con.sql("SELECT count(*) FROM dim_date").df()   # process start-up (imports, first scan) is not the dashboard's time
    _, cold = W.timed(dashboard, model)
    _, warm = W.timed(dashboard, model, repeat=5)
    RESULTS.mkdir(exist_ok=True)
    out = {"first_load_s": round(cold, 3), "best_of_5_s": round(warm, 3), "budget_s": 3}
    (RESULTS / "load_time.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(out)
    return 0 if cold <= 3 else 1


def cmd_score(a):
    con = W.db()
    model = _model(a.model, con)
    cert = W.yaml_load(a.certified)["questions"]
    nabih = A.Agent("semantic", con, model, script=a.stand_in, log=RESULTS / "agent_log.jsonl")
    RESULTS.mkdir(exist_ok=True)
    rows = []
    for c in cert:
        ans = nabih.ask(c)
        rows.append({"id": c["id"], "type": c["type"], "mode": ans["mode"], "value": ans["value"],
                     "refused": ans["refused"], "correct": A.score(ans, c)})
    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "agent_scores.csv", index=False, lineterminator="\n")
    print(df.to_string(index=False))
    print(f"\n{int(df.correct.sum())} of {len(df)} right · mode: {', '.join(df['mode'].unique())}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["validate", "test", "time", "score"])
    p.add_argument("--model", default=HERE / "fares_model_starter.yaml")
    p.add_argument("--tests", default=HERE / "test_queries.example.yaml")
    p.add_argument("--certified", default=HERE / "certified.example.yaml")
    p.add_argument("--stand-in", default=HERE / "stand_in.example.yaml")
    a = p.parse_args(argv)
    return {"validate": cmd_validate, "test": cmd_test, "time": cmd_time, "score": cmd_score}[a.command](a)


if __name__ == "__main__":
    sys.exit(main())
