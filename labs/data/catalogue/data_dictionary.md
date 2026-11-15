# Data dictionary: the Wadi Noor Transit warehouse (synthetic, 1 January to 31 October 2026)

Owner of the warehouse: Muneer Al-Thaqafi, data platform lead. Classification of every table is Public unless a
column says otherwise. Weeks start on Sunday. Dates are service dates: a trip after midnight belongs to the day it
started.

| Table | Grain (one row is) | Columns |
|---|---|---|
| `fct_trip` | one scheduled trip | `trip_id`, `service_date`, `route_id`, `direction`, `sched_departure`, `sched_minutes`, `vehicle_id`, `status` (operated, partial, cancelled), `dep_delay_min` (minutes late leaving the first timepoint; negative is early; empty when cancelled), `arr_delay_min` (minutes late at the terminus; empty unless operated) |
| `fct_timepoint` | one departed trip at one of its four timepoints | `trip_id`, `tp_seq` (1 to 4), `sched_arrival`, `actual_arrival`, `delay_min` (empty when the trip never reached it) |
| `fct_boarding` | one card tap at a validator | `tap_id`, `tap_ts`, `service_date`, `trip_id`, `route_id`, `vehicle_id`, `card_id` (pseudonymous; **Restricted**), `fare_type`, `product`, `fare_sar` (charged at the tap; 0 on passes and on a transfer within 60 minutes) |
| `fct_complaint` | one complaint | `complaint_id`, `received_date`, `route_id`, `category`, `category_ar`, `channel`, `complaint_text` (**Restricted**: may hold names and phone numbers) |
| `fct_fare_sale` | one pass sold | `sale_id`, `sale_date`, `card_id` (**Restricted**), `product`, `fare_type`, `price_sar`, `channel` |
| `dim_route` | one version of a route | `route_key`, `route_id`, `route_name_en`, `route_name_ar`, `depot`, `route_type` (trunk, feeder, express), `length_km`, `stop_count`, `run_minutes`, `valid_from`, `valid_to` (empty while current), `is_current` |
| `dim_date` | one day | `date`, `day_of_week_en`, `day_of_week_ar`, `is_weekend` (Friday, Saturday), `week_start` (Sunday), `iso_week`, `gregorian_month`, `hijri_date`, `hijri_year`, `hijri_month`, `hijri_month_key`, `hijri_month_name_en`, `hijri_month_name_ar`, `is_ramadan`, `holiday_en`, `holiday_ar`, `is_school_day` |
| `dim_vehicle` | one bus | `vehicle_id`, `depot`, `home_route`, `validator_firmware` |
| `dim_depot` | one depot | `depot`, `depot_ar` |
| `dim_fare_type` | one fare type | `fare_type`, `name_en`, `name_ar`, `single_fare_sar`, `card_level_classification` |
| `dim_fare_product` | one product | `product`, `name_en`, `name_ar`, `valid_days` |

The Hijri calendar is Umm al-Qura, converted with the `hijridate` package.
