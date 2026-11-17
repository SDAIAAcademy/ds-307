"""Dashboard helpers of the DS-307 labs (Day 3): the wireframe checker, small-count suppression, bilingual panels.

    import wnt_dash as D
    D.check_wireframe(spec, brief, model)    # findings of the brief checker ([] is a pass)
    D.suppress(df, "trips", ["on_time_rate"])  # hide values computed from fewer than 10 rows
    D.bar_panel(df, ...)                       # one Altair (Vega-Lite) bar panel, in English or Arabic
    D.page(panels, lang, title, path)          # an HTML page of panels, left to right or right to left
"""

from __future__ import annotations

import json
from pathlib import Path

COMPARISONS = {"target", "prior_period", "peer"}
TEXT = {
    "en": {"dir": "ltr", "target": "Target", "prior": "Usual level", "value": "Last week", "suppressed": "fewer than 10"},
    "ar": {"dir": "rtl", "target": "المستهدف", "prior": "المستوى المعتاد", "value": "الأسبوع الماضي", "suppressed": "أقل من 10"},
}


def check_wireframe(spec: dict, brief: dict, model) -> list[str]:
    """The brief checker: what a reviewer asks of a wireframe before anything is built."""
    out = []
    panels = spec.get("panels", [])
    if spec.get("decision", "").strip() == "":
        out.append("state the decision the dashboard serves, in one sentence")
    if not 1 <= len(panels) <= 6:
        out.append(f"{len(panels)} panels: a decision dashboard has at most six")
    by_id = {q["id"]: q for q in brief["questions"]}
    covered = set()
    for i, p in enumerate(panels, 1):
        name = p.get("title", f"panel {i}")
        q = by_id.get(p.get("question"))
        if q is None:
            out.append(f"{name}: answers no question of the brief")
            continue
        covered.add(q["id"])
        if q["decision"] is False:
            out.append(f"{name}: {q['id']} does not serve the decision; cut it")
        if p.get("metric") not in model.metric_names():
            out.append(f"{name}: '{p.get('metric')}' is not a metric of the semantic model")
        if p.get("comparison") not in COMPARISONS:
            out.append(f"{name}: needs a comparison (target, prior_period or peer)")
        for d in p.get("dimensions", []):
            ds, f = d.split(".", 1)
            if f not in model.fields.get(ds, {}):
                out.append(f"{name}: unknown dimension {d}")
            elif model.classification(ds, f) != "Public":
                out.append(f"{name}: {d} is Restricted and cannot be shown")
        if not p.get("owner"):
            out.append(f"{name}: name the owner who answers for the number")
    for qid, q in by_id.items():
        if q["decision"] is True and qid not in covered:
            out.append(f"{qid} serves the decision and has no panel")
    return out


def suppress(df, count_col: str, value_cols: list[str], threshold: int = 10):
    """Blank the values computed from fewer than `threshold` rows, and keep a flag column."""
    df = df.copy()
    small = df[count_col] < threshold
    for c in value_cols + [count_col]:
        df[c] = df[c].astype(object).where(~small, None)
    df["suppressed"] = small
    return df


def bar_panel(df, label: str, value: str, title: str, lang: str = "en", target=None, prior: str | None = None,
              fmt: str = ".0%", width: int = 420):
    """A horizontal bar panel with an optional target line and prior-period ticks. In Arabic the panel is mirrored:
    bars grow from the right and the labels sit on the right."""
    import altair as alt

    t = TEXT[lang]
    rtl = lang == "ar"
    base = alt.Chart(df).encode(y=alt.Y(f"{label}:N", sort=None, title=None,
                                        axis=alt.Axis(orient="right" if rtl else "left", labelLimit=220)))
    x = alt.X(f"{value}:Q", title=t["value"], axis=alt.Axis(format=fmt, orient="bottom"),
              scale=alt.Scale(reverse=rtl, zero=True))
    layers = [base.mark_bar(color="#0f766e").encode(x=x, tooltip=[label, alt.Tooltip(value, format=fmt)])]
    if prior:
        layers.append(base.mark_tick(color="#c2410c", thickness=3, size=18).encode(
            x=alt.X(f"{prior}:Q", scale=alt.Scale(reverse=rtl)), tooltip=[alt.Tooltip(prior, format=fmt)]))
    if target is not None:
        layers.append(alt.Chart({"values": [{"t": target}]}).mark_rule(color="#1e293b", strokeDash=[6, 4]).encode(
            x=alt.X("t:Q", scale=alt.Scale(reverse=rtl))))
    return alt.layer(*layers).properties(title=alt.TitleParams(title, anchor="end" if rtl else "start"), width=width)


def page(panels: list, lang: str, title: str, path, notes: list[str] = ()) -> Path:
    """Write an HTML page with the panels (Vega-Lite specs) in the reading direction of the language."""
    t = TEXT[lang]
    specs = [p.to_dict() for p in panels]
    divs = "\n".join(f'<div id="p{i}" class="panel"></div>' for i in range(len(specs)))
    note = "".join(f"<li>{n}</li>" for n in notes)
    html = f"""<!doctype html>
<html lang="{lang}" dir="{t['dir']}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/vega@5.30.0"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@5.21.0"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6.26.0"></script>
<style>body{{font-family:system-ui,'IBM Plex Sans Arabic',sans-serif;margin:24px}} .grid{{display:flex;flex-wrap:wrap;gap:24px}}</style>
</head>
<body>
<h1>{title}</h1>
<div class="grid">
{divs}
</div>
<ul>{note}</ul>
<script>
const specs = {json.dumps(specs, ensure_ascii=False)};
specs.forEach((s, i) => vegaEmbed('#p' + i, s, {{actions: false}}));
</script>
</body>
</html>
"""
    path = Path(path)
    path.write_text(html, encoding="utf-8", newline="\n")
    return path
