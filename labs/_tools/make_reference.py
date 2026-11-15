"""Write data/reference/*.json: the results the safety-net cells use when an exercise is not done yet.

    uv run python _tools/make_reference.py           # from labs/

Each value is computed here with plain SQL, independently of the lab solutions, from the warehouse the generator
wrote. Run it after prepare_data.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LABS))
import wnt as W  # noqa: E402

REF = LABS / "data" / "reference"
OUT = {}


def put(name, value):
    OUT[name] = value


def day1(con):
    q = lambda s: W.scalar(con, s)
    put("d1_1_figures", {
        "operations": q("SELECT avg((dep_delay_min BETWEEN -1 AND 5)::INT) FROM fct_trip WHERE status <> 'cancelled' "
                        "AND month(service_date) = 9"),
        "planning": q("SELECT avg((p.delay_min BETWEEN -1 AND 5)::INT) FROM fct_timepoint p JOIN fct_trip t USING (trip_id) "
                      "WHERE p.delay_min IS NOT NULL AND month(t.service_date) = 9"),
        "board": q("SELECT avg((t.status = 'operated' AND coalesce(t.arr_delay_min <= 5, false))::INT) FROM fct_trip t "
                   "JOIN dim_date d ON d.date = t.service_date WHERE d.hijri_month_key = '1448-04'"),
    })
    put("d1_1_walk", [
        {"label": "measured at the terminus, not the first stop", "rules": {"point": "terminal"}},
        {"label": "early arrivals count as on time", "rules": {"point": "terminal", "early": None}},
        {"label": "cancelled trips count as late", "rules": {"point": "terminal", "early": None, "cancelled": "fail"}},
        {"label": "Hijri month Rabi al-Thani, not September",
         "rules": {"point": "terminal", "early": None, "cancelled": "fail", "period": ["hijri", "1448-04"]}},
    ])
    put("d1_1_diagnosis", {"operations vs planning": ["grain"],
                           "operations vs board": ["point measured", "tolerance", "cancelled trips", "period"]})

    wk = "service_date BETWEEN DATE '2026-09-13' AND DATE '2026-09-19'"
    W.linked_view(con)
    put("d1_2_counts", {
        "taps": q(f"SELECT count(*) FROM fct_boarding WHERE {wk}"),
        "unique_cards": q(f"SELECT count(DISTINCT card_id) FROM fct_boarding WHERE {wk}"),
        "journeys": q(f"SELECT sum(journey_start) FROM boarding_linked WHERE {wk}"),
        "rider_days": q(f"SELECT count(*) FROM (SELECT DISTINCT card_id, service_date FROM fct_boarding WHERE {wk})"),
    })
    cat = {m["name"]: m for m in W.yaml_load(LABS / "data/catalogue/metric_catalogue.yaml")["metrics"]}
    put("d1_2_definitions", [cat[n] for n in ("taps", "unique_cards", "journeys", "rider_days")])

    sep = "service_date BETWEEN DATE '2026-09-01' AND DATE '2026-09-30'"
    put("d1_3_network", {
        "on_time_rate": q(f"SELECT sum((status <> 'cancelled' AND dep_delay_min BETWEEN -1 AND 5)::INT) / "
                          f"sum((status <> 'cancelled')::INT) FROM fct_trip WHERE {sep}"),
        "cancellation_rate": q(f"SELECT avg((status = 'cancelled')::INT) FROM fct_trip WHERE {sep}"),
        "mean_of_route_rates": q(f"SELECT avg(r) FROM (SELECT route_id, avg((dep_delay_min BETWEEN -1 AND 5)::INT) r "
                                 f"FROM fct_trip WHERE {sep} AND status <> 'cancelled' GROUP BY route_id)"),
    })
    weeks = con.sql(f"""SELECT d.week_start::VARCHAR AS week_start, count(DISTINCT b.card_id) AS cards
        FROM fct_boarding b JOIN dim_date d ON d.date = b.service_date
        WHERE d.week_start BETWEEN DATE '2026-09-06' AND DATE '2026-09-27' GROUP BY 1 ORDER BY 1""").fetchall()
    put("d1_3_weekly_cards", {"weeks": dict(weeks), "four_weeks": q(
        "SELECT count(DISTINCT card_id) FROM fct_boarding WHERE service_date BETWEEN DATE '2026-09-06' AND DATE '2026-10-03'")})

    tree = {}
    for w in ("2026-09-13", "2026-09-20"):
        span = f"service_date BETWEEN DATE '{w}' AND DATE '{w}'::DATE + 6"
        tree[w] = {
            "taps": q(f"SELECT count(*) FROM fct_boarding WHERE {span}"),
            "scheduled_trips": q(f"SELECT count(*) FROM fct_trip WHERE {span}"),
            "cancellation_rate": q(f"SELECT avg((status = 'cancelled')::INT) FROM fct_trip WHERE {span}"),
            "taps_per_departed_trip": q(f"SELECT (SELECT count(*) FROM fct_boarding WHERE {span}) / "
                                        f"(SELECT count(*) FROM fct_trip WHERE status <> 'cancelled' AND {span})"),
            "complaints_per_10k_taps": q(f"SELECT 10000.0 * (SELECT count(*) FROM fct_complaint WHERE "
                                         f"{span.replace('service_date', 'received_date')}) / "
                                         f"(SELECT count(*) FROM fct_boarding WHERE {span})"),
        }
    put("d1_4_tree", tree)


RV = ("LEFT JOIN dim_route r ON r.route_id = {a}.route_id AND {a}.{d} >= r.valid_from "
      "AND (r.valid_to IS NULL OR {a}.{d} <= r.valid_to)")
SEP = "BETWEEN DATE '2026-09-01' AND DATE '2026-09-30'"
WK = "BETWEEN DATE '2026-09-13' AND DATE '2026-09-19'"
OCTW = "BETWEEN DATE '2026-10-04' AND DATE '2026-10-10'"
LINKED = ("(SELECT *, CASE WHEN lag(tap_ts) OVER (PARTITION BY card_id ORDER BY tap_ts) >= tap_ts - INTERVAL 60 MINUTE "
          "THEN 0 ELSE 1 END AS journey_start FROM fct_boarding)")
OT = "sum((t.status <> 'cancelled' AND t.dep_delay_min BETWEEN -1 AND 5)::INT) / sum((t.status <> 'cancelled')::INT)"

# The 25 test queries of Lab 2.4: the request to the semantic layer, and an independent SQL that gives the answer.
TESTS = [
    ("t01", "Card taps in September", ["boardings.boardings"], [], ["dates.gregorian_month = '2026-09'"],
     f"SELECT count(*) AS boardings FROM fct_boarding WHERE service_date {SEP}"),
    ("t02", "Card taps by depot in September", ["boardings.boardings"], ["routes.depot"], ["dates.gregorian_month = '2026-09'"],
     f"SELECT r.depot, count(*) AS boardings FROM fct_boarding b {RV.format(a='b', d='service_date')} WHERE b.service_date {SEP} GROUP BY 1"),
    ("t03", "Distinct cards in the week of 13 September", ["boardings.unique_cards"], [], ["dates.week_start = DATE '2026-09-13'"],
     f"SELECT count(DISTINCT card_id) AS unique_cards FROM fct_boarding WHERE service_date {WK}"),
    ("t04", "Linked journeys in the week of 13 September", ["boardings.journeys"], [], ["dates.week_start = DATE '2026-09-13'"],
     f"SELECT sum(journey_start) AS journeys FROM {LINKED} WHERE service_date {WK}"),
    ("t05", "On-time rate in September", ["on_time_rate"], [], ["dates.gregorian_month = '2026-09'"],
     f"SELECT {OT} AS on_time_rate FROM fct_trip t WHERE t.service_date {SEP}"),
    ("t06", "On-time rate by route type in September", ["on_time_rate"], ["routes.route_type"], ["dates.gregorian_month = '2026-09'"],
     f"SELECT r.route_type, {OT} AS on_time_rate FROM fct_trip t {RV.format(a='t', d='service_date')} WHERE t.service_date {SEP} GROUP BY 1"),
    ("t07", "Cancellation rate in September", ["cancellation_rate"], [], ["dates.gregorian_month = '2026-09'"],
     f"SELECT avg((status = 'cancelled')::INT) AS cancellation_rate FROM fct_trip WHERE service_date {SEP}"),
    ("t08", "Cancellation rate by depot in October", ["cancellation_rate"], ["routes.depot"], ["dates.gregorian_month = '2026-10'"],
     f"SELECT r.depot, avg((t.status = 'cancelled')::INT) AS cancellation_rate FROM fct_trip t {RV.format(a='t', d='service_date')} "
     "WHERE month(t.service_date) = 10 GROUP BY 1"),
    ("t09", "Timepoint on-time rate in September", ["timepoint_on_time_rate"], [], ["dates.gregorian_month = '2026-09'"],
     f"SELECT avg((p.delay_min BETWEEN -1 AND 5)::INT) AS timepoint_on_time_rate FROM fct_timepoint p JOIN fct_trip t USING (trip_id) "
     f"WHERE p.delay_min IS NOT NULL AND t.service_date {SEP}"),
    ("t10", "Taps per departed trip in September", ["boardings_per_departed_trip"], [], ["dates.gregorian_month = '2026-09'"],
     f"SELECT (SELECT count(*) FROM fct_boarding WHERE service_date {SEP}) / (SELECT count(*) FROM fct_trip WHERE status <> 'cancelled' "
     f"AND service_date {SEP}) AS boardings_per_departed_trip"),
    ("t11", "Complaints per 10,000 taps in September", ["complaints_per_10k_boardings"], [], ["dates.gregorian_month = '2026-09'"],
     f"SELECT 10000.0 * (SELECT count(*) FROM fct_complaint WHERE received_date {SEP}) / (SELECT count(*) FROM fct_boarding "
     f"WHERE service_date {SEP}) AS complaints_per_10k_boardings"),
    ("t12", "Scheduled trips in Rabi al-Awwal and Rabi al-Thani 1448", ["trips.scheduled_trips"], ["dates.hijri_month_key"],
     ["dates.hijri_month_key IN ('1448-03', '1448-04')"],
     "SELECT d.hijri_month_key, count(*) AS scheduled_trips FROM fct_trip t JOIN dim_date d ON d.date = t.service_date "
     "WHERE d.hijri_month_key IN ('1448-03', '1448-04') GROUP BY 1"),
    ("t13", "Card taps in Ramadan", ["boardings.boardings"], [], ["dates.is_ramadan"],
     "SELECT count(*) AS boardings FROM fct_boarding b JOIN dim_date d ON d.date = b.service_date WHERE d.is_ramadan"),
    ("t14", "Card taps on R07 by route name", ["boardings.boardings"], ["routes.route_name_en"], ["routes.route_id = 'R07'"],
     f"SELECT r.route_name_en, count(*) AS boardings FROM fct_boarding b {RV.format(a='b', d='service_date')} WHERE r.route_id = 'R07' GROUP BY 1"),
    ("t15", "On-time rate by month, August to October", ["on_time_rate"], ["dates.gregorian_month"],
     ["dates.gregorian_month >= '2026-08'"],
     f"SELECT d.gregorian_month, {OT} AS on_time_rate FROM fct_trip t JOIN dim_date d ON d.date = t.service_date "
     "WHERE d.gregorian_month >= '2026-08' GROUP BY 1"),
    ("t16", "Departed trips by route type in August", ["trips.departed_trips"], ["routes.route_type"], ["dates.gregorian_month = '2026-08'"],
     f"SELECT r.route_type, sum((t.status <> 'cancelled')::INT) AS departed_trips FROM fct_trip t {RV.format(a='t', d='service_date')} "
     "WHERE month(t.service_date) = 8 GROUP BY 1"),
    ("t17", "Card taps by fare type in September", ["boardings.boardings"], ["boardings.fare_type"], ["dates.gregorian_month = '2026-09'"],
     f"SELECT fare_type, count(*) AS boardings FROM fct_boarding WHERE service_date {SEP} GROUP BY 1"),
    ("t18", "Distinct cards in September and in October", ["boardings.unique_cards"], ["dates.gregorian_month"],
     ["dates.gregorian_month IN ('2026-09', '2026-10')"],
     "SELECT strftime(service_date, '%Y-%m') AS gregorian_month, count(DISTINCT card_id) AS unique_cards FROM fct_boarding "
     "WHERE month(service_date) IN (9, 10) GROUP BY 1"),
    ("t19", "Complaints by category in September", ["complaints.complaints"], ["complaints.category"], ["dates.gregorian_month = '2026-09'"],
     f"SELECT category, count(*) AS complaints FROM fct_complaint WHERE received_date {SEP} GROUP BY 1"),
    ("t20", "Card taps in the week of 4 October by the depot of the bus", ["boardings.boardings"], ["vehicles.depot"],
     ["dates.week_start = DATE '2026-10-04'"],
     f"SELECT v.depot, count(*) AS boardings FROM fct_boarding b JOIN dim_vehicle v USING (vehicle_id) WHERE b.service_date {OCTW} GROUP BY 1"),
    ("t21", "Card taps in the week of 4 October by the depot of the route", ["boardings.boardings"], ["routes.depot"],
     ["dates.week_start = DATE '2026-10-04'"],
     f"SELECT r.depot, count(*) AS boardings FROM fct_boarding b {RV.format(a='b', d='service_date')} WHERE b.service_date {OCTW} GROUP BY 1"),
    ("t22", "Linked journeys on weekdays and weekends in September", ["boardings.journeys"], ["dates.is_weekend"],
     ["dates.gregorian_month = '2026-09'"],
     f"SELECT d.is_weekend, sum(journey_start) AS journeys FROM {LINKED} b JOIN dim_date d ON d.date = b.service_date "
     f"WHERE b.service_date {SEP} GROUP BY 1"),
    ("t23", "Timepoint events and on-time events by timepoint in September", ["timepoints.timepoint_events", "timepoints.on_time_events"],
     ["timepoints.tp_seq"], ["dates.gregorian_month = '2026-09'"],
     f"SELECT p.tp_seq, count(p.delay_min) AS timepoint_events, sum((p.delay_min BETWEEN -1 AND 5)::INT) AS on_time_events "
     f"FROM fct_timepoint p JOIN fct_trip t USING (trip_id) WHERE t.service_date {SEP} GROUP BY 1"),
    ("t24", "Card taps on each public holiday", ["boardings.boardings"], ["dates.holiday_en"], ["dates.holiday_en IS NOT NULL"],
     "SELECT d.holiday_en, count(*) AS boardings FROM fct_boarding b JOIN dim_date d ON d.date = b.service_date "
     "WHERE d.holiday_en IS NOT NULL GROUP BY 1"),
    ("t25", "Cancellation rate by day of the week in September", ["cancellation_rate"], ["dates.day_of_week_en"],
     ["dates.gregorian_month = '2026-09'"],
     f"SELECT d.day_of_week_en, avg((t.status = 'cancelled')::INT) AS cancellation_rate FROM fct_trip t JOIN dim_date d "
     f"ON d.date = t.service_date WHERE t.service_date {SEP} GROUP BY 1"),
]


def _rows(con, sql):
    df = con.sql(sql).df()
    df = df.astype(object).where(df.notna(), None)
    rows = []
    for r in df.to_dict("records"):
        rows.append({k: (v.item() if hasattr(v, "item") else (str(v) if hasattr(v, "isoformat") else v)) for k, v in r.items()})
    return rows


def day2(con):
    q = lambda s: W.scalar(con, s)
    put("d2_1_keys", {
        "fct_trip": ["trip_id"], "fct_timepoint": ["trip_id", "tp_seq"], "fct_boarding": ["tap_id"],
        "fct_complaint": ["complaint_id"], "dim_route": ["route_key"], "dim_date": ["date"], "dim_vehicle": ["vehicle_id"],
    })
    put("d2_2_r07", _rows(con, """
        SELECT r.route_name_en, r.length_km, count(DISTINCT t.trip_id) FILTER (WHERE t.status <> 'cancelled') AS departed_trips,
               count(b.tap_id) AS taps
        FROM dim_route r
        JOIN fct_trip t ON t.route_id = r.route_id AND t.service_date >= r.valid_from
             AND (r.valid_to IS NULL OR t.service_date <= r.valid_to)
        LEFT JOIN fct_boarding b ON b.trip_id = t.trip_id
        WHERE r.route_id = 'R07' GROUP BY 1, 2 ORDER BY 2"""))
    put("d2_2_hijri", _rows(con, """
        SELECT d.hijri_month_key, any_value(d.hijri_month_name_en) AS month_name, count(*) / count(DISTINCT b.service_date) AS taps_per_day
        FROM fct_boarding b JOIN dim_date d ON d.date = b.service_date GROUP BY 1 ORDER BY 1"""))
    put("d2_3_fixed", _rows(con, f"""
        WITH b AS (SELECT route_id, count(*) AS taps FROM fct_boarding WHERE service_date {SEP} AND route_id IS NOT NULL GROUP BY 1),
             p AS (SELECT t.route_id, avg((p.delay_min BETWEEN -1 AND 5)::INT) AS timepoint_on_time
                   FROM fct_timepoint p JOIN fct_trip t USING (trip_id) WHERE t.service_date {SEP} AND p.delay_min IS NOT NULL GROUP BY 1)
        SELECT route_id, taps, timepoint_on_time FROM b JOIN p USING (route_id) ORDER BY 1"""))
    put("d2_3_rowcounts", {
        "trips": q(f"SELECT count(*) FROM fct_trip WHERE service_date {SEP}"),
        "trips x taps": q(f"SELECT count(*) FROM fct_boarding b JOIN fct_trip t USING (trip_id) WHERE t.service_date {SEP}"),
        "trips x taps x timepoints": q(f"SELECT count(*) FROM fct_boarding b JOIN fct_trip t USING (trip_id) "
                                       f"JOIN fct_timepoint p USING (trip_id) WHERE t.service_date {SEP} AND p.delay_min IS NOT NULL"),
    })
    tests = []
    for tid, question, metrics, dims, where, sql in TESTS:
        tests.append({"id": tid, "question": question, "metrics": metrics, "dimensions": dims, "where": where,
                      "expected": _rows(con, sql)})
    W.yaml_dump({"tests": tests}, LABS / "data" / "semantic" / "test_queries.yaml")
    print("wrote data/semantic/test_queries.yaml")
    # The starter model of Lab 2.4: the reference model without the five metrics the lab adds
    doc = W.yaml_load(LABS / "data" / "semantic" / "wadi_noor_transit.yaml")
    for d in doc["datasets"]:
        if d["name"] == "boardings":
            d.pop("metrics")
    doc["metrics"] = [m for m in doc["metrics"] if m["name"] not in ("on_time_rate", "cancellation_rate")]
    head = ("# The starter model of Lab 2.4: the reference model without five metrics (boardings, unique_cards, journeys,\n"
            "# on_time_rate, cancellation_rate). Written by _tools/make_reference.py from wadi_noor_transit.yaml.\n")
    (LABS / "data" / "semantic" / "model_starter.yaml").write_text(head + W.yaml_dump(doc), encoding="utf-8", newline="\n")
    print("wrote data/semantic/model_starter.yaml")


WIREFRAME = {
    "decision": "Where to place the six reserve buses and the four field supervisors next week, by depot and route.",
    "panels": [
        {"title": "Routes leaving late", "question": "Q1", "metric": "on_time_rate", "dimensions": ["routes.route_id"],
         "comparison": "target", "also": "the route's level over the four weeks before", "owner": "Tawfiq Al-Sahafi, control centre"},
        {"title": "Trips that did not run", "question": "Q2", "metric": "cancellation_rate", "dimensions": ["routes.depot"],
         "comparison": "prior_period", "owner": "Tawfiq Al-Sahafi, control centre"},
        {"title": "Riders per trip (crowding)", "question": "Q3", "metric": "boardings_per_departed_trip",
         "dimensions": ["routes.route_id"], "comparison": "prior_period", "owner": "Dhuha Al-Rowais, network planning"},
        {"title": "Complaints by subject", "question": "Q4", "metric": "complaints.complaints",
         "dimensions": ["complaints.category"], "comparison": "prior_period", "owner": "Yasmeen Al-Jaafari, strategy and finance"},
        {"title": "Network taps", "question": "Q5", "metric": "boardings.boardings", "dimensions": [],
         "comparison": "prior_period", "owner": "Muneer Al-Thaqafi, data platform"},
    ],
    "drill_through": "Q9, average delay by timepoint, opened from a route in the first panel",
    "left_out": ["Q6 revenue belongs to finance", "Q7 card numbers are Restricted", "Q8 a forecast is not this decision"],
}
WEEK, PREV, FOUR = "2026-10-25", "2026-10-18", ("2026-09-27", "2026-10-18")
ONT = ("sum((t.status <> 'cancelled' AND t.dep_delay_min BETWEEN -1 AND 5)::INT)", "sum((t.status <> 'cancelled')::INT)")


def day3(con):
    rv_t, rv_b = RV.format(a="t", d="service_date"), RV.format(a="b", d="service_date")
    put("d3_1_wireframe", WIREFRAME)

    def on_time(weeks, names=True):
        cols = "r.route_id, r.route_name_en, r.route_name_ar" if names else "r.route_id"
        return f"""SELECT {cols}, {ONT[0]} / {ONT[1]} AS on_time_rate, {ONT[1]} AS departed_trips
            FROM fct_trip t {rv_t} JOIN dim_date d ON d.date = t.service_date
            WHERE d.week_start BETWEEN DATE '{weeks[0]}' AND DATE '{weeks[1]}' GROUP BY ALL ORDER BY ALL"""

    def crowding(week, names=True):
        cols = "route_id, route_name_en, route_name_ar" if names else "route_id"
        return f"""WITH b AS (SELECT r.route_key, count(*) AS taps FROM fct_boarding b {rv_b} JOIN dim_date d ON d.date = b.service_date
                       WHERE d.week_start = DATE '{week}' AND b.route_id IS NOT NULL GROUP BY 1),
                  t AS (SELECT r.route_key, {ONT[1]} AS dep FROM fct_trip t {rv_t} JOIN dim_date d ON d.date = t.service_date
                       WHERE d.week_start = DATE '{week}' GROUP BY 1)
            SELECT {cols}, sum(b.taps) / sum(t.dep) AS boardings_per_departed_trip
            FROM dim_route r JOIN b USING (route_key) JOIN t USING (route_key) GROUP BY ALL ORDER BY ALL"""

    def complaints(weeks):
        return f"""SELECT category, count(*) AS complaints FROM fct_complaint c JOIN dim_date d ON d.date = c.received_date
            WHERE d.week_start BETWEEN DATE '{weeks[0]}' AND DATE '{weeks[1]}' GROUP BY 1 ORDER BY 1"""

    panels = {"on_time": _rows(con, on_time((WEEK, WEEK))), "crowding": _rows(con, crowding(WEEK)),
              "complaints": _rows(con, complaints((WEEK, WEEK)))}
    put("d3_2_panels", panels)
    usual = {r["route_id"]: r["on_time_rate"] for r in _rows(con, on_time(FOUR, names=False))}
    prior = {r["route_id"]: r["boardings_per_departed_trip"] for r in _rows(con, crowding(PREV, names=False))}
    cu = {r["category"]: r["complaints"] / 4 for r in _rows(con, complaints(FOUR))}
    week_c = {r["category"]: r["complaints"] for r in panels["complaints"]}
    put("d3_2_compared", {
        "on_time": [dict(r, usual=usual[r["route_id"]], target=0.85) for r in panels["on_time"]],
        "crowding": [dict(r, prior=prior[r["route_id"]]) for r in panels["crowding"]],
        "complaints": [{"category": c, "complaints": week_c.get(c, 0), "usual": cu.get(c)} for c in sorted(set(cu) | set(week_c))],
    })

    # Lab 3.3: the route-day table of the 56 days to 31 October, with the parts of each ratio
    put("d3_3_route_day", _rows(con, f"""
        WITH t AS (SELECT t.route_id, t.service_date AS date, {ONT[1]} AS departed_trips, {ONT[0]} AS on_time_departures
                   FROM fct_trip t WHERE t.service_date BETWEEN DATE '2026-09-06' AND DATE '2026-10-31' GROUP BY ALL),
             b AS (SELECT route_id, service_date AS date, count(*) AS boardings FROM fct_boarding
                   WHERE service_date BETWEEN DATE '2026-09-06' AND DATE '2026-10-31' AND route_id IS NOT NULL GROUP BY ALL)
        SELECT t.route_id, t.date::VARCHAR AS date, departed_trips, on_time_departures, coalesce(boardings, 0) AS boardings
        FROM t LEFT JOIN b USING (route_id, date) ORDER BY 1, 2"""))

    # Lab 3.4: the drop in the week of 4 October
    put("d3_4_weekly", _rows(con, """
        SELECT d.week_start::VARCHAR AS week_start, count(*) AS taps, count(b.route_id) AS route_taps
        FROM fct_boarding b JOIN dim_date d ON d.date = b.service_date
        WHERE d.week_start BETWEEN DATE '2026-09-06' AND DATE '2026-10-25' GROUP BY 1 ORDER BY 1"""))
    put("d3_4_by_depot", _rows(con, f"""
        SELECT coalesce(r.depot, '(no route)') AS depot,
               count(*) FILTER (WHERE b.service_date BETWEEN DATE '2026-09-27' AND DATE '2026-10-03') AS week_before,
               count(*) FILTER (WHERE b.service_date BETWEEN DATE '2026-10-04' AND DATE '2026-10-10') AS week_of_4_october
        FROM fct_boarding b {rv_b} WHERE b.service_date BETWEEN DATE '2026-09-27' AND DATE '2026-10-10' GROUP BY 1 ORDER BY 1"""))
    put("d3_4_by_day", _rows(con, """
        SELECT b.service_date::VARCHAR AS day, count(*) AS east_bus_taps, count(b.route_id) AS with_route
        FROM fct_boarding b JOIN dim_vehicle v USING (vehicle_id)
        WHERE v.depot = 'East' AND b.service_date BETWEEN DATE '2026-10-01' AND DATE '2026-10-10' GROUP BY 1 ORDER BY 1"""))
    put("d3_4_restated", _rows(con, """
        SELECT d.week_start::VARCHAR AS week_start, count(coalesce(b.route_id, v.home_route)) AS restated_route_taps
        FROM fct_boarding b JOIN dim_vehicle v USING (vehicle_id) JOIN dim_date d ON d.date = b.service_date
        WHERE d.week_start BETWEEN DATE '2026-09-06' AND DATE '2026-10-25' GROUP BY 1 ORDER BY 1"""))


def main(units=("day1",)):
    con = W.db()
    REF.mkdir(parents=True, exist_ok=True)
    for u in units:
        globals()[u](con)
    for name, value in OUT.items():
        (REF / f"{name}.json").write_text(json.dumps(value, indent=1, ensure_ascii=False, default=str) + "\n",
                                          encoding="utf-8", newline="\n")
        print("wrote", f"data/reference/{name}.json")


if __name__ == "__main__":
    main(tuple(sys.argv[1:]) or ("day1", "day2", "day3"))
