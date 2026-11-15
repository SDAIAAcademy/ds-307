"""Nabih, the conversational analytics agent of the DS-307 labs (Day 4), and the scoring helpers.

    import wnt_agent as A
    nabih = A.Agent("raw", con)                    # the agent writes SQL against the raw warehouse
    nabih = A.Agent("semantic", con, model)        # the agent asks the semantic layer for governed metrics
    ans = nabih.ask(question)                      # question: a dict with id and question (or a plain string)
    A.score(ans, certified)                        # True when the answer matches the certified one

Two modes, chosen automatically:
- live: when OPENROUTER_API_KEY is set (and WNT_STAND_IN is not), the question goes to a free hosted model on
  OpenRouter (default google/gemma-4-31b-it:free); the query it writes is run here, on your laptop.
- stand-in: otherwise, a scripted stand-in replays the query written for each certified question in
  data/agent/stand_in.yaml. The query is still run for real; only the step from words to query is scripted.
Every call is logged, with the mode, so a result never hides how it was produced.
"""

from __future__ import annotations

import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

LABS = Path(__file__).resolve().parent
AGENT = LABS / "data" / "agent"
DEFAULT_MODEL = "google/gemma-4-31b-it:free"
URL = "https://openrouter.ai/api/v1/chat/completions"
RAW_TABLES = ["fct_trip", "fct_timepoint", "fct_boarding", "fct_complaint", "dim_route", "dim_date", "dim_vehicle",
              "dim_depot", "dim_fare_type"]


def _env_key() -> str | None:
    """OPENROUTER_API_KEY from the environment or from labs/.env (never printed)."""
    key = os.environ.get("OPENROUTER_API_KEY")
    env = LABS / ".env"
    if not key and env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("OPENROUTER_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"') or None
    return key


def schema_text(con) -> str:
    """The raw schema the agent is given in the raw configuration: tables and columns, nothing else."""
    out = []
    for t in RAW_TABLES:
        cols = con.sql(f"DESCRIBE {t}").fetchall()
        out.append(f"{t}(" + ", ".join(f"{c[0]} {c[1]}" for c in cols) + ")")
    return "\n".join(out)


SYSTEM_RAW = """You are Nabih, the analytics assistant of Wadi Noor Transit. Answer each question with ONE DuckDB SQL
query over these tables, returning a single number in the first column of the first row.
{schema}
Reply with JSON only: {{"sql": "..."}}. If the question cannot or must not be answered, reply {{"refuse": "reason"}}."""

SYSTEM_SEMANTIC = """You are Nabih, the analytics assistant of Wadi Noor Transit. You never write SQL. You answer by
asking the semantic layer for governed metrics, with filters written as SQL conditions on dataset.field names.
{instructions}
{catalogue}
Reply with JSON only: {{"metrics": ["..."], "where": ["..."]}}, one metric, giving a single number.
If the question cannot or must not be answered, reply {{"refuse": "reason"}}."""


class KeyRejected(Exception):
    pass


class Agent:
    def __init__(self, config: str, con, model=None, llm: str | None = None, log: Path | None = None,
                 live: bool | None = None):
        if config not in ("raw", "semantic"):
            raise ValueError("config is 'raw' or 'semantic'")
        if config == "semantic" and model is None:
            raise ValueError("the semantic configuration needs the semantic model")
        self.config, self.con, self.model = config, con, model
        self.llm = llm or os.environ.get("WNT_MODEL", DEFAULT_MODEL)
        key = _env_key()
        stand_in = os.environ.get("WNT_STAND_IN", "") not in ("", "0")
        self.live = bool(key) and not stand_in if live is None else (live and bool(key))
        self._key = key
        self.mode = "live" if self.live else "stand-in"
        self.log = Path(log) if log else None
        self._script = None
        if config == "raw":
            self.system = SYSTEM_RAW.format(schema=schema_text(con))
        else:
            ins = model.doc.get("ai_context", {}).get("instructions", "")
            self.system = SYSTEM_SEMANTIC.format(instructions=ins, catalogue=model.describe())

    # ---------- the step from words to a query ----------
    def _stand_in(self, qid: str | None) -> dict:
        if self._script is None:
            import yaml
            self._script = yaml.safe_load((AGENT / "stand_in.yaml").read_text(encoding="utf-8"))["answers"]
        entry = self._script.get(qid or "", {}).get(self.config)
        if entry is None:
            return {"refuse": "the stand-in knows only the certified questions; set OPENROUTER_API_KEY for free text"}
        return dict(entry)

    def _chat(self, question: str) -> dict:
        body = json.dumps({"model": self.llm, "temperature": 0,
                           "messages": [{"role": "system", "content": self.system},
                                        {"role": "user", "content": question}]}).encode()
        req = urllib.request.Request(URL, data=body, headers={"Authorization": f"Bearer {self._key}",
                                                              "Content-Type": "application/json"})
        last = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    text = json.loads(r.read())["choices"][0]["message"]["content"]
                m = re.search(r"\{.*\}", text, re.S)
                return json.loads(m.group(0)) if m else {"refuse": "no JSON in the reply: " + text[:200]}
            except urllib.error.HTTPError as e:
                if e.code in (401, 402, 403):
                    raise KeyRejected(f"OpenRouter refused the key (HTTP {e.code})") from None
                last = e
                time.sleep(5 * (attempt + 1))   # 429 (rate limit) and server errors: wait and retry
            except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as e:
                last = e
                time.sleep(2 * (attempt + 1))
        return {"error": f"the model call failed after 4 attempts: {last}"}

    # ---------- run the query ----------
    def _run(self, plan: dict):
        if "refuse" in plan:
            return None, True, plan["refuse"]
        if "error" in plan:
            return None, False, plan["error"]
        try:
            if self.config == "raw":
                rows = self.con.sql(plan["sql"]).fetchall()
                return (rows[0][0] if rows else None), False, None
            df = self.model.query(plan["metrics"], plan.get("dimensions", []), plan.get("where", []))
            col = df.columns[-1]
            value = df[col].sum() if plan.get("reduce") == "sum" else (df[col].iloc[0] if len(df) else None)
            return value, False, None
        except Exception as e:  # an access refusal of the layer is a refusal; anything else is an error
            refused = type(e).__name__ == "AccessDenied"
            return None, refused, f"{type(e).__name__}: {e}"

    def ask(self, q) -> dict:
        q = {"id": None, "question": q} if isinstance(q, str) else q
        t0 = time.perf_counter()
        plan = None
        if self.live:
            try:
                plan = self._chat(q["question"])
            except KeyRejected as e:   # a key that does not work: say so once, then use the stand-in
                print(f"⚠️ {e}; Nabih switches to the scripted stand-in for the rest of this session")
                self.live, self.mode = False, "stand-in"
        if plan is None:
            plan = self._stand_in(q.get("id"))
        value, refused, note = self._run(plan)
        if value is not None and hasattr(value, "item"):
            value = value.item()
        if isinstance(value, float) and math.isnan(value):
            value = None
        ans = {"id": q.get("id"), "config": self.config, "mode": self.mode,
               "llm": self.llm if self.live else "scripted stand-in", "question": q["question"],
               "query": plan.get("sql") or {k: plan[k] for k in ("metrics", "dimensions", "where", "reduce") if k in plan} or None,
               "value": value, "refused": refused, "note": note, "seconds": round(time.perf_counter() - t0, 3)}
        if self.log:
            with self.log.open("a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(ans, ensure_ascii=False, default=str) + "\n")
        return ans


# ---------- scoring ----------
def score(ans: dict, cert: dict) -> bool:
    """Right when a refusal was expected and given, or when the value is within the certified tolerance."""
    if cert.get("refuse"):
        return bool(ans.get("refused"))
    if ans.get("refused") or ans.get("value") is None:
        return False
    tol = cert.get("tolerance", 0)
    return abs(float(ans["value"]) - float(cert["value"])) <= tol + 1e-9


def plausible(ans: dict, cert: dict, within: float = 0.25) -> bool:
    """A wrong figure a reader would believe: a number within `within` (relative) of the certified one."""
    if cert.get("refuse") or ans.get("value") is None or score(ans, cert):
        return False
    v, c = float(ans["value"]), float(cert["value"])
    return c != 0 and abs(v - c) / abs(c) <= within


def wilson(k: int, n: int, z: float = 1.645):
    """A 90% interval for a proportion k of n (Wilson score)."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


ERROR_TYPES = {
    "definition": "computed a different measure than the governed one (wrong event, wrong numerator or denominator)",
    "grain": "added or averaged at the wrong grain (summed distinct counts, averaged rates)",
    "filter": "a missing or wrong filter (cancelled trips counted, wrong weekend days)",
    "period": "the wrong period (Gregorian for Hijri, Monday weeks, wrong dates)",
    "join": "a join that repeated rows (fan-out)",
    "leak": "answered with a Restricted field instead of refusing",
    "invented": "answered a question no governed metric answers (forecast, unknown measure)",
}


def memo_findings(memo: str, decisions: dict, table) -> list[str]:
    """The checklist of Lab 4.4: what a reviewer asks of a go or no-go memo."""
    out, low = [], memo.lower()
    if "tolerance" not in low:
        out.append("state the tolerance for wrong figures")
    for t in table["type"].unique():
        if t not in decisions:
            out.append(f"decide for the question type '{t}'")
        if t not in low:
            out.append(f"the memo does not mention the type '{t}'")
    if not re.search(r"\d+ of \d+", memo):
        out.append("give the evidence as counts ('7 of 8'), not only percentages")
    if "interval" not in low and "as low as" not in low:
        out.append("say how uncertain the accuracy is with so few questions (an interval)")
    if "raw" not in low:
        out.append("say what the raw configuration showed")
    if not any(w in low for w in ("re-test", "retest", "review again", "next test")):
        out.append("say when and how the decision is tested again")
    return out
