# Contributing to TradingMapClaw

> **v2.0 | 2026-07-12**

## System Status: Active Development, Tightly Controlled

TradingMapClaw (TMC) is at **v2.0** (2026-07-12) and in daily operation and active maintenance. This is not a green-field project accepting arbitrary feature requests — it is a solo-maintained, 230+-script production system, and changes are deliberately constrained.

The system has 230+ Python scripts, many tightly coupled. Uncontrolled changes pose an existential risk to system stability. The v1.1 incident — where a single missing `id` field crashed all 115 cron jobs for 3 days — and the v1.6 Codex audit — which found a `HERMES_HOME` undefined-variable bug that had silently disabled Pass C's memory — both demonstrate why this discipline matters. See [CHANGELOG.md](CHANGELOG.md) for the full incident and fix history.

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

Note: the system's monthly budget cap is **$55 USD**. Suggestions for paid data sources are only useful if they fit within this budget — see [ARCHITECTURE.md](ARCHITECTURE.md#1-design-principles) for the budget-discipline principle.

---

## What Is NOT Accepted

- **Speculative feature requests** — new report types, new analysis modules, and new delivery channels require a clear justification tied to a real gap, not "it would be nice." The bar is high because every new surface adds to a 230+-script maintenance load carried by one person.
- **Code refactoring PRs** — see Engineering Constitution rule #4 (Surgical Changes). Uncontrolled refactoring is classified as a "Runaway Refactor" failure mode.
- **New dependencies** — see Engineering Constitution rule #8. Any new dependency must be justified against standard library / existing libraries. PRs adding `requirements.txt` entries without justification will be rejected.
- **Changes to frozen modules** — `send_reports.py`, `runtime_guard`, `scheduler`, and the `stocks.yaml` schema cannot be modified. See [ARCHITECTURE.md](ARCHITECTURE.md#10-frozen-modules--engineering-constitution).

---

## How to Propose a Change

1. **Open an Issue first.** Describe the problem, not the solution. State which script(s), cron job(s), or report type(s) are affected.
2. **Wait for a frozen-module check.** If the proposal touches `send_reports.py`, `runtime_guard`, `scheduler`, or `stocks.yaml` schema, it will be rejected outright — propose a wrapper instead (see `bilingual_send.py` as the precedent).
3. **State the smallest possible fix.** Per rule #4 below, PRs should be the minimum diff that solves the stated problem.
4. **Include a verification step.** How did you confirm the fix works? `py_compile`, a dry run, a specific test case — see rule #5.

---

## Hard Constraint: Engineering Constitution

All contributions — even bug fixes — must comply with the Engineering Constitution (source: Karpathy's `CLAUDE.md`, distilled 2026-06-29; see `skills/engineering_constitution.md`). The 10 rules:

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

## Frozen-Module Policy

The following are FROZEN and out of scope for any PR, regardless of how small:

| Module | Why it's frozen |
|--------|------------------|
| `send_reports.py` (1360 lines) | Core push infrastructure. `bilingual_send.py` is the sanctioned way to extend delivery behavior without touching this file. |
| `runtime_guard` | System health monitoring — a bug here can mask failures across the whole pipeline. |
| `scheduler` | Cron engine — the v1.1 incident (missing `id` field crashing all 115 jobs) originated adjacent to this layer. |
| `stocks.yaml` schema | Every downstream report and script assumes this schema. A silent schema change breaks 82-ticker coverage system-wide. |

If your proposal requires touching a frozen module, the correct pattern is a wrapper (see `bilingual_send.py` wrapping `send_reports.py`) — open an Issue describing why a wrapper isn't sufficient before proposing direct modification.

---

## Review Process

1. All PRs are reviewed by the maintainer (Mickey Wei).
2. Codex code review may be used to verify changes.
3. Changes to core scheduling or data collection require agreement between the Hermes and Codex engines.
4. Disputed changes remain unchanged until consensus is reached.

### A Note on Response Time

The maintainer has a physical disability (right-arm brachial plexus avulsion, permanent ostomy) that limits his mobility and typing speed. He reviews contributions with one working hand. Response times may be slower than typical open-source projects. This is a solo-maintained system — there is no team of reviewers.

Patience is appreciated. Quality is prioritized over speed.

---

*Contributing guide v2.0 | 2026-07-12. A Chinese version is available in [CONTRIBUTING_CN.md](CONTRIBUTING_CN.md).*
