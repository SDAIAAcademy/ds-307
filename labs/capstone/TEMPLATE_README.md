# <Project name>

> One sentence: the decision this work serves, and for whom.

[Metrics, Semantic Models and Dashboards (DS-307) - SDAIA Academy](https://github.com/SDAIAAcademy/ds-307)

**Author:** <name>
**Area:** fares and concessions of Wadi Noor Transit (synthetic data)
**Agent mode:** <live, with which free model / scripted stand-in, with your own stand-in file>

## The decision

Who decides what, how often, and which questions the work answers. 5 to 8 lines.

## How to rerun

```bash
cd labs
uv run python capstone/starter.py validate --model <your model>
uv run python capstone/starter.py test --model <your model> --tests <your tests>
uv run python capstone/starter.py time --model <your model>
uv run python capstone/starter.py score --model <your model> --certified <your set>
```

Put a model key, if you have one, in `labs/.env` as `OPENROUTER_API_KEY`. No keys are committed.

## Catalogue

| Metric | Question | Formula | Grain | Time logic | Owner | Limits |
|---|---|---|---|---|---|---|
| | | | | | | |

Verification notes for definitions an assistant drafted: <query run, what changed>.

## Semantic model

- Datasets and relationships: <list>
- Model-scoped metrics: <list, with their AGG() expressions>
- Access: <roles; how Restricted fields and concession fares are handled>
- Test queries: **<passed> of <N>** pass (`results/test_queries.csv`)

## Dashboard

- Brief: <audience, decision, cadence, budget>
- Panels: <at most six, each with its comparison and owner>
- Load time: **<first load> s**, best of 5 <best> s (`results/load_time.json`)
- Rationale: <link to the one-page rationale>

## Agent evaluation

| Question type | Questions | Right | 90% interval | Plausible wrong | Decision |
|---|---|---|---|---|---|
| | | | | | |

Memo: <link>. Mode of every answer: `results/agent_log.jsonl`.

## Limits

What this work does not show, and what you would test next.
