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


def main(units=("day1",)):
    con = W.db()
    REF.mkdir(parents=True, exist_ok=True)
    for u in units:
        globals()[u](con)
    for name, value in OUT.items():
        (REF / f"{name}.json").write_text(json.dumps(value, indent=1, ensure_ascii=False, default=str) + "\n",
                                          encoding="utf-8")
        print("wrote", f"data/reference/{name}.json")


if __name__ == "__main__":
    main(tuple(sys.argv[1:]) or ("day1",))
