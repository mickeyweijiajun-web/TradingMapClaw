# Contributing to TradingMapClaw

## System Status: FROZEN

TradingMapClaw (TMC) is in **FROZEN** status as of v1.1.1 (2026-06-30). The system is in daily operation and maintenance mode. **No new features will be accepted.**

This is not a temporary freeze. It is a deliberate architectural decision: the system has 232 Python scripts across 425 compilation units, many tightly coupled. Uncontrolled changes pose an existential risk to system stability. The v1.1 incident — where a single missing `id` field crashed all 115 cron jobs for 3 days — demonstrated why this discipline matters.

---

## What IS Accepted

| Contribution Type | Status | How to Submit |
|-------------------|--------|---------------|
| Bug reports | Accepted | Open a GitHub Issue using the bug report template |
| Documentation improvements | Accepted | Open a GitHub Issue or PR with `docs` label |
| Data source suggestions | Accepted | Open a GitHub Issue with `data-source` label |

### Bug Reports

Use the `.github/ISSUE_TEMPLATE/bug_report.md` template. Include:
- What happened (observed behavior)
- What should have happened (expected behavior)
- Which report type / script / cron job is affected
- Whether the issue is reproducible or intermittent
- Any error messages or log output

### Documentation

Documentation PRs are welcome if they:
- Fix factual errors in existing docs
- Add clarity to existing sections
- Provide translation improvements

Documentation PRs will be rejected if they:
- Add new features disguised as documentation
- Change the meaning of existing technical descriptions
- Introduce YAML blocks in report format descriptions (treated as code defects)

### Data Source Suggestions

If you know of a free or low-cost data source that could replace or supplement one of the existing 12+ sources, open an Issue with:
- Source name and URL
- What data it provides
- Whether it has a free tier
- Whether it has a Python library
- Why it is better than the current source it would replace

Note: The system's monthly budget cap is ~$55 USD. Suggestions for paid data sources are only useful if they fit within this budget.

---

## What is NOT Accepted

- **Feature requests** — the system is frozen. No new report types, no new analysis modules, no new delivery channels.
- **Code refactoring PRs** — see Engineering Constitution rule #4 (Surgical Changes). Uncontrolled refactoring is classified as a "Runaway Refactor" failure mode.
- **New dependencies** — see Engineering Constitution rule #8. Any new dependency must be justified against standard library / existing libraries. PRs adding `requirements.txt` entries without justification will be rejected.
- **Changes to frozen modules** — `send_reports`, `runtime_guard`, `scheduler`, and `stocks.yaml` schema cannot be modified.

---

## Hard Constraint: Engineering Constitution

All contributions — even bug fixes — must comply with the [Engineering Constitution](skills/engineering_constitution.md). The 10 rules:

1. **Read before write** — understand existing patterns before modifying code.
2. **Think before code** — state what you're doing and why before implementing.
3. **Simplicity** — write the minimum code to solve the problem.
4. **Surgical changes** — smallest possible diff. No incidental formatting changes, no refactoring of unrelated code. This is a hard rule.
5. **Verification** — write a failing test before fixing a bug.
6. **Goal-driven** — define success criteria before starting.
7. **Debugging** — investigate, don't guess. Read the full error. Fix one thing at a time.
8. **Dependencies** — no new dependencies without justification. Ask: can the standard library do this?
9. **Communication** — explain what you changed, why, and what is uncertain.
10. **Watch failure modes** — if you catch yourself doing Kitchen Sink, Wrong Abstraction, Happy Path, or Runaway Refactor, stop immediately.

PRs that violate these rules will be rejected, even if the code is functionally correct.

---

## Review Process

1. All PRs are reviewed by the maintainer (Mickey Wei).
2. Codex code review may be used to verify changes.
3. Changes to core scheduling or data collection require dual-engine agreement (Hermes + Codex).
4. Disputed changes remain unchanged until consensus is reached.

### A Note on Response Time

The maintainer has a physical disability (right-arm brachial plexus avulsion, permanent end ileostomy) that limits his mobility and typing speed. He reviews contributions with one working hand. Response times may be slower than typical open-source projects. This is a solo-maintained system — there is no team of reviewers.

Patience is appreciated. Quality is prioritized over speed.

---

*Contributing guide v1.1.1 — Generated 2026-06-30.*
