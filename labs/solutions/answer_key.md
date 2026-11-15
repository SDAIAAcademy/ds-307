# Trainer's answer key

What is planted in the Wadi Noor Transit data, where each lab finds it, and the answers of the deck checkpoints.
Every figure below is produced by `prepare_data.py` (seed 307) and checked by the labs; rerun
`_tools/make_reference.py` after any change to the generator.

## Planted in the data

| # | What is planted | How it shows | Found in |
|---|---|---|---|
| 1 | Three definitions of "on time" for September | operations 80.7% (departure, departed trips), planning 66.0% (every timepoint arrival), board 58.4% (terminus, no early, cancelled as late, Hijri month Rabi al-Thani) | Lab 1.1 |
| 2 | Taps, cards, journeys and card-days counted from the same taps | week of 13 September: 19,826 taps, 9,864 cards, 16,231 journeys, 13,992 card-days; 11% of taps are free transfers within 60 minutes | Lab 1.2 |
| 3 | Distinct counts that do not add across weeks | four weekly card counts sum to 38,764; the four weeks hold 22,962 cards | Lab 1.3 |
| 4 | Ratio of sums against mean of ratios | September network on time 80.7% against a mean of route rates of 79.9% | Lab 1.3 |
| 5 | National Day runs a holiday timetable | taps of the week of 20 September fall 8.5%; the timetable explains 94.2% of the change (log shares) | Lab 1.4 |
| 6 | R07 re-routed on 1 June 2026 (type 2) | `dim_route` has 13 rows for 12 routes; a join on `route_id` gives 91,418 rows for 85,010 trips; taps per trip-km 0.649 old, 0.666 new | Labs 2.1, 2.2 |
| 7 | Ramadan service hours and demand | 2,186 taps a day in Ramadan against 2,624 in the 30 days after | Lab 2.2 |
| 8 | Timepoint fan-out | joining taps and timepoints through trips gives 334,786 rows for 84,063 taps (×3.98); R01 timepoint punctuality 49.0% in the joined report against 51.1% | Lab 2.3 |
| 9 | Express frequency doubled and trunk cut from 1 September (Simpson) | every route type is less punctual in September than August, yet the network rises from 79.0% to 80.7% | Lab 3.4 stretch; Day 3 deck |
| 10 | East validator update, 5 to 8 October | 3,902 taps without route or trip; route taps of the week of 4 October -17.4%, all taps +2.5%; `dim_vehicle.validator_firmware` says "2.4 to 3.0 on 5 October" | Labs 3.3 (16 empty route-days), 3.4 |
| 11 | Small weekly complaint counts | 4 of 6 subjects below 10 in the week of 25 October | Lab 3.2 |
| 12 | Personal data in complaints | `complaint_text` holds synthetic names and phone numbers (05 followed by eight digits); Restricted in the model | Labs 2.4, 4.1, 4.3 |
| 13 | Concession fares Restricted at card level | `dim_fare_type.card_level_classification` is Restricted for senior and disability; their passes are free | Capstone |
| 14 | R12, a school feeder | ridership falls by more than half outside school days | no lab; for open questions in discussion |

## The stand-in agent of Day 4

`data/agent/stand_in.yaml` scripts the query of each certified question in each configuration. The errors were
written on purpose; `data/reference/d4_errors.json` is the key.

| Configuration | Right | Errors |
|---|---|---|
| raw | 18 of 40 | period 6 (Q03, Q25, Q26, Q27, Q28, Q32), definition 4 (Q09, Q16, Q19, Q22), grain 3 (Q10, Q18, Q23), filter 3 (Q04, Q12, Q30), join 1 (Q13), leak 4 (Q33, Q35, Q36, Q37), invented 1 (Q38) |
| semantic | 37 of 40 | grain 1 (Q23, weekly distinct cards summed), period 2 (Q27 Monday week, Q32 April for Shawwal) |

Decisions of Lab 4.4: count and ratio answer (provisionally), distinct and calendar review, restricted refuse.

## Deck checkpoints

| Deck | Answers in order |
|---|---|
| Day 1 | B, D, A, C |
| Day 2 | C (review), D, A, B, D |
| Day 3 | B (review), A, D, C, B |
| Day 4 | A (review), C, B, D, A |
