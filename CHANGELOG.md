# Changelog

## 2026-07-15 — Third-round audit tooling

- Added a redacted Mac snapshot audit covering the real Hermes, cron, skills, shared-context and website paths.
- Added static checks for stale model references, Council round assignments/conditional tiebreaker, browser temp-file cleanup and task-queue state.
- Separated public-repository findings from Mac-only claims that still require on-device evidence.
- Documented the new website publication architecture: deterministic system updates may auto-merge after CI; research evidence remains review-gated.

> **TradingMapClaw (TMC) v2.0 | 2026-07-12**

All notable changes to TradingMapClaw (TMC) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [v2.0] — 2026-07-12 — Active

### Dual-Pass Council Formalized

The council structure was formalized as a **dual-engine architecture** (Pass A / B / C) with explicit weighting — Pass A (Hermes/GLM-5.2: fundamentals, valuation, insider — 40%), Pass B (Codex/GPT-5.6: technicals, capital flow, options, cross-verification — 35%), Pass C (Hermes/GLM-5.2: macro, industry, sentiment, regulatory — 25%) — backed by a **Council War Room** tiebreaker protocol (DeepSeek → GLM-5.2 → GPT-5.6) for contested calls, under the existing all-must-complete gate.

### Two Joint Audit Rounds — 14 Bugs Fixed Total

Two further joint Hermes+Codex audit rounds were run on top of the v1.6 audit, bringing the cumulative total to **14 bugs fixed**, including a critical `HERMES_HOME` undefined-variable bug that had been silently disabling Pass C's memory feature.

### Scale and Budget

- Public wording is temporarily **hundreds of Python scripts** and **100+ scheduled workflows**.
- The operator reports 415+ scripts; the Hermes audit contains conflicting 118/121 task totals. Exact current counts remain unverified until `tools/mac_snapshot_audit.py --compile` produces a reproducible inventory.
- **50+ SKILL.md** files.
- **82 tickers**, 12+ data sources.
- Budget: ~$7/month actual spend vs $55/month hard cap (13.5% of cap).

### Public Website and Payments

Public website and skill packs published; payments moved to fiat-only (PayPal/Wise) and the crypto tip jar was removed.

---

## [v1.6.1] — 2026-07-03 — Active

### Budget Tracker Fix

`budget_status.json` had been showing ¥0.00 every month because `token_tracker.record_usage()` was not being called by most cron jobs, and Codex CLI costs were logged separately in `codex_usage.jsonl` (248 entries with a real `cost_cny` field) but never fed into the tracker. `token_budget_check.py` (nightly cron at 23:00) was surgically rewritten to aggregate real costs from three sources:

1. `codex_usage.jsonl` — reads every entry, filters by current month, sums the real `cost_cny` field.
2. `quality_scores.csv` — counts Hermes agent LLM calls, estimates cost using model pricing rates.
3. `token_tracker.budget_status()` — retained as fallback for future `flush_monthly()` calls.

Verified output: `🟢 Budget: ¥1.84/400 (0.5%) — GREEN | Codex: 28 calls ¥1.58 | Hermes: 10 calls ¥0.26`. The dashboard now shows a per-model and per-task cost breakdown, updated nightly.

### T26 Race Condition Fix

The T26 data pipeline and the T26 onion report were both scheduled for 21:00 on Mondays, risking the onion report reading incomplete `sc_alpha_*.json` output. Fixed: data pipeline moved to **20:30**, 30 minutes ahead of the 21:00 onion report.

### Multi-Engine Timeout Fix

The multi-engine deep analysis flow (4 tickers × 3 engine calls × 300s timeout) could exceed the scheduler's 2700-second cap. Fixed: `MAX_TICKERS_PER_RUN` reduced from 4 to 2.

### Monday Readiness Audit — 7/7 PASS

A joint Hermes+Codex audit covering 7 operational risk points, run ahead of the v1.6.1 seal:

| # | Risk | Verdict | Action Taken |
|---|------|---------|-------------|
| 1 | T26 race condition (data pipeline vs onion report @ 21:00 Mon) | FAIL → FIXED | Data pipeline moved to 20:30 |
| 2 | Multi-engine timeout (4 tickers × 3 calls × 300s > 2700s cap) | WARN → FIXED | `MAX_TICKERS_PER_RUN` reduced 4 → 2 |
| 3 | yfinance cold cache (~60 calls, 5-10 min first run) | WARN | Acceptable — subsequent runs warm via 7-day TTL cache |
| 4 | Data freshness (technical/sentiment/stocks before 21:00) | PASS ✅ | All collected 1-3 hours before T26/analysis runs |
| 5 | Budget tracker runs + valid JSON | PASS ✅ | ¥1.84/¥400, GREEN status |
| 6 | `collect_market_data --check-only` API connectivity | PASS ✅ | Finnhub OK, CoinGecko OK |
| 7 | `py_compile` all 22 modified files | PASS ✅ | Zero errors |

### Added

- Website (tradingmapclaw.com) and author story integration.

### Verification

- **499/499 scripts compile** (`py_compile`)
- Monday readiness audit: 7/7 PASS/FIXED
- Budget tracker: accurate real-cost aggregation confirmed

---

## [v1.6] — 2026-07-03

### Codex Audit: 5 Post-Refactoring Bugs Found & Fixed

After all v1.5 changes were complete, Codex (GPT-5.6) performed a full engineering quality audit: read all 19 modified Python files completely, ran `py_compile` on all 19 (all PASS), ran `importlib.import_module()` on key files (all OK), verified cross-file dependencies, checked file sync between `scripts/` and `cron/scripts/` copies, and verified frozen modules were untouched.

| # | Severity | File | Bug | Fix | Verification |
|---|----------|------|-----|-----|-------------|
| 1 | CRITICAL | `codex_analyst_wrapper.py` L766 | `HERMES_HOME` undefined → Pass C macro/sentiment data never loaded (silently caught by except, no crash but feature dead) | Changed to `SCRIPTS_ROOT` (already defined at L39) | ✅ `_load_engine_c_memory('AVGO')` now returns real data |
| 2 | HIGH | `scripts/collect_market_data.py` L29 | `from pathlib import Path` missing in `scripts/` copy (`cron/scripts/` copy was fixed) | Added import | ✅ `py_compile` pass |
| 3 | MODERATE | `codex_options.py` L116,121,135-139 | Chinese strings in output headers ("策略分析") and review prompt | Converted to English | ✅ 0 non-comment Chinese in output lines |
| 4 | LOW | `scripts/codex_position_risk_wrapper.py` | `scripts/` copy still had 39 Chinese lines (`cron/scripts/` copy was English) | Synced: `cp cron/scripts/ → scripts/` | ✅ MD5 match |
| 5 | LOW | `codex_bullbear.py` L161,170 | Debug print statements in Chinese ("采集数据...", "分析...") | Converted to English | ✅ 0 Chinese prints |

### Multi-Engine Deep Analysis

Introduced the 4-step Pass C → Pass A → Pass B → Synthesis flow with mandatory cross-verification, co-authorship, and an all-must-complete gate (see [ARCHITECTURE.md](ARCHITECTURE.md#3-dual-engine-multi-model-analysis-flow)). Deep analysis template rewritten Chinese → English (8 sections). Cost analysis added (~$7/mo actual against $55/mo cap). Competitive comparison matrix added.

### Frozen Modules Verification (Post-Fix)

| Module | Status |
|--------|--------|
| `send_reports.py` | ✅ Not modified |
| `bilingual_send.py` | ✅ Not modified |
| `runtime_guard` | ✅ Not modified |
| `scheduler` | ✅ Not modified |
| `stocks.yaml` schema | ✅ Not modified |

---

## [v1.5] — 2026-07-03

### T26 Pipeline Fixes (9 items)

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| 1 | P0 | `collect_market_data.py` missing `from pathlib import Path` → all T1/T2/T3 reports used stale prices | Added import (both copies) |
| 2 | P0 | T26 scoring graph `depth==0` filter excluded Layer3 candidates | Removed filter |
| 3 | P0 | `get_hot_sectors()` read wrong data structure → only 3 of 8 sectors scanned | Rewritten to read `apewisdom_ranking` |
| 4 | P0 | `ALL_CANDIDATES` permanently empty → scoring engine missed tickers | Populated from `STATIC_SUPPLY_CHAIN` |
| 5 | P0 | T26 `collect_tech()` read wrong JSON path → RSI/MACD always empty | Added `.get("indicators", {})` |
| 6 | P0 | T26 `max_cap_usd=10B` filtered out ASML/AMAT/LRCX/KLAC/MU | Changed to 500B |
| 7 | P0 | Deep analysis Chinese validation headers → always failed on English | Changed to English headers |
| 8 | P0 | `_write_engine_c_memory()` Chinese regex → silently failed | Changed to English regex |
| 9 | P1 | T16 output `.json` but content is markdown | Changed to `.md` (both copies) |

### Feature Enhancements (15 items)

Supply chain graph expanded 43 → 49 suppliers; T26 now scans all 8 sectors (was top 3), eliminating a 62.5% blind spot; crawl depth increased 2 → 3; T11 alpha_score threshold lowered 0.3 → 0.15; T11 yfinance enrichment extended to all tickers (was 20 cap); market cap cache added (7-day TTL); alpha scoring expanded 5 → 8 dimensions; T26 report reads structured `sc_alpha` scores instead of fabricating; T26 prompts converted to plain language; T11 cron reduced to once daily; multi-engine flow introduced into `codex_analyst_wrapper` (single call → 4-step, all-must-complete gate); cross-verification logic added (Pass B verifies A, +0.1 confidence on pass); 6 no_agent scripts converted Chinese → English.

### Prompt Conciseness (5 items)

Report-generation prompts tightened across `codex_analyst_wrapper`, `codex_position_analyst`, `codex_bullbear`, and `codex_council` — shorter length targets, plain language, no preambles, fixed parser priority.

---

## [v1.1.4] — 2026-07-01 — SUPERSEDED

### Data Collection Pipeline Fix

A `NameError` in the data-collection entry point was silently degrading all T1/T2/T3 reports to stale cache. Root-caused, fixed, and cross-audited. **468/468 scripts compiled at this point. Hermes+Codex cross-audit passed. 32 total fixes across v1.1 → v1.1.4.**

### Fixed

- **P0:** `collect_market_data.py` line 1004 used `Path(__file__)` but the file header was missing `from pathlib import Path` → `NameError` crash. This is the data-collection entry point for all T1/T2/T3 reports — when it crashed, all reports fell back to stale cache (data freshness exceeded thresholds 43–54×; price data lagging 25–27 hours). Fixed: added `from pathlib import Path`.
- **P0:** `collect_social_sentiment_v2.py` had the same missing import → sentiment-collection crash. Fixed: added import.
- **P2:** `t1r3_wrapper.py` — DeepSeek V4 Pro generated `||` double-pipe table prefixes. Fixed: regex post-processing `_fix_deepseek_tables()`.
- **P2:** `t1r2_wrapper.py` — defensive addition of the same table fix (Codex cross-audit recommendation).
- **P1:** `generate_monday_report.py` Monday validation falsely flagged R2/R3 as missing. Confirmed existing `should_run_on_date()` logic correct; false positive came from an older version. No code change needed.

### Verification

- 468/468 scripts compile (`py_compile`)
- `Path()` import full scan: 118 scripts all pass
- Hermes+Codex cross-audit: passed
- Finnhub / Yahoo Finance / CoinGecko connectivity: HTTP 200
- Cron scheduler: ticking normally; push chain (Telegram + Feishu) verified

---

## [v1.1.3] — 2026-06-30 — SUPERSEDED

### Dual Codex Audit

A second, independent Codex audit was run against v1.1.2. It surfaced one item, which turned out to be a false alarm on verification. +1 fix. 27 total fixes at this point.

### Fixed
- **P2:** Dual Codex audit flagged a SKILL.md size alarm + ctx residue + t1r1 no-dry-run. Verified: on-disk SKILL.md 99K ✓, no new ctx errors ✓, t1r1 compiles ✓. False alarm — no code change required.

### Superseded
Superseded by v1.1.4 after a data-collection pipeline `NameError` was discovered.

---

## [v1.1.2] — 2026-06-30 — SUPERSEDED

### Final Seal

Cleanup of custodian caching and gateway module reloading after v1.1.1. +2 fixes.

### Fixed
- **P2:** Custodian `.pyc` cache not cleared — deleted all `__pycache__`.
- **P2:** Gateway held an old plugin module in memory — disable/enable triggered a reload.

### Superseded
Superseded by v1.1.3 (dual Codex audit).

---

## [v1.1.1] — 2026-06-30 — SUPERSEDED

### Post-Codex-Review Repair

The system was frozen at v1.1 on 2026-06-29. A subsequent Codex code review found 4 additional issues. This release fixes all 4. **425/425 scripts compiled at this point (later grew to 468, then 499, as upstream files were regenerated).**

### Fixed
- **P0:** Batch sys.path patch broke 11 scripts in `cron/scripts/` + 8 in `scripts/` with IndentationError — `_CRON_ROOT` block was inserted at column 0 inside `try:` blocks. Fixed: moved `_CRON_ROOT` to module top level, re-indented `from lib.*` imports back into `try:` blocks. All 425 scripts now compile.
- **P0:** T1 R4 C-group tickers showed missing analyst_net data — LLM was not reading `analyst.yaml` correctly for all tickers. Fixed: merged `analyst_net`/`buy`/`hold`/`sell` from `analyst.yaml` directly into `stocks.yaml`. Updated `collect_market_data.py` to auto-merge on every collection.
- **P1:** `mock_prices()` in position risk wrapper referenced an undefined variable. Fixed: replaced with explicit mock price dict. `--mock-risks` dry-run mode now works.
- **P2:** `codex_analyst` profile SKILL.md exceeded the 100K char limit. Fixed: moved content to a references subfile.

### Verification
- 425/425 scripts compile (`py_compile`)
- 34/34 wrapper scripts pass syntax check
- Cron scheduler running normally
- T3 premarket report generated successfully
- Push chain (`send_reports.py`): dry-run passed
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
- **P0:** `t3_wrapper.py` calls a nonexistent function. Changed to `sanitize_positions()`.
- **P0:** 18 wrapper scripts use `__file__` undefined in exec() context. Batch-patched all 18 wrappers.
- **P1:** `no_agent` script runner discards `command` field args. Added `_parse_command_args()` to scheduler.
- **P1:** Wrapper error stubs pushed to Telegram/Feishu as "reports." Added blacklist + suppression filter.
- **P1:** Event calendar catalyst lookahead too short (14 days). Extended to 30 days.
- **P1:** `collect_news.py` missing `import sys` → NameError. Added import.
- **P1:** Two tickers had stale/missing analyst_net data. Ran yfinance analyst collector manually.
- **P1:** Position Risk report weight/concentration missing. Added `_merge_position_shares()` from positions data.
- **P1:** T1/T2 news sentiment occasionally missing. LLM now infers sentiment from headline text.
- **P2:** Custodian plugin hook signature mismatch. Removed unused parameter from 4 callbacks.
- **P2:** 3 SKILL.md files exceeded the 100,000 char limit. Moved content to references subfiles.
- **P2:** `pandas_ta_classic` not installed. Installed.
- **P2:** 79 scripts imported `from lib.*` without a sys.path fix. Batch-patched 158 scripts.
- **P2:** `codex_position_risk_wrapper.py` ModuleNotFoundError. Applied sys.path fix.
- **P3:** `codex_screening_engine` missing upstream file. Root cause: 3-day scheduler outage.
- **P3:** `panel_data_writer.py` reported missing. False alarm — file exists.

### Superseded
Superseded by v1.1.1 after Codex code review found batch patch indentation bugs in 19 scripts.

---

## [v1.0] — 2026-06-29 — SUPERSEDED

### Initial Freeze

Full-system audit completed. 7 dimensions, 232 scripts, 115 cron jobs, 65k LOC.

### Added
- T11 dual-track alpha radar with Chuanmu 6-dimension rubric scoring (0-12 scale)
- T26 supply chain chokepoint scoring (AMAT/LRCX/KLAC)
- `backtrader` local backtesting engine
- Engineering Constitution (10 rules, Karpathy-derived)
- Full data collection pipeline: 12+ sources, 226 collection scripts
- 13 report types: T1/T2/T3/T11/T15/T16/T17/T18/T19/T25/T26/R1-R3/Visual
- Dual-engine AI council: Pass A Hermes/GLM-5.2 (fundamentals) + Pass B Codex/GPT-5.6 (technicals, cross-verify) + Pass C Hermes/GLM-5.2 (macro, sentiment)
- Model fallback chain: GLM-5.2 → GPT-5.6 → DeepSeek V4 Pro → Qwen3 14B (local)
- Telegram + Feishu delivery: 30+ wrapper scripts
- Budget watchdog: $55/month hard cap
- Coverage: 82 tickers across 5 groups

### Superseded
Superseded by v1.1 due to critical cron scheduler incident (`L13_LogCleanup` missing `id`).

---

## Version History Summary

| Version | Date | Status | Key Changes |
|---------|------|--------|-------------|
| v1.0 | 2026-06-29 | SUPERSEDED | Initial freeze. Full system audit. |
| v1.1 | 2026-06-29 | SUPERSEDED | Post-incident repair. 20 fixes (5P0/8P1/5P2/2P3). |
| v1.1.1 | 2026-06-30 | SUPERSEDED | Post-Codex-review repair. 4 fixes (2P0/1P1/1P2). |
| v1.1.2 | 2026-06-30 | SUPERSEDED | Final seal. +2 fixes (custodian pyc + gateway reload). |
| v1.1.3 | 2026-06-30 | SUPERSEDED | Dual Codex audit passed. +1 fix (false-alarm verification). 27 total. |
| v1.1.4 | 2026-07-01 | SUPERSEDED | Data pipeline fix. +5 fixes. 468/468 compile. Hermes+Codex cross-audit passed. |
| v12.1 | 2026-07-01 | SUPERSEDED | Hermes+Codex joint audit: 16 runtime import P0s fixed. |
| v12.2 | 2026-07-01 | SUPERSEDED | BullBear cache fallback + Sympathy Play structured news. |
| v13 | 2026-07-02 | SUPERSEDED | Bilingual report delivery: 30 prompts English, DeepSeek translation, 33 scripts swapped. |
| v1.5 | 2026-07-03 | SUPERSEDED | T26 pipeline fixed (9 bugs), T11 expanded, 8-dimension scoring, 6 scripts Chinese→English. |
| v1.6 | 2026-07-03 | SUPERSEDED | Codex audit: 5 post-refactoring bugs found & fixed. Multi-engine deep analysis (4-step flow, cross-verification, co-authorship, all-must-complete gate). Cost analysis (~$7/mo actual). Competitive comparison matrix. |
| v1.6.1 | 2026-07-03 | SUPERSEDED | Budget tracker fixed (reads real Codex CLI logs + quality_scores.csv). T26 race condition fixed (data pipeline 21:00→20:30). Multi-engine timeout fixed (MAX_TICKERS 4→2). Monday readiness audit: 7/7 PASS. Website + author story added. |
| **v2.0** | **2026-07-12** | **Active** | **Dual-engine architecture formalized (Pass A 40% / Pass B 35% / Pass C 25%) with Council War Room tiebreaker. Two further joint audit rounds — 14 bugs fixed total. Current public scale wording is hundreds of scripts / 100+ scheduled workflows pending Mac snapshot reconciliation; 50+ SKILL.md, 82 tickers. Budget ~$7/mo vs $55/mo cap.** |

Total fixes across v1.0 → v2.0: **74+ items** across ten repair/enhancement cycles.

---

*Changelog v2.0 | 2026-07-12. A Chinese version is available in [CHANGELOG_CN.md](CHANGELOG_CN.md).*
