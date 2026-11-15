# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pyarrow>=18", "duckdb>=1.4", "hijridate>=2.5"]
# ///
"""Write the synthetic warehouse of Wadi Noor Transit into data/warehouse/ (fixed seed, same values every run).

    uv run python prepare_data.py           # writes data/warehouse/*.parquet and data/warehouse/schema.md

Everything here is invented: the operator, its routes, its riders and their cards. No real person, card or place.
The problems the labs find are planted on purpose and listed in solutions/answer_key.md.
"""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 307
LABS = Path(__file__).resolve().parent
OUT = LABS / "data" / "warehouse"
START, END = date(2026, 1, 1), date(2026, 10, 31)
REROUTE = date(2026, 6, 1)            # R07 extended to Al-Rawdah Hospital: a type 2 change
EXPRESS_UP = date(2026, 9, 1)         # express frequency doubled, trunk frequency cut (driver shortage)
OUTAGE = (date(2026, 10, 5), date(2026, 10, 8))   # East depot validators write taps without route and trip
FARES = {"adult": 3.00, "student": 1.50, "senior": 0.00, "disability": 0.00}

ROUTES = [
    # id, name_en, name_ar, depot, type, length_km, stops, minutes
    ("R01", "Al-Nakheel to City Centre", "النخيل - وسط المدينة", "North", "trunk", 16.8, 26, 52),
    ("R02", "Al-Wurud Loop", "دائري الورود", "North", "feeder", 9.6, 17, 34),
    ("R03", "University Feeder", "خط الجامعة", "North", "feeder", 8.2, 14, 30),
    ("R04", "North Express", "السريع الشمالي", "North", "express", 21.5, 8, 38),
    ("R05", "Central Trunk", "الخط الرئيس الأوسط", "Central", "trunk", 15.1, 24, 50),
    ("R06", "Old Souq Feeder", "خط السوق القديم", "Central", "feeder", 7.4, 15, 30),
    ("R07", "Al-Rawdah Feeder", "خط الروضة", "Central", "feeder", 11.4, 18, 36),
    ("R08", "Airport Express", "سريع المطار", "Central", "express", 24.0, 6, 40),
    ("R09", "East Trunk", "الخط الرئيس الشرقي", "East", "trunk", 17.6, 27, 54),
    ("R10", "Industrial Area Feeder", "خط المنطقة الصناعية", "East", "feeder", 10.8, 16, 36),
    ("R11", "Al-Faisaliyah Feeder", "خط الفيصلية", "East", "feeder", 9.9, 18, 36),
    ("R12", "East Schools Feeder", "خط مدارس الشرق", "East", "feeder", 8.6, 15, 32),
]
R07_NEW = ("R07", "Al-Rawdah Hospital Feeder", "خط مستشفى الروضة", "Central", "feeder", 15.8, 24, 46)
TYPE_TRIPS = {"trunk": 40, "feeder": 24, "express": 16}       # weekday trips, both directions
TYPE_LOAD = {"trunk": 13.0, "feeder": 6.0, "express": 8.0}     # mean taps per operated trip
TYPE_DELAY = {"trunk": (3.0, 2.0), "feeder": (1.3, 1.3), "express": (0.6, 0.6)}
TYPE_SD = {"trunk": 2.2, "feeder": 1.9, "express": 1.1}  # mean departure, extra at terminal
DEPOT_AR = {"North": "الشمال", "Central": "الوسط", "East": "الشرق"}
TYPE_AR = {"trunk": "رئيس", "feeder": "مغذٍّ", "express": "سريع"}
HIJRI_EN = ["Muharram", "Safar", "Rabi al-Awwal", "Rabi al-Thani", "Jumada al-Ula", "Jumada al-Akhirah", "Rajab",
            "Shaban", "Ramadan", "Shawwal", "Dhu al-Qadah", "Dhu al-Hijjah"]
HIJRI_AR = ["محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان",
            "شوال", "ذو القعدة", "ذو الحجة"]
DOW_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DOW_AR = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]


def dates():
    from hijridate import Gregorian

    rows, d = [], START
    while d <= END:
        h = Gregorian(d.year, d.month, d.day).to_hijri()
        holiday_en = holiday_ar = None
        if h.month == 10 and h.day <= 4:
            holiday_en, holiday_ar = "Eid al-Fitr", "عيد الفطر"
        elif h.month == 12 and 9 <= h.day <= 13:
            holiday_en, holiday_ar = "Eid al-Adha", "عيد الأضحى"
        elif (d.month, d.day) == (2, 22):
            holiday_en, holiday_ar = "Founding Day", "يوم التأسيس"
        elif (d.month, d.day) == (9, 23):
            holiday_en, holiday_ar = "National Day", "اليوم الوطني"
        school = not (date(2026, 6, 25) <= d <= date(2026, 8, 22)) and h.month != 9 and holiday_en is None
        week_start = d - timedelta(days=(d.weekday() + 1) % 7)   # weeks start on Sunday
        rows.append(dict(
            date=d, day_of_week_en=DOW_EN[d.weekday()], day_of_week_ar=DOW_AR[d.weekday()],
            is_weekend=d.weekday() in (4, 5), week_start=week_start, iso_week=d.isocalendar()[1],
            gregorian_month=f"{d.year}-{d.month:02d}", hijri_date=f"{h.year}-{h.month:02d}-{h.day:02d}",
            hijri_year=h.year, hijri_month=h.month, hijri_month_key=f"{h.year}-{h.month:02d}",
            hijri_month_name_en=HIJRI_EN[h.month - 1], hijri_month_name_ar=HIJRI_AR[h.month - 1],
            is_ramadan=h.month == 9, holiday_en=holiday_en, holiday_ar=holiday_ar, is_school_day=school,
        ))
        d += timedelta(days=1)
    return pd.DataFrame(rows)


def routes():
    rows, key = [], 1
    for r in ROUTES:
        if r[0] == "R07":
            rows.append(dict(route_key=key, route_id="R07", route_name_en=r[1], route_name_ar=r[2], depot=r[3],
                             route_type=r[4], length_km=r[5], stop_count=r[6], run_minutes=r[7],
                             valid_from=START, valid_to=REROUTE - timedelta(days=1), is_current=False))
            key += 1
            r = R07_NEW
            rows.append(dict(route_key=key, route_id="R07", route_name_en=r[1], route_name_ar=r[2], depot=r[3],
                             route_type=r[4], length_km=r[5], stop_count=r[6], run_minutes=r[7],
                             valid_from=REROUTE, valid_to=None, is_current=True))
        else:
            rows.append(dict(route_key=key, route_id=r[0], route_name_en=r[1], route_name_ar=r[2], depot=r[3],
                             route_type=r[4], length_km=r[5], stop_count=r[6], run_minutes=r[7],
                             valid_from=START, valid_to=None, is_current=True))
        key += 1
    df = pd.DataFrame(rows)
    df["valid_to"] = pd.to_datetime(df["valid_to"]).dt.date
    return df


def route_on(rid, d):
    if rid == "R07" and d >= REROUTE:
        return R07_NEW
    return next(r for r in ROUTES if r[0] == rid)


def trips_per_day(rtype, d, cal):
    n = TYPE_TRIPS[rtype]
    if d >= EXPRESS_UP:
        n = {"express": 36, "trunk": 24}.get(rtype, n)
    if cal["holiday_en"]:
        n = n // 2
    elif d.weekday() == 4:
        n = n // 2
    elif d.weekday() == 5:
        n = int(n * 0.75)
    return max(n, 2)


def build(rng):
    cal = dates()
    cal_by = {r["date"]: r for r in cal.to_dict("records")}
    trip_rows, vehicles = [], {}
    trip_id = 100000
    for d, c in cal_by.items():
        for r0 in ROUTES:
            rid, depot, rtype = r0[0], r0[3], r0[4]
            r = route_on(rid, d)
            minutes = r[7]
            n = trips_per_day(rtype, d, c)
            first, last = (8 * 60, 26 * 60) if c["is_ramadan"] else (5 * 60 + 30, 23 * 60 + 30)
            headway = (last - first) / n
            pool = math.ceil((minutes + 15) / headway) + 1
            for i in range(n):
                dep_min = first + headway * i
                vid = f"V-{rid}-{(i % pool) + 1:02d}"
                vehicles[vid] = (depot, rid)
                trip_rows.append((trip_id, d, rid, "out" if i % 2 == 0 else "back", dep_min, minutes, vid, rtype, depot))
                trip_id += 1
    t = pd.DataFrame(trip_rows, columns=["trip_id", "service_date", "route_id", "direction", "dep_min",
                                         "sched_minutes", "vehicle_id", "route_type", "depot"])
    n = len(t)
    d = pd.to_datetime(t.service_date)
    t["sched_departure"] = d + pd.to_timedelta(t.dep_min.round(), unit="m")

    # status: cancelled more often in the East, partial trips rare
    p_cancel = np.where(t.depot == "East", 0.045, 0.025)
    u = rng.random(n)
    status = np.where(u < p_cancel, "cancelled", np.where(u < p_cancel + 0.015, "partial", "operated"))
    t["status"] = status

    # delays: by route type, worse in the peaks, a little worse from September (schools back)
    hour = (t.dep_min // 60) % 24
    peak = hour.isin([6, 7, 13, 14, 15]).to_numpy()
    base = t.route_type.map(lambda x: TYPE_DELAY[x][0]).to_numpy()
    extra = t.route_type.map(lambda x: TYPE_DELAY[x][1]).to_numpy()
    sep = (t.service_date >= EXPRESS_UP).to_numpy()
    east = (t.depot == "East").to_numpy()
    sd = t.route_type.map(TYPE_SD).to_numpy()
    dep = base + 1.2 * peak + sep * t.route_type.map({"trunk": 0.12, "feeder": 0.25, "express": 0.0}).to_numpy() + 0.6 * east + rng.normal(0, 1, n) * sd
    express = (t.route_type == "express").to_numpy()
    early = 0.04 + 0.025 * (sep & express)      # the new express timetable runs early
    dep = np.where(rng.random(n) < early, rng.uniform(-3.5, -1.2, n), dep)       # some leave early
    arr = dep + extra + 1.2 * peak + 0.35 * sep + rng.normal(0, 2.8, n)
    dep, arr = np.round(dep, 1), np.round(arr, 1)
    t["dep_delay_min"] = np.where(status == "cancelled", np.nan, dep)
    t["arr_delay_min"] = np.where(status == "operated", arr, np.nan)

    # timepoints: four per trip, delay interpolated from departure to terminal
    tp = []
    for k in range(1, 5):
        frac = (k - 1) / 3
        dk = np.round(dep + (arr - dep) * frac + (rng.normal(0, 1.0, n) if 1 < k < 4 else 0), 1)
        if k == 4:
            dk = arr
        reached = (status == "operated") | ((status == "partial") & (k <= 2))
        sched = t.sched_departure + pd.to_timedelta(t.sched_minutes * frac, unit="m")
        tp.append(pd.DataFrame({"trip_id": t.trip_id, "tp_seq": k, "sched_arrival": sched.dt.floor("min"),
                                "delay_min": np.where(reached, dk, np.nan)}).loc[status != "cancelled"])
    tps = pd.concat(tp, ignore_index=True)
    tps["actual_arrival"] = tps.sched_arrival + pd.to_timedelta(tps.delay_min * 60, unit="s")
    tps = tps.sort_values(["trip_id", "tp_seq"]).reset_index(drop=True)

    # boardings (card taps)
    ops = t[t.status != "cancelled"].copy()
    cal_df = cal.set_index("date")
    dowf = np.select([pd.to_datetime(ops.service_date).dt.day_of_week == 4, pd.to_datetime(ops.service_date).dt.day_of_week == 5],
                     [0.6, 0.8], 1.0)
    ram = ops.service_date.map(cal_df.is_ramadan).to_numpy().astype(bool)
    hol = ops.service_date.map(cal_df.holiday_en).notna().to_numpy()
    school = ops.service_date.map(cal_df.is_school_day).to_numpy().astype(bool)
    oh = (ops.dep_min // 60) % 24
    peakf = np.where(oh.isin([6, 7, 13, 14, 15, 16]), 1.45, np.where(oh >= 21, 0.6, 1.0))
    growth = 1 + 0.0004 * (pd.to_datetime(ops.service_date) - pd.Timestamp(START)).dt.days.to_numpy()
    r07 = ((ops.route_id == "R07") & (ops.service_date >= REROUTE)).to_numpy()
    lam = (ops.route_type.map(TYPE_LOAD).to_numpy() * dowf * peakf * growth * np.where(ram, 0.85, 1.0)
           * np.where(hol, 0.7, 1.0) * np.where(r07, 1.35, 1.0)
           * np.where((ops.route_id == "R12").to_numpy() & ~school, 0.45, 1.0)
           * np.where(ops.status.to_numpy() == "partial", 0.6, 1.0))
    k = rng.poisson(lam)
    idx = np.repeat(np.arange(len(ops)), k)
    b = ops.iloc[idx][["trip_id", "service_date", "route_id", "vehicle_id", "sched_departure", "sched_minutes",
                       "dep_delay_min", "depot"]].reset_index(drop=True)
    m = len(b)
    offset = rng.uniform(0, 0.8, m) * b.sched_minutes.to_numpy() + b.dep_delay_min.fillna(0).to_numpy()
    b["tap_ts"] = (b.sched_departure + pd.to_timedelta(np.round(offset * 60), unit="s"))

    # cards: a skewed pool; each card has one fare type
    n_cards = 46000
    card_type = rng.choice(list(FARES), size=n_cards, p=[0.70, 0.19, 0.08, 0.03])
    weights = rng.pareto(1.6, n_cards) + 0.2
    student_mask = card_type == "student"
    is_school = b.service_date.map(cal_df.is_school_day).to_numpy().astype(bool)
    w_school, w_break = weights / weights.sum(), np.where(student_mask, weights * 0.35, weights)
    w_break = w_break / w_break.sum()
    cards = np.empty(m, dtype=np.int64)
    cards[is_school] = rng.choice(n_cards, size=is_school.sum(), p=w_school)
    cards[~is_school] = rng.choice(n_cards, size=(~is_school).sum(), p=w_break)
    b["card_id"] = cards + 700000
    b["fare_type"] = card_type[cards]
    product = rng.choice(["single", "day_pass", "month_pass"], size=n_cards, p=[0.74, 0.08, 0.18])
    b["product"] = product[cards]
    b["fare_sar"] = np.where(b["product"] == "single", b.fare_type.map(FARES), 0.0)

    # transfers: 11% of taps are followed by a tap of the same card on another route of the same depot
    tr = b.sample(frac=0.11, random_state=SEED).copy()
    others = {dep: [r[0] for r in ROUTES if r[3] == dep] for dep in ("North", "Central", "East")}
    tr["route_id"] = [rng.choice([x for x in others[dp] if x != rr]) for dp, rr in zip(tr.depot, tr.route_id)]
    tr["tap_ts"] = tr.tap_ts + pd.to_timedelta(rng.integers(8 * 60, 45 * 60, len(tr)), unit="s")
    tr["fare_sar"] = 0.0   # a transfer within 60 minutes is free
    # attach the transfer tap to a real trip of that route, near the tap time
    ops_idx = ops.assign(dep_ts=ops.sched_departure).sort_values("dep_ts")
    trs = []
    for rid, g in tr.groupby("route_id"):
        cand = ops_idx[ops_idx.route_id == rid][["trip_id", "dep_ts", "vehicle_id"]]
        g = g.sort_values("tap_ts")
        mg = pd.merge_asof(g.drop(columns=["trip_id", "vehicle_id"]), cand, left_on="tap_ts", right_on="dep_ts",
                           direction="backward")
        trs.append(mg.dropna(subset=["trip_id"]).drop(columns=["dep_ts"]))
    tr = pd.concat(trs, ignore_index=True)
    tr["trip_id"] = tr.trip_id.astype(int)
    tr["service_date"] = tr.tap_ts.dt.date.where(tr.tap_ts.dt.date <= END, END)
    b = pd.concat([b, tr[b.columns]], ignore_index=True).sort_values(["tap_ts", "card_id"]).reset_index(drop=True)
    b["service_date"] = pd.to_datetime(b.service_date).dt.date

    # planted: the East validator update writes taps without route and trip for four days
    out = ((b.depot == "East") & (b.service_date >= OUTAGE[0]) & (b.service_date <= OUTAGE[1])).to_numpy()
    b["route_id"] = b.route_id.where(~out, None)
    b["trip_id"] = b.trip_id.astype("Int64").where(~out, pd.NA)
    b.insert(0, "tap_id", np.arange(5_000_001, 5_000_001 + len(b)))
    taps = b[["tap_id", "tap_ts", "service_date", "trip_id", "route_id", "vehicle_id", "card_id", "fare_type",
              "product", "fare_sar"]]

    trips = t[["trip_id", "service_date", "route_id", "direction", "sched_departure", "sched_minutes", "vehicle_id",
               "status", "dep_delay_min", "arr_delay_min"]].copy()

    veh = pd.DataFrame([(v, dp, rid, "2.4" if dp != "East" else "2.4 to 3.0 on 5 October") for v, (dp, rid) in
                        sorted(vehicles.items())], columns=["vehicle_id", "depot", "home_route", "validator_firmware"])

    return cal, trips, tps, taps, veh, cards_table(card_type, product, n_cards), rng


def cards_table(card_type, product, n):
    return pd.DataFrame({"card_id": np.arange(700000, 700000 + n), "fare_type": card_type, "product": product})


def complaints(rng, trips, cal):
    cats = [("late", "تأخر الحافلة", 0.34), ("crowding", "ازدحام", 0.18), ("driver", "سلوك السائق", 0.12),
            ("card", "البطاقة والأجرة", 0.16), ("cleanliness", "النظافة", 0.08), ("accessibility", "سهولة الوصول", 0.12)]
    tmpl = {
        "late": "انتظرت الحافلة على {r} أكثر من عشرين دقيقة يوم {d}. رقمي {p} للتواصل.",
        "crowding": "الحافلة على {r} مزدحمة جدًا وقت الذروة يوم {d}، لم أستطع الركوب.",
        "driver": "السائق على {r} لم يتوقف عند المحطة يوم {d}. اسمي {n} ورقمي {p}.",
        "card": "خصمت البطاقة مرتين على {r} يوم {d}. رقم البطاقة {c}.",
        "cleanliness": "المقاعد غير نظيفة في حافلة {r} يوم {d}.",
        "accessibility": "المنحدر لا يعمل على حافلة {r} يوم {d} وأنا أستخدم كرسيًا متحركًا. رقمي {p}.",
    }
    names = ["سلمان", "عبير", "فهد", "منيرة", "ريم", "ماجد", "أروى", "بدر"]
    n = 2400
    pick = rng.choice(len(cats), size=n, p=[c[2] for c in cats])
    days = rng.choice(cal.date.to_numpy(), size=n)
    rts = rng.choice([r[0] for r in ROUTES], size=n, p=np.array([2, 1, 1, 1, 2, 1, 1.2, 1, 2.6, 1.4, 1.8, 1]) / 17.0)
    rows = []
    for i in range(n):
        key, ar, _ = cats[pick[i]]
        r = route_on(rts[i], days[i])
        text = tmpl[key].format(r=r[2], d=str(days[i]), p=f"05{rng.integers(10_000_000, 99_999_999)}",
                                n=names[i % len(names)], c=700000 + int(rng.integers(0, 46000)))
        rows.append((900001 + i, days[i], rts[i], key, ar, rng.choice(["app", "call_centre", "web"], p=[.5, .3, .2]), text))
    return pd.DataFrame(rows, columns=["complaint_id", "received_date", "route_id", "category", "category_ar",
                                       "channel", "complaint_text"])


def fare_sales(rng, cards, cal):
    # pass products are bought; single-trip taps pay at the validator (fct_boarding.fare_sar)
    prices = {("day_pass", "adult"): 10.0, ("day_pass", "student"): 5.0, ("month_pass", "adult"): 150.0,
              ("month_pass", "student"): 75.0}
    rows, sid = [], 300001
    days = cal.date.to_list()
    for card, ftype, prod in cards[cards["product"] != "single"].itertuples(index=False):
        if prod == "month_pass":
            buys = list(range(0, len(days), 30))
            start = int(rng.integers(0, 30))
            for s in buys:
                day = days[min(s + start, len(days) - 1)]
                price = prices.get((prod, ftype), 0.0)
                rows.append((sid, day, card, prod, ftype, price, rng.choice(["app", "kiosk"], p=[.7, .3])))
                sid += 1
        else:
            for day in rng.choice(days, size=int(rng.integers(3, 14)), replace=False):
                price = prices.get((prod, ftype), 0.0)
                rows.append((sid, day, card, prod, ftype, price, rng.choice(["app", "kiosk", "driver"], p=[.5, .3, .2])))
                sid += 1
    s = pd.DataFrame(rows, columns=["sale_id", "sale_date", "card_id", "product", "fare_type", "price_sar", "channel"])
    return s.sort_values(["sale_date", "sale_id"]).reset_index(drop=True)


def small_dims():
    depots = pd.DataFrame([("North", "الشمال", "Muneer Al-Thaqafi"), ("Central", "الوسط", "Muneer Al-Thaqafi"),
                           ("East", "الشرق", "Muneer Al-Thaqafi")], columns=["depot", "depot_ar", "data_owner"])
    depots = depots.drop(columns="data_owner")
    fare_types = pd.DataFrame([
        ("adult", "Adult", "بالغ", 3.00, "Public"), ("student", "Student", "طالب", 1.50, "Public"),
        ("senior", "Senior (60 and over)", "كبار السن", 0.00, "Restricted"),
        ("disability", "Person with disability", "ذوو الإعاقة", 0.00, "Restricted"),
    ], columns=["fare_type", "name_en", "name_ar", "single_fare_sar", "card_level_classification"])
    products = pd.DataFrame([
        ("single", "Single trip, free transfer within 60 minutes", "رحلة واحدة مع تحويل مجاني خلال 60 دقيقة", 1),
        ("day_pass", "Day pass", "تذكرة يوم", 1), ("month_pass", "30-day pass", "اشتراك 30 يومًا", 30),
    ], columns=["product", "name_en", "name_ar", "valid_days"])
    return depots, fare_types, products


def main():
    rng = np.random.default_rng(SEED)
    cal, trips, tps, taps, veh, cards, rng = build(rng)
    rts = routes()
    comp = complaints(rng, trips, cal)
    sales = fare_sales(rng, cards, cal)
    depots, fare_types, products = small_dims()
    OUT.mkdir(parents=True, exist_ok=True)
    tables = {
        "dim_date": cal, "dim_route": rts, "dim_depot": depots, "dim_vehicle": veh, "dim_fare_type": fare_types,
        "dim_fare_product": products, "fct_trip": trips, "fct_timepoint": tps, "fct_boarding": taps,
        "fct_complaint": comp, "fct_fare_sale": sales,
    }
    for name, df in tables.items():
        df.to_parquet(OUT / f"{name}.parquet", index=False, compression="zstd")
        print(f"{name:18s} {len(df):>9,} rows")


if __name__ == "__main__":
    main()
