# Changelog

All notable changes to TradingMapClaw (TMC) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [v1.1.1] — 2026-06-30 — FROZEN

### Post-Codex-Review Repair

The system was frozen at v1.1 on 2026-06-29. A subsequent Codex code review found 4 additional issues. This release fixes all 4. **425/425 scripts now compile.**

### Fixed
- **P0:** Batch sys.path patch broke 11 scripts in `cron/scripts/` + 8 in `scripts/` with IndentationError — `_CRON_ROOT` block was inserted at column 0 inside `try:` blocks. Fixed: moved `_CRON_ROOT` to module top level, re-indented `from lib.*` imports back into `try:` blocks. All 425 scripts now compile.
- **P0:** T1 R4 C组 23/44 tickers showed "数据暂缺" for analyst_net — LLM was not reading analyst.yaml correctly for all tickers. Fixed: merged `analyst_net`/`buy`/`hold`/`sell` from analyst.yaml directly into stocks.yaml (55/57 tickers). Updated `collect_market_data.py` to auto-merge on every collection. Updated T1-R1/R2/R3/R4 + T2 + T3 wrapper prompts.
- **P1:** `mock_prices()` in position_risk wrapper references undefined variable `m` (line 314). Fixed: replaced `m` with explicit mock price dict. `--mock-risks` dry-run mode now works.
- **P2:** `codex_analyst` profile `research-paper-writing/SKILL.md` still over 100K chars (102K). Fixed: moved Phase 5 to `references/phase5-paper-drafting.md` (102K→71K). All 4 SKILL.md files now under 100K limit.

### Verification
- 425/425 scripts compile (verified via `py_compile`)
- 34/34 wrapper scripts pass syntax check
- Cron scheduler running normally
- T3 premarket report generated successfully
- Council/Synthesizer/Portfolio/Alert Router all completed
- Data files freshness: all current
- Push chain (send_reports.py): dry-run passed
- Telegram + Feishu credentials: readable
- Hermes-Codex collaboration bridge: running

---

## [v1.1] — 2026-06-29 — SUPERSEDED

### Post-Incident Repair

Root cause: `L13_LogCleanup` job missing `id` field → `get_due_jobs()` KeyError → entire cron scheduler crashed → 115 jobs stopped for 3 days (2026-06-26 to 2026-06-29).

20 fixes applied: 5 P0, 8 P1, 5 P2, 2 P3.

### Fixed
- **P0:** `L13_LogCleanup` missing `id` field → KeyError crash. Added `id` field to job record in `jobs.json`.
- **P0:** `get_due_jobs()` unsafe `job["id"]` access (20 sites). Changed to `_normalize_job_record()` with `.get()` coercion.
- **P0:** `audit_utils.py` import `lib.universe` fails — sys.path not set. Inserted `_CRON_ROOT` sys.path guard.
- **P0:** `t3_wrapper.py` calls `ensure_positions_safe()` which doesn't exist. Changed to `sanitize_positions()`.
- **P0:** 18 wrapper scripts use `__file__` undefined in exec() context. Batch-patched all 18 wrappers.
- **P1:** `no_agent` script runner discards `command` field args. Added `_parse_command_args()` to scheduler.
- **P1:** Wrapper error stubs pushed to Telegram/Feishu as "reports". Added blacklist + suppression filter.
- **P1:** `event_calendar_rolling.yaml` catalyst lookahead too short (14 days). Extended to 30 days.
- **P1:** `collect_news.py` missing `import sys` → NameError. Added import.
- **P1:** SPCX `analyst_net` = 数据暂缺. Ran yfinance analyst collector manually.
- **P1:** CBRS `analyst_net` stale. Refreshed via yfinance collector.
- **P1:** Position Risk report weight/concentration = 数据暂缺. Added `_merge_position_shares()` from `positions_safe.yaml`.
- **P1:** T1/T2 news sentiment = 数据暂缺. LLM now infers sentiment from headline text.
- **P2:** Custodian plugin hook signature mismatch. Removed `ctx` parameter from 4 callbacks.
- **P2:** 3 SKILL.md files exceed 100,000 char limit. Moved content to references/ subfiles.
- **P2:** `pandas_ta_classic` not installed. Installed v0.6.52.
- **P2:** 79 scripts import `from lib.*` without sys.path fix. Batch-patched 158 scripts.
- **P2:** `codex_position_risk_wrapper.py` ModuleNotFoundError. Applied sys.path fix.
- **P3:** `codex_screening_engine` missing upstream file. Root cause: 3-day scheduler outage.
- **P3:** `panel_data_writer.py` reported missing. False alarm — file exists (98KB, Jun 18).

### Superseded
Superseded by v1.1.1 after Codex code review found batch patch indentation bugs in 19 scripts.

---

## [v1.0] — 2026-06-29 — SUPERSEDED

### Initial Freeze

Full-system audit completed. 7 dimensions, 232 scripts, 115 cron jobs, 65k LOC.

### Added
- T11 dual-track alpha radar with Chuanmu 6-dimension rubric scoring (0-12 scale)
- T26 supply chain chokepoint scoring (AMAT/LRCX/KLAC)
- backtrader local backtesting engine
- Engineering Constitution (10 rules, Karpathy-derived)
- Full data collection pipeline: 12+ sources, 226 collection scripts
- 13 report types: T1/T2/T3/T11/T15/T16/T17/T18/T19/T25/T26/R1-R3/Visual
- Dual-engine AI council: Hermes GLM-5.2 (fundamentals) + Codex GPT-5.5 (technicals)
- Model hierarchy: GLM-5.2 → GPT-5.5 → DeepSeek-V4-Pro → Qwen3 14B (local)
- Telegram + Feishu delivery: 30+ wrapper scripts
- Budget watchdog: ~$55/month hard cap
- Coverage: 82 tickers across 5 groups

### Superseded
Superseded by v1.1 due to critical cron scheduler incident (L13_LogCleanup missing `id`).

---

## Version History Summary

| Version | Date | Status | Fixes/Features |
|---------|------|--------|----------------|
| v1.0 | 2026-06-29 | SUPERSEDED | Initial freeze. Full system audit. 17 items completed. |
| v1.1 | 2026-06-29 | SUPERSEDED | Post-incident repair. 20 fixes (5P0/8P1/5P2/2P3). |
| v1.1.1 | 2026-06-30 | FROZEN | Post-Codex-review repair. 4 fixes (2P0/1P1/1P2). 425/425 scripts compile. |

Total fixes across v1.1 + v1.1.1: 24 items.

---

*Changelog v1.1.1 — Generated 2026-06-30.*
