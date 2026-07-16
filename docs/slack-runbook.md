# Slack demonstration runbook

Create: `#sprint-main`, `#agent-coder`, `#agent-orchestrator`, `#ci-cd`, and `#human-review`.

1. Hermes → `#agent-orchestrator`: “Plan: collect titles, verify JSON, request human approval. I will use the title-collection skill.”
2. Hermes → `#sprint-main`: “Task 1 assigned to @coder: run the collector for three URLs and validate the report.”
3. OpenClaw → `#agent-coder`: “What I Did: received Task 1. What's Left: run collector and tests. What Needs Your Call: none.”
4. OpenClaw → `#agent-coder`: “What I Did: generated `output/titles.json`; tests pass. What's Left: approval. What Needs Your Call: approve publishing this report.”
5. CI → `#ci-cd`: “Quality gate passed: unit tests and health check are green.”
6. Human → `#human-review`: “Approved: publish the verified title report.”
7. Hermes → `#sprint-main`: “Task 1 verified and approved. Report complete.”

For memory proof, first tell Hermes: “Remember that the preferred report owner is NMG Labs.” Start a new chat and ask it who owns the report; screenshot both exchanges. For the autonomous-run proof, schedule the health check in the Hermes scheduler and capture its `#ci-cd` result.
