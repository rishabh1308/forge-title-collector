# Title Collection Skill

## Trigger

Use automatically when asked to collect, compare, validate, or report the titles of web pages.

## Steps

1. Post a concise plan in `#agent-orchestrator` and assign the coding task in `#sprint-main`.
2. Ask OpenClaw to run `python3 -m title_collector` with the requested URLs.
3. Require OpenClaw to run the test suite and `scripts/health_check.py`.
4. Inspect `output/titles.json` for failed records; ask the human in `#human-review` before publishing a report with failures.
5. Record the outcome, error pattern, and approved decision in memory and `agent-log.md`.

## Status format

Every update must use: **What I Did / What's Left / What Needs Your Call**.
