# Follow-up task · A measure your team reports

Tracked after the course, within four weeks; about six hours. You apply the course to one measure your own team
reports every week or month, using only data your entity allows you to use for training, or a synthetic copy of it.
No personal data leaves your entity's systems; what you hand in contains definitions, counts and queries, not rows.

## What you do

1. **Three governed definitions.** Pick one measure your team reports and two that feed it (a metric tree of three).
   Write each with name, question, formula, table, grain, filters, time logic, unit, owner and limits, and check it
   with `wnt.lint()`. Reconcile each to a source total and note the query.
2. **Ten certified questions.** Write ten questions a manager asks about these measures: at least two ratios, two
   that depend on the calendar (a Hijri month, a week that starts on Sunday, a holiday) and two that must be refused,
   with the reason. Give each the value, the query, the time logic and the tolerance.
3. **One test.** Ask one assistant, report or dashboard your team uses the ten questions. Score the answers against
   your certified set and name the error type of each wrong one, with the types of Lab 4.1.
4. **A half-page note** to your manager: what you found, which questions the assistant or report may answer without
   review, and what you would change first.

## What you hand in

- The three definitions (YAML in the format of `data/catalogue/metric_catalogue.yaml`).
- The certified set (YAML in the format of `data/agent/certified_questions.yaml`), with values replaced by "withheld"
  if they are confidential: the trainer checks the structure and the queries, not your entity's numbers.
- The scoring table and the half-page note.

## How it is reviewed

The trainer reviews the definitions with the peer checklist of Lab 1.2 and the certified set with the checklist of
Lab 4.2, and returns one written comment on each. The follow-up is tracked for completion; it does not change the
course result.
