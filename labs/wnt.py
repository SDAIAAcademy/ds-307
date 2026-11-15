"""Shared helpers of the DS-307 labs (case: Wadi Noor Transit).

    import wnt as W
    con = W.db()                  # an in-memory DuckDB connection with the eleven warehouse tables as views
    W.check(cond, "message")      # prints a pass or a fail mark, never stops the notebook
    W.reference("name")           # a supplied reference result, for the safety-net cells
    W.lab_dir("D3_3")             # a scratch folder for one lab's outputs, under artifacts/
    W.yaml_load(path) / W.yaml_dump(obj, path)
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

LABS = Path(__file__).resolve().parent
DATA = LABS / "data"
WAREHOUSE = DATA / "warehouse"
REF = DATA / "reference"
QUICK = os.environ.get("WNT_QUICK", "") not in ("", "0")
TABLES = ["dim_date", "dim_route", "dim_depot", "dim_vehicle", "dim_fare_type", "dim_fare_product",
          "fct_trip", "fct_timepoint", "fct_boarding", "fct_complaint", "fct_fare_sale"]


def pick(full, quick):
    """The small value in quick mode (WNT_QUICK=1), the full one otherwise."""
    return quick if QUICK else full


def posix(path) -> str:
    return Path(path).as_posix()


def ensure_data():
    """Write data/warehouse/ with the generator if it is missing (a clone has it; this is a fallback)."""
    if not (WAREHOUSE / "fct_boarding.parquet").exists():
        import prepare_data
        prepare_data.main()


def db(tables: list[str] | None = None):
    """A fresh in-memory DuckDB connection: one read-only view per warehouse table. Nothing a lab does changes data/."""
    import duckdb

    ensure_data()
    con = duckdb.connect()
    for t in tables or TABLES:
        con.execute(f"CREATE VIEW {t} AS SELECT * FROM read_parquet('{posix(WAREHOUSE / (t + '.parquet'))}')")
    return con


def check(ok, message: str) -> bool:
    print(("✅ " if ok else "❌ ") + message)
    return bool(ok)


def reference(name: str):
    """A reference result written by _tools/make_reference.py, for the cells after an exercise."""
    p = REF / f"{name}.json"
    if not p.exists():
        raise FileNotFoundError(f"no reference named {name} in data/reference/")
    return json.loads(p.read_text(encoding="utf-8"))


def lab_dir(name: str) -> Path:
    """artifacts/<name>/: where a lab writes its own files, so data/ never changes."""
    p = LABS / "artifacts" / name
    p.mkdir(parents=True, exist_ok=True)
    return p


def scalar(con, sql: str):
    return con.execute(sql).fetchall()[0][0]


def df(con, sql: str):
    return con.sql(sql).df()


def show(frame, n: int = 30):
    """Print a data frame as plain text (works in a terminal and in a notebook)."""
    import pandas as pd

    with pd.option_context("display.width", 160, "display.max_columns", 20):
        print(frame.head(n).to_string(index=False))


def yaml_load(path):
    import yaml

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def yaml_dump(obj, path=None) -> str:
    import yaml

    text = yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=110)
    if path:
        Path(path).write_text(text, encoding="utf-8")
    return text


def timed(fn, *args, repeat: int = 1, **kw):
    """Run fn and return (result, best seconds over `repeat` runs)."""
    best, out = float("inf"), None
    for _ in range(repeat):
        t0 = time.perf_counter()
        out = fn(*args, **kw)
        best = min(best, time.perf_counter() - t0)
    return out, best


def pct(x, digits: int = 1) -> str:
    return f"{100 * x:.{digits}f}%"


def close(a, b, tol: float = 1e-6) -> bool:
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False
