# Architecture

> **TradingMapClaw (TMC) v2.0 | 2026-07-12**
> This document describes the system's design principles, data flow, component responsibilities, key decisions, and known limitations.

---

## 1. Design Principles

### 1.1 Budget Discipline

Every design decision is filtered through a hard monthly budget cap of **$55 USD (¥400 CNY)**. This constraint shapes the entire architecture:

- No cloud infrastructure — the system runs on a single Mac mini (Apple Silicon, macOS 26.5.1).
- No premium data feeds (Bloomberg, Refinitiv). Data comes from 12+ free or low-cost sources.
- LLM costs are monitored by a custom budget watchdog. The model fallback chain (GLM-5.2 → GPT-5.6 → DeepSeek V4 Pro → Qwen3 14B local) cascades from cheapest-and-first-tried to most-expensive-last-resort.
- The local model (Qwen3 14B via Ollama) handles formatting, deduplication, and free voting — tasks that do not require frontier reasoning — to conserve API budget.
- Actual measured spend runs around $7/month (13.5% of the cap); see the [README cost breakdown](README.md#monthly-cost).

### 1.2 Dual-Engine, Multi-Model Council

The core analytical architecture is not one model, and not a simple maker-checker pair — it is a **Dual-Engine architecture running a Multi-Model Council**:

- **Dual-Engine** = two independent AI engines — **Engine 1: Hermes Agent** (orchestrator) and **Engine 2: Codex** (independent checker) — that cross-check each other across three analysis passes:
  - **Pass A — Engine 1 / Hermes Agent** (Nous Research, GLM-5.2): orchestration plus fundamental, valuation, and insider reasoning.
  - **Pass B — Engine 2 / Codex (GPT-5.6)**: independent technical/flow analysis, and — critically — mandatory cross-verification of Pass A's numbers.
  - **Pass C — Engine 1 / Hermes Agent** (Nous Research, GLM-5.2): macro, industry, sentiment, and regulatory reasoning.
- **Multi-Model Council** = the models the two engines convene across the three analysis passes: **DeepSeek V4 Pro**, **GLM-5.2**, and **GPT-5.6** (plus local **Qwen3 14B** for free voting).
- The council's role split and weighting is **Pass A / B / C**:
  - **Pass A** (Hermes, GLM-5.2) — fundamentals, valuation, insider activity (40%).
  - **Pass B** (Codex, GPT-5.6) — technicals, capital flow, options, and mandatory cross-verification of Pass A's numbers (35%).
  - **Pass C** (Hermes, GLM-5.2) — macro, industry, sentiment, regulatory context (25%).
  - **Council War Room tiebreaker** (contested calls): DeepSeek → GLM-5.2 → GPT-5.6.

One model can be confidently wrong. A second engine catches it. A multi-model council decides. This is the single most defensible feature in the system — see [Section 3](#3-dual-engine-multi-model-analysis-flow) for the full execution flow.

### 1.3 Zero-Touch Automation

The system is designed to operate without human intervention during market hours:

- 118 cron jobs (117 enabled) handle data collection, analysis, report generation, and delivery.
- Reports are pushed to Telegram and Feishu via `bilingual_send.py`, a drop-in wrapper around the FROZEN `send_reports.py`.
- Quality gates validate data freshness and completeness before reports are generated.
- Error stubs and wrapper diagnostics are blacklisted from push delivery — users never receive broken reports.
- The system runs around the clock: collecting data before US market open (Beijing time), running analysis, delivering reports to the user's phone before, during, and after the trading session.

---

## 2. Data Flow

### Layer 1: Data Collection (Input)

| Aspect | Detail |
|--------|--------|
| Input format | HTTP API responses (JSON/HTML), RSS feeds, YAML config files |
| Collection & analysis scripts | 230+ Python scripts total (all compile) across `~/.hermes/scripts/` and `~/.hermes/cron/scripts/` |
| Scheduling | Hermes cron engine — 118 jobs, ~110 enabled, ~9 disabled |
| Job mix | 29 LLM-driven jobs · 76 script-only jobs |
| Proxy | All outbound traffic through `http://127.0.0.1:10808` |
| Output format | YAML files (stocks.yaml, news.yaml, analyst.yaml, sentiment_cache.json, insider_trades.yaml, etc.) |

Data collection scripts fetch from 12+ sources (Yahoo Finance/yfinance, FMP, Finnhub, SEC EDGAR, FRED, Reddit/ApeWisdom, NewsAPI/Alpha Vantage, Polymarket, GDELT, FinBERT local, CoinGecko, Binance), normalize the responses into structured YAML, and write to the shared data directory.

### Layer 2: Quality Gate (Pre-Gate)

| Aspect | Detail |
|--------|--------|
| Input | YAML files from Layer 1 |
| Validation | Data freshness check, field completeness check, schema validation |
| API | Port 8080 (programmatic access) |
| Dashboard | Port 8888 (visual monitoring) |
| Output | Pass/fail signal to scheduler — failed data blocks report generation |

The quality gate prevents "data gap shells" — reports that present missing data as if complete. If required fields are absent or stale, the gate halts downstream processing and the 4-level fallback chain (see §8) is invoked before anything is marked unavailable.

### Layer 3: Dual-Engine, Multi-Model Council

| Aspect | Detail |
|--------|--------|
| Input | Validated data from Layer 2 |
| Pass A | Hermes, GLM-5.2 — fundamentals, valuation, insider (weight 40%) |
| Pass B | Codex, GPT-5.6 — technicals, capital flow, options, cross-verification of A (weight 35%) |
| Pass C | Hermes, GLM-5.2 — macro, industry, sentiment, regulatory (weight 25%) |
| Model fallback chain | GLM-5.2 → GPT-5.6 → DeepSeek V4 Pro → Qwen3 14B (local, free) |
| Output | Structured analysis with consensus, divergence, and confidence annotations |

### Layer 4: Report Generation & Bilingual Delivery (Output)

| Aspect | Detail |
|--------|--------|
| Input | Synthesized analysis from Layer 3 |
| Report types | 13 types (T1/T2/T3/T11/T15/T16/T17/T18/T19/T25/T26/R1–R3/Visual) |
| Delivery layer | `bilingual_send.py` — drop-in wrapper, identical CLI args to frozen `send_reports.py` |
| Delivery channels | Telegram Bot API (English, native `.md`) + Feishu OpenAPI (Chinese, DeepSeek-translated `.cn.md`) |
| Output format | Markdown reports with plain-text frontmatter — YAML blocks inside report bodies are treated as code defects |
| Delivery target | Zero missed deliveries |

---

## 3. Dual-Engine, Multi-Model Analysis Flow

### 3.1 Why Multi-Engine?

A single LLM can produce a plausible-sounding analysis with wrong numbers. TMC splits analysis across three independent engines, each responsible for a specific domain, and forces Pass B to cross-verify Pass A's numbers before the final report is co-authored.

### 3.2 Pass Assignment

| Engine | Model | Domain | Weight | Output |
|--------|-------|--------|--------|--------|
| **Pass A** | Hermes, GLM-5.2 | Fundamentals + valuation + insider | 40% | Score 1-10, key metrics, DCF range, valuation verdict |
| **Pass B** | Codex, GPT-5.6 | Technicals + capital flow + options | 35% | Score 1-10, entry/stop levels, cross-verify verdict |
| **Pass C** | Hermes, GLM-5.2 | Macro + industry + sentiment + regulatory | 25% | Macro bias, industry rank, sentiment percentile, regulatory risk |

### 3.3 Execution Flow (All Must Complete)

```
Step 1: Pass C Pre-Load
  → Read macro/sentiment memory from previous runs
  → If no memory: fall back to sentiment_cache.json + macro.yaml
  → Output: macro context string

Step 2: Pass A (Fundamentals)
  → Receives Pass C context + all market data
  → Analyzes: revenue growth, margins, ROE/ROIC, PE/Forward PE/PEG, DCF, debt, insider
  → Output: fundamentals score + metrics + valuation range
  → If fails: ABORT (no partial report)

Step 3: Pass B (Technicals + Cross-Verification)
  → Receives Pass A's output
  → MUST verify Pass A's key numbers (PE, revenue growth, target price, 52w high/low)
  → If any number off by >5%: [CROSS-VERIFY] status: FAIL
  → Analyzes: RSI, MACD, BB, EMA, volume, institutional holdings, analyst targets, short interest, options P/C
  → Output: technicals score + entry/stop + cross-verify verdict
  → If fails: ABORT (no partial report)

Step 4: Cross-Verification Check
  → Parse Pass B's [CROSS-VERIFY] status
  → If PASS: confidence +0.1 (capped at 1.0)
  → If FAIL: flag discrepancies for divergence section

Step 5: Synthesis (Co-Authored)
  → Receives: Pass A output + Pass B output + Pass C data + cross-verify result
  → Co-authors unified 8-section report (not three reports stitched together)
  → Identifies consensus (what all agree on) and divergence (where they disagree, ≤3 points)
  → Outputs: scenario label (bullish / neutral / bearish) + weighted score + 3-scenario target table + position advice

Step 6: Pass C Memory Write-Back
  → Extract macro/sentiment sections from final report
  → Write to memory (namespace=engine_c) for future runs
```

### 3.4 Report Structure (8 Sections, ≤1200 Words)

| Section | Engine | Limit | Content |
|---------|--------|-------|---------|
| 1. Core Conclusion | Co-authored | ≤80 words | Verdict + rating + target range |
| 2. Fundamentals | Pass A | ≤220 words | Revenue/margins/ROE/valuation/DCF/balance sheet/insider → score 1-10 |
| 3. Technicals + Flow | Pass B | ≤220 words | Trend/support/resistance/RSI/MACD/BB/volume/institutional/analyst/short/options → score 1-10 + entry/stop |
| 4. Macro + Industry | Pass C | ≤120 words | Rate sensitivity, FX impact, industry growth, competition |
| 5. Sentiment | Pass C | ≤120 words | News sentiment, bull/bear split, analyst trend, retail vs institutional |
| 6. Regulatory | Pass C | ≤80 words | Pending regulatory matters or "no material risk" |
| 7. Consensus & Divergence | All | ≤150 words | What all agree on + where they disagree (≤3 points, each with adopted engine + reason) |
| 8. Final Verdict | Co-authored | — | Rating (★1-5) + weighted score + 3-scenario probability table + position advice + catalyst |

### 3.5 Hard Constraints

1. **All engines must complete** — no partial reports. Any engine failure → abort.
2. **Cross-verification mandatory** — Pass B must verify Pass A's numbers.
3. **Co-authorship** — final report is one unified article, not three reports stitched together.
4. **Consensus + divergence** — both must appear in Section 7.
5. **Rating required** — no "no recommendation" allowed. Must output scenario label (bullish / neutral / bearish) + target range.
6. **Plain language** — no jargon without explanation, e.g. "PEG (price/earnings-to-growth, lower = cheaper) 0.83."
7. **English only** — all prompts and outputs in English. Feishu gets Chinese translation via DeepSeek.

### 3.6 Interactive vs Cron

- **Interactive** (user requests a deep dive on a ticker): uses the `deep-analysis-dual-head` skill. Pass B is dispatched via `delegate_task`; Pass A/C run through Hermes directly. All outputs are collected before the unified report.
- **Cron** (`codex_analyst_wrapper.py`): 4-step sequential flow — Pass C pre-load → Pass A (Codex CLI) → Pass B (Codex CLI, cross-verify) → Synthesis (Codex CLI). All-must-complete gate.

### 3.7 Council War Room (Contested Calls)

For higher-stakes position decisions, a separate three-model voting protocol runs: **Round 1** (DeepSeek drafts) → **Round 2** (GLM-5.2 reviews) → **Round 3** (GPT-5.6 tiebreaker, only if Rounds 1-2 disagree). Output: final scenario label (bullish / neutral / bearish) + confidence/100.

---

## 4. Component Responsibilities

| Component | Responsibility | Location |
|-----------|---------------|----------|
| Cron Scheduler | Time-based job execution, 118 jobs | `~/.hermes/cron/` |
| Collection Scripts | Fetch and normalize data from 12+ sources | `~/.hermes/cron/scripts/` |
| Quality Gate | Validate data freshness and completeness | Ports 8080/8888 |
| Pass A (Hermes, GLM-5.2) | Fundamental analysis, valuation, insider | Hermes Agent runtime |
| Pass B (Codex, GPT-5.6) | Technical analysis, capital flow, cross-verification | Codex runtime |
| Pass C (Hermes, GLM-5.2) | Macro, industry, sentiment, regulatory | Hermes Agent runtime |
| Synthesis / Council Layer | Merge engine outputs, flag divergences, annotate confidence | Hermes Agent runtime |
| Report Wrappers | Format and deliver reports to Telegram/Feishu | `~/.hermes/cron/scripts/` |
| Budget Watchdog | Monitor monthly API spend, enforce $55 cap | `budget_status.json` |
| Engineering Constitution | 10-rule constraint on all AI code modifications | `skills/engineering_constitution.md` |
| Runtime Guard | System health monitoring | Frozen module |
| Send Reports | Push delivery pipeline | Frozen module |

---

## 5. T26 Supply Chain Alpha Pipeline (Summary)

T26 discovers investment targets by peeling supply chain layers across **8 sectors and 49 suppliers**, using a **5-layer onion-peel method** (Bottom/Raw → Ignored Middle → Core Equipment → Direct Beneficiary → End Brand). The alpha is typically found in Layer 4 — companies that don't make end products but hold chokepoints (e.g. AXTI's InP substrate, Entegris's CMP/high-purity chemicals).

Scoring uses **8 dimensions** (biz_momentum, supply_tension, mkt_blindness, linkage, rev_accel, valuation, technicals, sentiment). Classification: `alpha_score > 0.65 AND mkt_blindness > 0.70` → CANDIDATE, else WATCH. Output feeds `sc_alpha_{SECTOR}.json`, consumed by both T11 (Alpha Radar) and the T26 onion report.

---

## 6. T11 Alpha Radar (Summary)

T11 scans **8 data sources** (ApeWisdom surge, social watchlists, FMP screener, news mentions, T26 supply-chain output, stocks.yaml fallback, analyst data) to surface "new face" tickers outside the B/C watchlist. Hard filters remove invalid/OTC/meme/penny/micro-cap names. Output is **3-tier**: 🔴 High-Conviction (α≥70), 🟡 Emerging (α50-69), 🟠 Speculative Surge (α<50 + social surge).

---

## 7. Data Sources & Fallback Chain

### 7.1 Data Sources (12)

Yahoo Finance (yfinance), FMP API, Finnhub API, SEC EDGAR/XBRL, FRED, Reddit (ApeWisdom), NewsAPI/Alpha Vantage, Polymarket, GDELT, FinBERT (local), CoinGecko, Binance REST API.

### 7.2 4-Level Fallback Chain

Every data field has a 4-level fallback. No "data missing" is allowed without trying all levels:

| Level | Method | Example |
|-------|--------|---------|
| 1 | Direct API call | Yahoo Finance Chart API |
| 2 | Proxy route | Via 127.0.0.1:10808 |
| 3 | Python library | yfinance `Ticker().info` |
| 4 | Local cache | stocks.yaml, marked `[CACHED: date]`, max staleness 3 trading days |

**Special fallbacks:** Crypto: CoinGecko → Binance REST API (no auth, no rate limit). Macro 10Y: FRED → Yahoo ^TNX via proxy → macro.yaml cache. Technicals: `technical_signals.json` (≤3 days) → `precompute.py`. Options: `[N/A - not collected]` (allowed missing).

---

## 8. Bilingual Delivery

- **Telegram** receives the English original `.md` file directly via `bilingual_send.py` (bypasses the FROZEN `send_reports.py` Chinese formatter).
- **Feishu** receives the Chinese translation (`report.cn.md`) via DeepSeek API translation, with GLM-4-Flash as fallback if DeepSeek fails.
- The LLM generates **native English** reports (more precise for financial data than translated English); DeepSeek translates to **full Chinese** for Feishu readers.
- `send_reports.py` (1360 lines) is FROZEN — `bilingual_send.py` is a drop-in wrapper accepting identical CLI arguments.

---

## 9. Key Design Decisions

### 9.1 Why YAML for Data Storage (Not a Database)

TMC stores all intermediate data as YAML files, not in a relational database:
- Zero operational overhead — no database server to maintain.
- Human-readable — debugging is opening a file.
- Atomic writes — `yaml.safe_dump` + temp file rename ensures consistency.
- The dataset is small (82 tickers) — performance is not a constraint.

Trade-off: no query language, no concurrent write protection. Acceptable for a single-user system on a single machine.

### 9.2 Why Dual-Engine + Council (Not a Single LLM)

A single LLM can produce plausible-sounding analysis with incorrect numbers. The dual-engine pattern forces independent verification: Pass A produces analysis, Pass B independently checks Pass A's numbers, confidence rises on verification pass, and divergence is flagged in the report on failure. This costs more API calls but prevents the most dangerous failure mode: confident wrongness. Layering a multi-model council (DeepSeek V4 Pro + GLM-5.2 + GPT-5.6) on top further reduces the risk that a single vendor's model quirks silently shape every report.

### 9.3 Why a Model Fallback Chain (Not One Model)

The cascade GLM-5.2 → GPT-5.6 → DeepSeek V4 Pro → Qwen3 14B serves two purposes:
- **Cost control:** cheaper models are tried first; fallbacks only activate on failure.
- **Resilience:** if one provider has an outage, the system continues operating.
- **Local fallback:** Qwen3 14B runs on-device via Ollama. Even if all API providers are down, formatting and deduplication still work.

### 9.4 Why an Engineering Constitution

The system has 230+ Python scripts, many tightly coupled. Uncontrolled refactoring is an existential risk. The 10-rule constitution (derived from Karpathy's CLAUDE.md) enforces read-before-write, surgical changes, no new dependencies without justification, and verification before declaring a fix complete. This is a survival protocol, not a style guide.

### 9.5 Why WATCHLIST_ONLY

The system deliberately has no broker API connection and cannot execute trades:
- **Regulatory:** the system is a research tool, not a registered investment advisor.
- **Safety:** automated trading with LLM-generated signals introduces catastrophic risk.
- **Focus:** the system's value is in analysis quality, not execution speed.

---

## 10. Frozen Modules & Engineering Constitution

### 10.1 Frozen Modules

The following are FROZEN and must not be modified without explicit operator approval:

- `send_reports.py` — push infrastructure (1360 lines; bypassed, not replaced, by `bilingual_send.py`)
- `runtime_guard` — task guard system
- `scheduler` — cron engine
- `stocks.yaml` schema — data schema

### 10.2 Engineering Constitution

Source: Karpathy `CLAUDE.md` — distilled 2026-06-29. Priority: HIGHEST.

1. **Read before write** — read relevant files and existing patterns before making changes
2. **Think before code** — state what you're doing, key assumptions, tradeoffs in one sentence
3. **Simplicity** — write minimal code for the current problem, no over-abstraction
4. **Surgical changes (hard rule)** — smallest diff possible, only touch what needs touching
5. **Verification** — write a failing test first, then fix
6. **Goal-driven** — define success criteria before starting; plan before executing
7. **Debugging** — investigate, don't guess. Read the full error. One change at a time
8. **Dependencies (hard rule)** — check stdlib/existing libs before adding new dependencies
9. **Communication** — explain what changed, why, and what's uncertain
10. **Failure modes** — watch for Kitchen Sink / Wrong Abstraction / Happy Path / Runaway Refactor

---

## 11. Known Limitations and Trade-offs

| Limitation | Detail | Mitigation |
|------------|--------|------------|
| yfinance rate limiting | Yahoo Finance frequently rate-limits requests. Some scripts are not yet connected to the fallback chain. | `data_fallback_chain.py` exists but needs per-script integration. Pending in maintenance backlog. |
| Scheduler resource contention | Multiple cron jobs fire in the same minute, causing CPU/memory contention. | Pending dedicated stagger or queue optimization. |
| No Level 2 data | The system cannot access real-time order book depth. | Architectural — would require a paid data feed. Not planned. |
| Single point of failure | One Mac mini. Hardware failure = total system outage. | Acceptable for a personal research tool. Backups are file-level. |
| No concurrent write protection | YAML files are written by collection scripts without file locks. | Acceptable because the cron scheduler serializes jobs. |
| LLM dependency | System depends on external LLM APIs. If all providers are down, only local Qwen3 14B remains operational. | Model fallback chain provides 3 levels of fallback. Local model handles formatting but cannot generate analysis. |
| Budget constraint | $55/month cap limits the volume of LLM calls and data sources. | Budget watchdog enforces the cap continuously. System prioritizes critical reports when budget is low. |
| yfinance cold cache | First run after a code change can take 5–10 minutes to warm the 7-day TTL cache. | Acceptable — subsequent runs are warm. |

---

## 12. Security Boundary

TMC operates within a strict security perimeter:

- **No broker API:** the system cannot execute trades. No broker credentials are stored.
- **No user data:** the system does not collect or store personal data from any user other than the operator.
- **Local storage:** all data files, configuration, and credentials are stored locally on the Mac mini. No cloud storage.
- **API key isolation:** API keys and tokens are stored in environment variables and local config files. Never committed to version control.
- **Proxy boundary:** all outbound traffic flows through a single proxy (127.0.0.1:10808). No direct internet access from collection scripts.
- **Hermes+Codex cross-audit:** all scripts scanned. See [SECURITY.md](SECURITY.md) for the full posture.
- **Engineering Constitution:** 10 rules constrain all AI-assisted code modifications, preventing unreviewed changes.

Full policy: [SECURITY.md](SECURITY.md) · Contribution rules: [CONTRIBUTING.md](CONTRIBUTING.md)

---

*Architecture document v2.0 | 2026-07-12. All architectural descriptions verified against [README_v161_SOURCE.md](README_v161_SOURCE.md).*
