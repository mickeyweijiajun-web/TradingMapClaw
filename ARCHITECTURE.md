# Architecture

> TradingMapClaw (TMC) v1.1.1 — FROZEN
> This document describes the system's design principles, data flow, component responsibilities, key decisions, and known limitations.

---

## 1. Design Principles

### 1.1 Budget Discipline

Every design decision is filtered through a hard monthly budget cap of ~$55 USD (¥400 CNY). This constraint shapes the entire architecture:

- No cloud infrastructure — the system runs on a single Mac mini (Apple Silicon, macOS 26.5.1).
- No premium data feeds (Bloomberg, Refinitiv). Data comes from 12+ free or low-cost sources.
- LLM costs are monitored by a custom budget watchdog. The model hierarchy (GLM-5.2 → GPT-5.5 → DeepSeek-V4-Pro → Qwen3 14B local) cascades from cheapest to most expensive.
- The local model (Qwen3 14B via Ollama) handles formatting and deduplication — tasks that do not require frontier reasoning — to conserve API budget.

### 1.2 Maker-Checker Dual Engine

The core analytical architecture uses a dual-engine council pattern:

- **Engine A (Maker):** Hermes GLM-5.2 — produces fundamental analysis, valuation, and options assessment.
- **Engine B (Checker):** Codex GPT-5.5 — produces technical analysis, capital flow, and risk assessment. Engine B also fact-checks Engine A's numerical outputs. If numbers pass verification, confidence increases by +0.1.
- **Council/Synthesis Layer:** Merges both engines' outputs into a consensus report. Divergences are flagged, not hidden. Confidence is annotated.
- **Engine C (Optional):** Macro, industry, and sentiment layer. Activated for event-driven reports (T15 macro, T11 radar).

This is not a voting mechanism. It is a structured adversarial review: Engine B actively tries to find errors in Engine A's work.

### 1.3 Zero-Touch Automation

The system is designed to operate without human intervention during market hours:

- 115 cron jobs handle data collection, analysis, report generation, and delivery.
- Reports are pushed to Telegram and Feishu via 30+ wrapper scripts, all using `--caption-only` and `--telegram-chat-id` flags.
- Quality gates validate data freshness and completeness before reports are generated.
- Error stubs and wrapper diagnostics are blacklisted from push delivery — users never receive broken reports.
- The system runs overnight: collecting data at 4 AM, running analysis before market open, delivering reports to the user's phone.

---

## 2. Data Flow

### Layer 1: Data Collection (Input)

| Aspect | Detail |
|--------|--------|
| Input format | HTTP API responses (JSON/HTML), RSS feeds, YAML config files |
| Collection scripts | 226 Python scripts in `~/.hermes/cron/scripts/` |
| Scheduling | Hermes cron engine — 115 jobs, 106 enabled, 9 disabled |
| Proxy | All outbound traffic through `http://127.0.0.1:10808` |
| Output format | YAML files in `~/.hermes/cron/data/` (stocks.yaml, news.yaml, analyst.yaml, sentiment.yaml, insider.yaml, etc.) |

Data collection scripts fetch from 12+ sources, normalize the responses into structured YAML, and write to the shared data directory. Each script includes a `_CRON_ROOT` sys.path guard to ensure module imports resolve correctly in the exec() context.

### Layer 2: Quality Gate (Pre-Gate)

| Aspect | Detail |
|--------|--------|
| Input | YAML files from Layer 1 |
| Validation | Data freshness check, field completeness check, schema validation |
| API | Port 8080 (programmatic access) |
| Dashboard | Port 8888 (visual monitoring) |
| Output | Pass/fail signal to scheduler — failed data blocks report generation |

The quality gate prevents "data gap shells" — reports that present missing data as if complete. If required fields are absent or stale, the gate halts downstream processing.

### Layer 3: AI Analysis (Dual-Engine Council)

| Aspect | Detail |
|--------|--------|
| Input | Validated YAML data from Layer 2 |
| Engine A | Hermes GLM-5.2 — fundamentals, valuation, options |
| Engine B | Codex GPT-5.5 — technicals, capital flow, risk, fact-check of Engine A |
| Engine C | Optional — macro, industry, sentiment (activated for T15/T11) |
| Model hierarchy | GLM-5.2 (primary, 1M context) → GPT-5.5 (fallback 1) → DeepSeek-V4-Pro (fallback 2) → Qwen3 14B (local, formatting/dedup) |
| Judge model | DeepSeek-V4-Pro — used for subagent review |
| Output | Structured analysis with consensus, divergence, and confidence annotations |

### Layer 4: Report Generation & Delivery (Output)

| Aspect | Detail |
|--------|--------|
| Input | Synthesized analysis from Layer 3 |
| Report types | 13 types (T1/T2/T3/T11/T15/T16/T17/T18/T19/T25/T26/R1-R3/Visual) |
| Wrappers | 30+ wrapper scripts, each with `--caption-only` and `--telegram-chat-id` |
| Delivery channels | Telegram Bot API + Feishu OpenAPI |
| Output format | Markdown reports with plain-text frontmatter (YAML blocks in reports are treated as code defects — zero tolerance) |
| Delivery target | Zero missed deliveries |

---

## 3. Component Responsibilities

| Component | Responsibility | Location |
|-----------|---------------|----------|
| Cron Scheduler | Time-based job execution, 115 jobs | `~/.hermes/cron/` |
| Collection Scripts | Fetch and normalize data from 12+ sources | `~/.hermes/cron/scripts/` |
| Quality Gate | Validate data freshness and completeness | Ports 8080/8888 |
| Engine A (Hermes) | Fundamental analysis, valuation, options assessment | Hermes Agent runtime |
| Engine B (Codex) | Technical analysis, capital flow, fact-checking | Codex runtime |
| Council/Synthesis | Merge engine outputs, flag divergences, annotate confidence | Hermes Agent runtime |
| Report Wrappers | Format and deliver reports to Telegram/Feishu | `~/.hermes/cron/scripts/` |
| Budget Watchdog | Monitor monthly API spend, enforce ~$55 cap | `budget_status.json` |
| Engineering Constitution | 10-rule constraint on all AI code modifications | `skills/engineering_constitution.md` |
| Runtime Guard | System health monitoring | Frozen module |
| Send Reports | Push delivery pipeline | Frozen module |

---

## 4. Key Design Decisions

### 4.1 Why YAML for Data Storage (Not a Database)

TMC stores all intermediate data as YAML files, not in a relational database. Rationale:
- Zero operational overhead — no database server to maintain.
- Human-readable — debugging is as simple as opening a file.
- Atomic writes — Python's yaml.safe_dump + temp file rename ensures consistency.
- The dataset is small (82 tickers) — performance is not a constraint.

Trade-off: No query language, no concurrent write protection. Acceptable for a single-user system on a single machine.

### 4.2 Why a Dual-Engine Council (Not a Single LLM)

A single LLM can produce plausible-sounding analysis with incorrect numbers. The dual-engine pattern forces independent verification:
- Engine A produces analysis.
- Engine B independently checks Engine A's numbers.
- If verification passes, confidence increases.
- If verification fails, the divergence is flagged in the report.

This costs more API calls but prevents the most dangerous failure mode: confident wrongness.

### 4.3 Why a Model Hierarchy (Not One Model)

The cascade GLM-5.2 → GPT-5.5 → DeepSeek-V4-Pro → Qwen3 14B serves two purposes:
- **Cost control:** GLM-5.2 is the cheapest frontier model in the chain. Fallbacks only activate on failure.
- **Resilience:** If one provider has an outage, the system continues operating.
- **Local fallback:** Qwen3 14B runs on-device via Ollama. Even if all API providers are down, formatting and deduplication still work.

### 4.4 Why an Engineering Constitution

The system has 232 Python scripts across 425 compilation units, many tightly coupled. Uncontrolled refactoring is an existential risk. The 10-rule constitution (derived from Karpathy's CLAUDE.md) enforces:
- Read before write (understand existing patterns before modifying).
- Surgical changes (smallest possible diff).
- No new dependencies without justification.
- Verification before declaring a fix complete.

This is not a style guide. It is a survival protocol for a solo-developed system.

### 4.5 Why WATCHLIST_ONLY

The system deliberately has no broker API connection and cannot execute trades. Rationale:
- Regulatory: The system is a research tool, not a registered investment advisor.
- Safety: Automated trading with LLM-generated signals introduces catastrophic risk.
- Focus: The system's value is in analysis quality, not execution speed.

---

## 5. Known Limitations and Trade-offs

| Limitation | Detail | Mitigation |
|------------|--------|------------|
| yfinance rate limiting | Yahoo Finance frequently rate-limits requests. 24 scripts are not yet connected to the fallback chain. | data_fallback_chain.py exists but needs per-script integration. Pending in maintenance backlog. |
| Scheduler resource contention | Multiple cron jobs fire in the same minute (e.g. 19:00 EDT batch), causing CPU/memory contention. | Pending dedicated stagger or queue optimization. |
| No Level 2 data | The system cannot access real-time order book depth. | Architectural — would require a paid data feed. Not planned. |
| Single point of failure | One Mac mini. Hardware failure = total system outage. | Acceptable for a personal research tool. Backups are file-level. |
| Code quality debt | 17 bare except blocks, 61 hardcoded paths, 36 unclosed file handles, 36 subprocess calls without timeout. | Does not affect current operation. Tracked in freeze log for gradual cleanup. |
| No concurrent write protection | YAML files are written by collection scripts without file locks. | Acceptable because the cron scheduler serializes jobs. Risk exists if manual runs overlap with scheduled jobs. |
| LLM dependency | System depends on external LLM APIs. If all providers are down, only local Qwen3 14B remains operational. | Model hierarchy provides 3 levels of fallback. Local model handles formatting but cannot generate analysis. |
| Budget constraint | ~$55/month cap limits the volume of LLM calls and data sources. | Budget watchdog enforces the cap. System prioritizes critical reports when budget is low. |

---

## 6. Security Boundary

TMC operates within a strict security perimeter:

- **No broker API:** The system cannot execute trades. No broker credentials are stored.
- **No user data:** The system does not collect or store personal data from any user other than the operator.
- **Local storage:** All data files, configuration, and credentials are stored locally on the Mac mini. No cloud storage.
- **API key isolation:** API keys and tokens are stored in environment variables and local config files. They are never committed to version control.
- **Proxy boundary:** All outbound traffic flows through a single proxy (127.0.0.1:10808). No direct internet access from collection scripts.
- **Codex audit:** 230 files scanned by Codex code review. 0 high-severity bugs found.
- **Engineering Constitution:** 10 rules constrain all AI-assisted code modifications, preventing unreviewed changes.

---

*Architecture document v1.1.1 — Generated 2026-06-30.*
*All architectural descriptions verified against actual system files.*
