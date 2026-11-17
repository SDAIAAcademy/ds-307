"""A small semantic-layer compiler for Apache Ossie documents (the course's stand-in for MetricFlow or Cube).

    import wnt_semantic as S
    doc = S.load("data/semantic/wadi_noor_transit.yaml")
    S.validate(doc)                          # [] when the document passes the Ossie JSON Schema and the course rules
    m = S.Model(doc, con)
    m.query(["on_time_rate"], ["routes.route_type", "dates.gregorian_month"], where=["dates.gregorian_month = '2026-09'"])
    print(m.compile(...))                    # the SQL it runs

What it does, as a semantic layer engine does:
- each dataset becomes a common table expression of its declared fields (a field is an expression over the source);
- each metric is aggregated in the subquery of its own dataset, joined only along many-to-one relationships
  (from -> to), so a grouping never fans out; a request that would need a one-to-many join is refused;
- metrics of different datasets are aggregated first, then joined on the requested dimensions;
- a model-scoped metric written with AGG(dataset.metric) is computed from those aggregates;
- access: the model's nonportable extension (vendor WADI_NOOR) names roles with a row filter, and fields carry a
  classification; a role may not group by, filter on or select a field above its clearance.
Ossie itself defines no access rules: they ride in the extension, which another tool would ignore.
"""

from __future__ import annotations

import json
import re
from collections import deque
from pathlib import Path

LABS = Path(__file__).resolve().parent
SCHEMA = LABS / "data" / "semantic" / "ossie-schema.json"
VENDOR = "WADI_NOOR"
LEVELS = ["Public", "Restricted", "Secret", "Top Secret"]


class SemanticError(Exception):
    pass


class JoinPathError(SemanticError):
    pass


class AccessDenied(SemanticError):
    pass


def load(path):
    import yaml

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _ext(obj) -> dict:
    for e in obj.get("nonportable_extensions") or []:
        if e.get("vendor_name") == VENDOR:
            return e.get("data") or {}
    return {}


def validate(doc) -> list[str]:
    """Errors against the Ossie JSON Schema, then the course's own rules. An empty list is a pass."""
    import jsonschema

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema)
    errs = [f"schema: {'/'.join(map(str, e.path)) or '(root)'}: {e.message[:160]}" for e in v.iter_errors(doc)]
    if errs:
        return errs
    ds = {d["name"]: d for d in doc["datasets"]}
    for d in doc["datasets"]:
        names = [f["name"] for f in d.get("fields", [])] + [m["name"] for m in d.get("metrics", [])]
        dup = {n for n in names if names.count(n) > 1}
        if dup:
            errs.append(f"dataset {d['name']}: names used twice: {sorted(dup)}")
        for m in d.get("metrics", []):
            for ref in re.findall(r"\b([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\b", _unquoted(m["expression"]["sql"])):
                if ref[0] != "source":
                    errs.append(f"metric {d['name']}.{m['name']}: a dataset-scoped metric names {ref[0]}.{ref[1]}; "
                                "move it to the model-root metrics")
    for r in doc.get("relationships", []):
        for side, cols in (("from", r["from_columns"]), ("to", r["to_columns"])):
            if r[side] not in ds:
                errs.append(f"relationship {r['name']}: unknown dataset {r[side]}")
                continue
            fields = {f["name"] for f in ds[r[side]].get("fields", [])}
            errs += [f"relationship {r['name']}: {r[side]} has no field {c}" for c in cols if c not in fields]
        if r["to"] in ds and ds[r["to"]].get("primary_key") and list(r["to_columns"]) != list(ds[r["to"]]["primary_key"]):
            errs.append(f"relationship {r['name']}: to_columns must be the primary key of {r['to']}")
    names = [m["name"] for m in doc.get("metrics", [])]
    errs += [f"model metric named twice: {n}" for n in sorted({n for n in names if names.count(n) > 1})]
    return errs


def _unquoted(sql: str) -> str:
    return re.sub(r"'[^']*'", "''", sql)


def _qualify(expr: str, dataset: str, fields: set[str]) -> str:
    """Qualify the bare field names of a dataset-scoped expression with the dataset's alias."""
    parts = re.split(r"('[^']*')", expr)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"(?<![\w.])([a-z_][a-z0-9_]*)\b(?!\s*\()",
                          lambda m: f"{dataset}.{m.group(1)}" if m.group(1) in fields else m.group(1), parts[i])
    return "".join(parts)


class Model:
    def __init__(self, doc, con, role: str = "network_analyst"):
        errs = validate(doc)
        if errs:
            raise SemanticError("the document does not validate:\n  " + "\n  ".join(errs[:10]))
        self.doc, self.con, self.role = doc, con, role
        self.ds = {d["name"]: d for d in doc["datasets"]}
        self.fields = {n: {f["name"]: f for f in d.get("fields", [])} for n, d in self.ds.items()}
        self.ds_metrics = {f"{n}.{m['name']}": (n, m) for n, d in self.ds.items() for m in d.get("metrics", [])}
        self.model_metrics = {m["name"]: m for m in doc.get("metrics", [])}
        self.roles = _ext(doc).get("roles", {})
        self.edges = {}
        for r in doc.get("relationships", []):
            self.edges.setdefault(r["from"], []).append(r)

    # ---------- catalogue ----------
    def metric_names(self) -> list[str]:
        return list(self.model_metrics) + list(self.ds_metrics)

    def describe(self) -> str:
        """The metric and dimension catalogue as text (what an agent is given in the semantic configuration)."""
        out = ["Metrics:"]
        for name, m in self.model_metrics.items():
            out.append(f"- {name}: {m.get('description', '')}")
        for name, (_, m) in self.ds_metrics.items():
            out.append(f"- {name}: {m.get('description', '')}")
        out.append("Dimensions (dataset.field):")
        for n, fs in self.fields.items():
            for f in fs.values():
                if f.get("dimension") is not None or f.get("label") == "dimension":
                    tag = "" if self.classification(n, f["name"]) == "Public" else " [Restricted]"
                    out.append(f"- {n}.{f['name']}: {f.get('description', '')}{tag}")
        return "\n".join(out)

    def classification(self, dataset: str, field: str) -> str:
        f = self.fields[dataset].get(field)
        if f is None:
            raise SemanticError(f"{dataset} has no field {field}")
        return _ext(f).get("classification", "Public")

    # ---------- joins ----------
    def path(self, start: str, target: str):
        """Relationships from start to target, many-to-one only (breadth first)."""
        if start == target:
            return []
        seen, q = {start}, deque([(start, [])])
        while q:
            node, p = q.popleft()
            for r in self.edges.get(node, []):
                if r["to"] in seen:
                    continue
                if r["to"] == target:
                    return p + [r]
                seen.add(r["to"])
                q.append((r["to"], p + [r]))
        raise JoinPathError(f"no many-to-one path from {start} to {target}: grouping {start} by {target} would "
                            f"repeat {start} rows (fan-out). Ask for a metric of {target}, or add a relationship.")

    # ---------- compile ----------
    def _refs(self, text: str):
        return re.findall(r"\b([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\b", _unquoted(text))

    def _check_access(self, refs, what):
        rule = self.roles.get(self.role)
        if rule is None:
            raise AccessDenied(f"unknown role {self.role}")
        clearance = LEVELS.index(rule.get("clearance", "Public"))
        for d, f in refs:
            if d not in self.ds:
                raise SemanticError(f"unknown dataset {d} in {what}")
            if LEVELS.index(self.classification(d, f)) > clearance:
                raise AccessDenied(f"role {self.role} may not use {d}.{f} ({self.classification(d, f)}) in {what}")

    def _components(self, metric: str):
        """[(base dataset, aggregate SQL, alias)], and the outer expression of the metric."""
        if metric in self.ds_metrics:
            d, m = self.ds_metrics[metric]
            alias = metric.replace(".", "__")
            return [(d, _qualify(m["expression"]["sql"], d, set(self.fields[d])), alias)], alias
        if metric not in self.model_metrics:
            raise SemanticError(f"no metric named {metric}. Known: {', '.join(self.metric_names())}")
        sql = self.model_metrics[metric]["expression"]["sql"]
        aggs = re.findall(r"AGG\(\s*([a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*)\s*\)", sql)
        if aggs:
            comps, outer = [], sql
            for ref in aggs:
                c, a = self._components(ref)
                comps += c
                outer = re.sub(r"AGG\(\s*" + re.escape(ref) + r"\s*\)", f"CAST({a} AS DOUBLE)", outer)
            return comps, outer
        refs = {d for d, _ in self._refs(sql)}
        base = [d for d in refs if all(self._reachable(d, o) for o in refs)]
        if not base:
            raise JoinPathError(f"metric {metric}: no dataset reaches all of {sorted(refs)} by many-to-one joins")
        alias = metric
        return [(base[0], sql, alias)], alias

    def _reachable(self, a, b):
        try:
            self.path(a, b)
            return True
        except JoinPathError:
            return False

    def compile(self, metrics, dimensions=(), where=(), order_by=None, limit=None) -> str:
        metrics, dimensions, where = list(metrics), list(dimensions), list(where)
        if not metrics:
            raise SemanticError("ask for at least one metric")
        dims = []
        for dname in dimensions:
            if "." not in dname:
                raise SemanticError(f"write dimensions as dataset.field: {dname}")
            d, f = dname.split(".", 1)
            if d not in self.fields or f not in self.fields[d]:
                raise SemanticError(f"unknown dimension {dname}")
            dims.append((d, f))
        self._check_access(dims, "a dimension")
        for w in where:
            self._check_access(self._refs(w), "a filter")
        rule = self.roles.get(self.role, {})
        row_filter = rule.get("row_filter")

        groups, outers = {}, []
        for metric in metrics:
            comps, outer = self._components(metric)
            outers.append((metric, outer))
            for base, agg, alias in comps:
                groups.setdefault(base, {})[alias] = agg
        dim_alias = [(d, f, (f"{d}_{f}" if [x for _, x in dims].count(f) > 1 else f)) for d, f in dims]
        used_ds = set()
        subqueries = []
        for base, aggs in groups.items():
            need = {d for d, _, _ in dim_alias} | {d for w in where for d, _ in self._refs(w)}
            if row_filter:
                need |= {d for d, _ in self._refs(row_filter)}
            for agg in aggs.values():
                need |= {d for d, _ in self._refs(agg)}
            joins, joined = [], {base}
            for target in sorted(need - {base}):
                for r in self.path(base, target):
                    if r["to"] in joined:
                        continue
                    on = " AND ".join(f"{r['from']}.{a} = {r['to']}.{b}" for a, b in zip(r["from_columns"], r["to_columns"]))
                    joins.append(f"LEFT JOIN ds_{r['to']} AS {r['to']} ON {on}")
                    joined.add(r["to"])
            used_ds |= joined
            sel = [f"{d}.{f} AS {a}" for d, f, a in dim_alias] + [f"{agg} AS {al}" for al, agg in aggs.items()]
            conds = list(where) + ([row_filter] if row_filter else [])
            sq = f"SELECT {', '.join(sel)}\n  FROM ds_{base} AS {base}\n  " + "\n  ".join(joins)
            if conds:
                sq += "\n  WHERE " + " AND ".join(f"({c})" for c in conds)
            if dim_alias:
                sq += "\n  GROUP BY " + ", ".join(f"{d}.{f}" for d, f, _ in dim_alias)
            subqueries.append((base, sq))
        ctes = []
        for d in sorted(used_ds):
            src = self.ds[d]["source"].strip()
            src = f"({src})" if " " in src else src
            cols = ", ".join(f"{f['expression']['sql']} AS {f['name']}" for f in self.ds[d].get("fields", []))
            ctes.append(f"ds_{d} AS (SELECT {cols} FROM {src} AS source)")
        for i, (base, sq) in enumerate(subqueries):
            ctes.append(f"agg_{i} AS (\n  {sq}\n)")
        keys = [a for _, _, a in dim_alias]
        frm = "agg_0"
        for i in range(1, len(subqueries)):
            frm += f" FULL OUTER JOIN agg_{i} USING ({', '.join(keys)})" if keys else f" CROSS JOIN agg_{i}"
        short = [n.split(".")[-1] for n, _ in outers]
        names = [s if short.count(s) == 1 and s not in keys else n.replace(".", "__") for s, (n, _) in zip(short, outers)]
        select = keys + [f"{outer} AS {nm}" for nm, (_, outer) in zip(names, outers)]
        sql = "WITH " + ",\n".join(ctes) + f"\nSELECT {', '.join(select)}\nFROM {frm}"
        if order_by or keys:
            sql += f"\nORDER BY {order_by or ', '.join(keys)}"
        if limit:
            sql += f"\nLIMIT {int(limit)}"
        return sql

    def query(self, metrics, dimensions=(), where=(), order_by=None, limit=None):
        return self.con.sql(self.compile(metrics, dimensions, where, order_by, limit)).df()

    def value(self, metric, where=()):
        """One number: a metric with no dimension."""
        return self.query([metric], [], where).iloc[0, 0]


def _same(a, b, rel=1e-9):
    if a is None or b is None or a != a or b != b:
        return (a is None or a != a) and (b is None or b != b)
    if isinstance(a, (int, float)) or isinstance(b, (int, float)):
        try:
            return abs(float(a) - float(b)) <= rel * max(1.0, abs(float(b)))
        except (TypeError, ValueError):
            return False
    return str(a) == str(b)


def run_tests(model, tests, verbose=True):
    """Run test queries ({id, metrics, dimensions, where, expected}) and compare with their reference rows.
    Returns a data frame with one row per test: passed or the first difference."""
    import pandas as pd

    out = []
    for t in tests:
        try:
            got = model.query(t["metrics"], t.get("dimensions", []), t.get("where", []))
            got = got.astype(object).where(got.notna(), None).to_dict("records")
            exp = t["expected"]
            keys = [d.split(".", 1)[1] for d in t.get("dimensions", [])]
            srt = lambda rows: sorted(rows, key=lambda r: tuple(str(r.get(k)) for k in keys))
            got, exp = srt(got), srt(exp)
            if len(got) != len(exp):
                ok, why = False, f"{len(got)} rows, expected {len(exp)}"
            else:
                bad = [(k, g.get(k), e[k]) for g, e in zip(got, exp) for k in e if not _same(g.get(k), e[k])]
                ok, why = not bad, ("" if not bad else f"{bad[0][0]}: got {bad[0][1]}, expected {bad[0][2]}")
        except Exception as e:  # a refusal or an error is a failed test, with its message
            ok, why = False, f"{type(e).__name__}: {str(e)[:120]}"
        out.append({"test": t["id"], "passed": ok, "detail": why})
        if verbose:
            print(("✅ " if ok else "❌ ") + f"{t['id']:4s} {t.get('question', '')[:70]}" + ("" if ok else f"  [{why}]"))
    return pd.DataFrame(out)
