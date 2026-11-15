# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.4", "pandas>=2.2", "pyarrow>=18", "pyyaml>=6.0", "jsonschema>=4.23", "altair>=5.5"]
# ///
# %% [markdown]
# # Lab 3.2 · Three bilingual panels
#
# Day 3 · Session 2 (Comparisons and bilingual layout) · 25 min. You build three panels of the director's wireframe
# from the semantic layer, for the week of 25 to 31 October 2026: on-time departures by route against the 85% target
# and the route's usual level, riders per trip against the week before, and complaints by subject. Then you render them
# in Arabic and English and suppress counts below ten.
#
# **AI-tutor.** An assistant may explain an Altair error; the panels are yours.
#
# **Reference state.** `data/semantic/wadi_noor_transit.yaml`, `data/dashboard/brief.yaml` and the wireframe of
# Lab 3.1 (its reference is in `data/reference/d3_1_wireframe.json`).
#
# **Tasks**
# - [ ] 1 · Query the three panels from the semantic layer (6')
# - [ ] 2 · Add a target and the prior period (7')
# - [ ] 3 · Render the panels in Arabic and English (8')
# - [ ] 4 · Suppress small counts and check the layout (4')
# - [ ] ✱ Stretch · Check the colours for colour-blind readers

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

import re
import pandas as pd
import wnt as W
import wnt_semantic as S
import wnt_dash as D
con = W.db()
model = S.Model(S.load("data/semantic/wadi_noor_transit.yaml"), con)
brief = W.yaml_load("data/dashboard/brief.yaml")
WEEK, PREV, PRIOR4 = "2026-10-25", "2026-10-18", ("2026-09-27", "2026-10-18")
OUT = W.lab_dir("D3_2")

# %% [markdown]
# ## 1 · Query the three panels from the semantic layer (6')
#
# Ask the model, never the raw tables: the definitions are the governed ones. Group routes by `routes.route_id`,
# `routes.route_name_en` and `routes.route_name_ar` so that both languages have labels.
#
# ✏️ **Exercise** · Return the three data frames for the week of 25 October.

# %%
ROUTE = ["routes.route_id", "routes.route_name_en", "routes.route_name_ar"]


def panel_data(week: str) -> dict:
    w = [f"dates.week_start = DATE '{week}'"]
    # BEGIN SOLUTION
    return {
        "on_time": model.query(["on_time_rate", "trips.departed_trips"], ROUTE, w),
        "crowding": model.query(["boardings_per_departed_trip"], ROUTE, w + ["routes.route_id IS NOT NULL"]),
        "complaints": model.query(["complaints.complaints"], ["complaints.category"], w),
    }
    # END SOLUTION


# %%
try:
    data = panel_data(WEEK)
except NotImplementedError:
    data = {k: pd.DataFrame(v) for k, v in W.reference("d3_2_panels").items()}
for k, v in data.items():
    print(k, len(v), "rows")
W.show(data["on_time"].head(4))
ref = W.reference("d3_2_panels")
W.check(all(W.close(a, b["on_time_rate"]) for a, b in zip(data["on_time"].on_time_rate, ref["on_time"])),
        "on-time by route matches the reference")

# %% [markdown]
# ## 2 · Add a target and the prior period (7')
#
# ✏️ **Exercise** · Add `target` (from the brief) and `usual` (the rate over the four weeks before) to the on-time panel,
# `prior` (the week before) to the crowding panel, and `usual` (the weekly mean of the four weeks before) to the
# complaints panel.

# %%
def add_comparisons(data: dict) -> dict:
    # BEGIN SOLUTION
    four = [f"dates.week_start BETWEEN DATE '{PRIOR4[0]}' AND DATE '{PRIOR4[1]}'"]
    usual = model.query(["on_time_rate"], ["routes.route_id"], four).rename(columns={"on_time_rate": "usual"})
    on_time = data["on_time"].merge(usual, on="route_id").assign(target=brief["targets"]["on_time_rate"])
    prev = model.query(["boardings_per_departed_trip"], ["routes.route_id"],
                       [f"dates.week_start = DATE '{PREV}'", "routes.route_id IS NOT NULL"]).rename(
        columns={"boardings_per_departed_trip": "prior"})
    crowding = data["crowding"].merge(prev, on="route_id")
    cu = model.query(["complaints.complaints"], ["complaints.category"], four)
    cu["usual"] = cu.complaints / 4
    complaints = data["complaints"].merge(cu[["category", "usual"]], on="category", how="outer").fillna({"complaints": 0})
    return {"on_time": on_time, "crowding": crowding, "complaints": complaints}
    # END SOLUTION


# %%
try:
    panels = add_comparisons(data)
except NotImplementedError:
    panels = {k: pd.DataFrame(v) for k, v in W.reference("d3_2_compared").items()}
W.check({"target", "usual"} <= set(panels["on_time"].columns), "on-time: a target and the usual level")
W.check("prior" in panels["crowding"].columns, "crowding: the week before")
W.check("usual" in panels["complaints"].columns, "complaints: the usual week")
below = panels["on_time"].query("on_time_rate < target").sort_values("on_time_rate")
print("below the 85% target last week:", ", ".join(below.route_id))

# %% [markdown]
# ## 3 · Render the panels in Arabic and English (8')
#
# `D.bar_panel()` draws one panel; `D.page()` writes the page with the right direction. In Arabic the panel mirrors:
# bars grow from the right, labels sit on the right, and the route names come from `route_name_ar`. Digits stay
# Western in both languages.
#
# ✏️ **Exercise** · Build the three panels in each language and write `dashboard_en.html` and `dashboard_ar.html`.

# %%
TITLES = {
    "en": {"page": "Network week of 25 October 2026", "on_time": "Departures on time, by route",
           "crowding": "Card taps per departed trip", "complaints": "Complaints by subject"},
    "ar": {"page": "أسبوع الشبكة، 25 أكتوبر 2026", "on_time": "الانطلاق في الموعد حسب الخط",
           "crowding": "النقرات لكل رحلة منطلقة", "complaints": "الشكاوى حسب الموضوع"},
}
CAT_AR = {"late": "تأخر الحافلة", "crowding": "ازدحام", "driver": "سلوك السائق", "card": "البطاقة والأجرة",
          "cleanliness": "النظافة", "accessibility": "سهولة الوصول"}


def render(panels: dict, lang: str) -> Path:
    t = TITLES[lang]
    name = "route_name_ar" if lang == "ar" else "route_name_en"
    comp = panels["complaints"].assign(label=lambda d: d.category.map(CAT_AR) if lang == "ar" else d.category)
    # BEGIN SOLUTION
    charts = [
        D.bar_panel(panels["on_time"].sort_values("on_time_rate"), name, "on_time_rate", t["on_time"], lang,
                    target=0.85, prior="usual"),
        D.bar_panel(panels["crowding"].sort_values("boardings_per_departed_trip"), name, "boardings_per_departed_trip",
                    t["crowding"], lang, prior="prior", fmt=".1f"),
        D.bar_panel(comp.dropna(subset=["complaints"]), "label", "complaints", t["complaints"], lang, prior="usual", fmt=".0f"),
    ]
    # END SOLUTION
    return D.page(charts, lang, t["page"], OUT / f"dashboard_{lang}.html",
                  notes=[D.TEXT[lang]["target"] + ": 85%", "Wadi Noor Transit (synthetic data)"])


# %%
pages = {}
for lang in ("en", "ar"):
    try:
        pages[lang] = render(panels, lang)
    except NotImplementedError:
        pages[lang] = None
for lang, p in pages.items():
    if p:
        html = p.read_text(encoding="utf-8")
        W.check(f'dir="{"rtl" if lang == "ar" else "ltr"}"' in html, f"{p.name}: written, direction {'right to left' if lang == 'ar' else 'left to right'}")
        W.check(not re.search("[٠-٩]", html), f"{p.name}: Western digits only")
if pages.get("ar"):
    W.check("خط الروضة" in pages["ar"].read_text(encoding="utf-8") or "خط مستشفى الروضة" in pages["ar"].read_text(encoding="utf-8"),
            "the Arabic page labels routes with their Arabic names")

# %% [markdown]
# 🔍 Open `artifacts/D3_2/dashboard_ar.html` in a browser (it loads Vega from a CDN). Does the eye land on the routes
# below target first, from the right?
#
# ## 4 · Suppress small counts and check the layout (4')
#
# Complaints by subject in one week are small numbers. The model's extension sets the threshold at 10: a count below it
# is not shown, so that a single complainant cannot be singled out.
#
# ✏️ **Exercise** · Suppress the complaint counts below 10 with `D.suppress()`.

# %%
def suppressed(df):
    # BEGIN SOLUTION
    return D.suppress(df, "complaints", ["usual"], threshold=10)
    # END SOLUTION


# %%
try:
    sup = suppressed(panels["complaints"])
except NotImplementedError:
    sup = D.suppress(panels["complaints"], "complaints", ["usual"])
W.show(sup)
W.check(sup.suppressed.any(), f"{int(sup.suppressed.sum())} subjects hidden as 'fewer than 10'")
W.check(sup.loc[sup.suppressed, "complaints"].isna().all(), "no hidden count is still in the data")

# The pages are written again with the suppressed panel; the hidden subjects are listed under it.
panels["complaints"] = sup
for lang in ("en", "ar"):
    try:
        p = render(panels, lang)
        hidden = sup.loc[sup.suppressed, "category"]
        if lang == "ar":
            hidden = hidden.map(CAT_AR)
        html = p.read_text(encoding="utf-8").replace("</ul>", f"<li>{D.TEXT[lang]['suppressed']}: {', '.join(hidden)}</li></ul>")
        p.write_text(html, encoding="utf-8", newline="\n")
        W.check(D.TEXT[lang]["suppressed"] in html, f"{p.name}: the hidden subjects are named, without their counts")
    except NotImplementedError:
        pass

# %% [markdown]
# ## ✱ Stretch · Colours for colour-blind readers
#
# The panels use teal bars and an orange tick for the usual level. Check the contrast of the two colours against white
# and against each other with the WCAG formula, and say whether the meaning survives without colour (it should: the
# tick is a different mark).

# %%
def contrast(a: str, b: str) -> float:
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted([lum(a), lum(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


for a, b in [("#0f766e", "#ffffff"), ("#c2410c", "#ffffff"), ("#0f766e", "#c2410c")]:
    print(f"{a} on {b}: {contrast(a, b):.2f} to 1")

# %% [markdown]
# ## Checkpoint
#
# 1. R09 shows 61% on time against an 85% target, and its usual level is 66%. What does the usual-level tick add?
#    <details><summary>Answer</summary>That R09 is always far below target, not just last week: a reserve bus fixes a
#    bad week, not a timetable that cannot be kept. R11 (76% against a usual 86%) is the bad week.</details>
# 2. Why mirror the bars in Arabic instead of only translating the labels?
#    <details><summary>Answer</summary>A right-to-left reader starts at the right: labels and the start of the bars
#    belong there, or the eye meets the bar ends first.</details>
# 3. A subject had 3 complaints last week. Why hide the number rather than show "3"?
#    <details><summary>Answer</summary>Small counts can point to individuals, and they move by chance; the dashboard
#    says "fewer than 10".</details>
#
# **Carry forward.** These panels are what Lab 3.3 must load in under three seconds.
