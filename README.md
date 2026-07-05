# TradingMapClaw (TMC)

> **v1.8 | 2026-07-04**
> **One Hand. One Bag. One System.**
> A production-grade, three-engine AI research system running a multi-model council for US equities and crypto — built and run solo on a single Mac mini for **~$55/month** (actual spend ~$7/mo).

> ### 🖐️ Read this first → [**STORY.md**](STORY.md)
>
> Eight surgeries. One working hand (right-arm brachial plexus avulsion, ~95% function lost). A permanent ostomy. Zero prior coding background. In **two months**, I taught myself to build everything in this repository.
>
> This project is not a demo of what AI can do. It is proof of what a person can do when they refuse to accept the dimensions of the room they were given. **Not pity. Visibility.** — [full story](STORY.md) · [my 2019 essay on disability & employment](https://www.linkedin.com/in/mickey-wei-5b95aa95/recent-activity/articles/)

[![Status](https://img.shields.io/badge/status-v1.8%20Active-2a6b73)](CHANGELOG.md)
[![Scripts](https://img.shields.io/badge/scripts-502%2B%20compile-5ba8b0)](ARCHITECTURE.md)
[![Cron](https://img.shields.io/badge/cron%20jobs-119-5ba8b0)](ARCHITECTURE.md)
[![Engines](https://img.shields.io/badge/engines-3-5ba8b0)](ARCHITECTURE.md)
[![Skills](https://img.shields.io/badge/SKILL.md-93%2B-5ba8b0)](ARCHITECTURE.md)
[![Coverage](https://img.shields.io/badge/tickers-82-5ba8b0)](#coverage)
[![Delivery](https://img.shields.io/badge/delivery-bilingual%20EN%2FZH-5ba8b0)](CHANGELOG.md)
[![Cost](https://img.shields.io/badge/cost-%2455%2Fmonth%20cap-2a6b73)](#monthly-cost)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## What is this

One model can be confidently wrong. Two engines catch it. A council of three decides.

TradingMapClaw is a zero-touch, budget-disciplined research pipeline built around that idea. It collects market data from **12+ free/low-cost sources**, runs it through a **Three-Engine council** — **Engine A** (Hermes / GLM-5.2: fundamentals, valuation, insider — 40%), **Engine B** (Codex / GPT-5.5: technicals, capital flow, options, cross-verification — 35%), and **Engine C** (Hermes / GLM-5.2: macro, industry, sentiment, regulatory — 25%) — with a **Council War Room** (DeepSeek → GLM-5.2 → GPT-5.5 tiebreaker) resolving disagreements. It passes the result through a quality gate and delivers structured reports **bilingually**: native English to Telegram, full Chinese (DeepSeek translation) to Feishu — fully automated, around the clock, every trading day.

It has **no broker connection and cannot execute trades**. It is a research tool: `WATCHLIST_ONLY`.

### Why this is different

A single LLM can produce a plausible-sounding report with a wrong number in it, and nothing about the prose will tell you that. TMC's answer is structural, not cosmetic:

- **Cross-engine verification** — Engine B (Codex/GPT-5.5) independently re-derives Engine A's (Hermes) key numbers — PE, revenue growth, target price, 52-week range. If they agree within 5%, confidence rises. If they don't, the discrepancy is printed in the report, not smoothed over.
- **Multi-Model Council** — DeepSeek V4 Pro, GLM-5.2, and GPT-5.5 each own a role (fundamentals / technicals / macro-sentiment) so no single vendor's model, training bias, or outage can silently define the whole analysis.
- **Council War Room** — for contested calls, a three-round vote (DeepSeek → GLM-5.2 review → GPT-5.5 tiebreaker) produces one BUY/HOLD/SELL with a confidence score, not three shrugging opinions.

Full mechanics in [ARCHITECTURE.md](ARCHITECTURE.md).

### By the numbers

| Metric | Value |
|--------|-------|
| Python scripts | **502+** (all compile) |
| Cron jobs | **119** (~110 enabled) |
| Analysis engines | **3** (A/B/C council) |
| SKILL.md skill files | **93+** |
| Coverage tickers | **82** (75 unique) across 5 groups |
| Data sources | **12+** free / low-cost |
| Report types | **13** (T1/T2/T3/T11/T15/T16/T17/T18/T19/T25/T26/R1–R3/Visual) |
| Delivery | **Bilingual** — English (Telegram) + Chinese (Feishu, DeepSeek) |
| Monthly cost | **~$55 USD** hard cap (actual spend tracks near ~$7; see [cost breakdown](#monthly-cost)) |
| Runtime | macOS 26.5.1 · single Mac mini (Apple Silicon) |

---

## Architecture at a glance

```
                    ┌─────────────────────────────────────────┐
                    │         Data Sources (12+)              │
                    │  Yahoo Finance · FMP · Finnhub · SEC    │
                    │  FRED · Reddit · NewsAPI · Polymarket   │
                    │  EDGAR · yfinance · ApeWisdom · GitHub  │
                    │  GDELT · CoinGecko · Binance            │
                    └────────────────┬────────────────────────┘
                                     │ proxy:127.0.0.1:10808
                    ┌────────────────▼────────────────────────┐
                    │      Cron Scheduler (119 jobs)          │
                    │   502+ Python scripts (all compile ✓)   │
                    │   LLM-driven + script-only mix          │
                    └────────────────┬────────────────────────┘
                                     │
                    ┌────────────────▼────────────────────────┐
                    │        Quality Gate / Pre-Gate          │
                    │   4-Level Fallback Chain                │
                    │   Ports: 8080 (API) · 8888 (Dashboard)  │
                    └────────────────┬────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
  ┌──────▼──────┐          ┌────────▼────────┐          ┌───────▼──────┐
  │  Engine A   │          │    Engine B      │          │  Engine C    │
  │  Hermes     │          │    Codex         │          │  Hermes      │
  │  GLM-5.2    │          │    GPT-5.5       │          │  GLM-5.2     │
  │ Fundamentals│          │ Technicals/Flow  │          │ Macro/Sent   │
  │  Valuation  │          │ Cross-verify A   │          │  Regulatory  │
  │  Insider    │          │  Options         │          │  Industry    │
  └──────┬──────┘          └────────┬────────┘          └───────┬──────┘
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     │
                    ┌────────────────▼────────────────────────┐
                    │      Synthesis / Council Layer          │
                    │   Engine B verifies Engine A's numbers  │
                    │   If pass → confidence +0.1             │
                    │   Consensus · Divergence · Co-author    │
                    │   All engines must complete (no partial)│
                    └────────────────┬────────────────────────┘
                                     │
                    ┌────────────────▼────────────────────────┐
                    │     Bilingual Delivery Layer            │
                    │   English (Telegram) · Chinese (Feishu) │
                    └────────────────┬────────────────────────┘

    Model fallback chain: GLM-5.2 → GPT-5.5 → DeepSeek V4 Pro → Qwen3 14B (local)
    Translation: DeepSeek API (primary) → GLM-4-Flash (fallback)
    Delivery: English → Telegram · Chinese → Feishu
```

Full detail — including the six-step execution flow, hard constraints, and interactive-vs-cron paths — in [ARCHITECTURE.md](ARCHITECTURE.md).

The council is **not a vote first, ask questions later** — it is structured cross-verification. Engine B actively re-checks Engine A's numbers before synthesis. Divergences are flagged, not hidden.

---

## Coverage

82 tickers across 5 groups:

- **A · Macro** (6) — SPX, NDX, DJI, GLD, WTI, BTC
- **B · Core Holdings** (8) — MSFT · META · NVDA · CRWV · RKLB · AVGO · NOW · SPCX
- **C · Hot + Watchlist** (56) — 10 high-attention names + 46-ticker rolling watchlist
- **D · Crypto** (13) — majors + selected alts

75 unique tickers total (some overlap across groups).

---

## Monthly cost

**Headline: ~$55/month operating cap.** Actual measured spend runs far under that ceiling.

| Component | Monthly Cost ($) | Basis |
|-----------|------------------|-------|
| T2 + T3 daily reports (GPT-5.5) | ~$4.68 | 44 calls/mo, actual logged cost |
| Other Hermes agent jobs (DeepSeek/GLM) | ~$1.15 | ~338 calls/mo, actual token rates |
| Codex CLI (T26, bull/bear, etc.) | ~$1.56 | 214 logged calls over 34 days |
| DeepSeek translation (Feishu) | ~$0.04 | 22 reports/mo × ~5K tokens |
| **Actual total** | **~$7.43** | 13.5% of the $55 budget cap |
| **Budget cap** | **$55** | Hard ceiling, continuously enforced |

Why it stays cheap: the majority of the 119 jobs are script-only (zero LLM cost), DeepSeek V4 Pro handles the majority of LLM calls at ~$0.0003/1K tokens, and local Qwen3 14B is free. See [README full cost breakdown](README_v161_SOURCE.md) methodology and [ARCHITECTURE.md](ARCHITECTURE.md) for the fallback chain.

---

## Engineering Constitution

Every AI-assisted change is bound by 10 rules (derived from Karpathy's `CLAUDE.md`):

1. Read before write · 2. Think before code · 3. Simplicity · 4. Surgical changes ·
5. Verification · 6. Goal-driven · 7. Debug, don't guess · 8. No new dependencies without justification ·
9. Communicate uncertainty · 10. Watch failure modes.

This is a survival protocol for a solo-developed, 502+-script system, not a style guide. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Status: v1.8 — Active

TMC is at **v1.8** (2026-07-04), in daily operation and maintenance. Recent work: two rounds of joint Hermes+Codex bug hunting closed **14 bugs**, the three-engine council flow was hardened with mandatory cross-verification, and the budget tracker was rewritten to read real Codex CLI + Hermes usage logs.

**What shipped through v1.8:**

- **Three-engine deep analysis** — Engine A (fundamentals/valuation/insider, 40%) → Engine B (technicals/capital flow/options/cross-verification, 35%) → Engine C (macro/industry/sentiment/regulatory, 25%), with a Council War Room (DeepSeek → GLM-5.2 → GPT-5.5 tiebreaker) and an all-must-complete gate (no partial reports).
- **14 bugs found and fixed** across two joint-audit rounds, including a critical `HERMES_HOME` undefined-variable bug that had silently disabled Engine C's memory for every run.
- **Budget tracker fix** — `token_budget_check.py` now aggregates real costs from `codex_usage.jsonl` and `quality_scores.csv` instead of showing a stale ¥0.00; actual spend is ~$7/mo against the $55 cap.
- **Readiness audits** — joint Hermes+Codex audits, all items PASS or FIXED (T26 race condition resolved, multi-engine timeout resolved).

Full version history: [CHANGELOG.md](CHANGELOG.md) · Security posture: [SECURITY.md](SECURITY.md)

---

## Work with me

I help solo operators and serious investors build their own low-cost, production-grade AI research systems — without needing to first lose function in one hand.

| Service | What you get | Price |
|---------|--------------|-------|
| **Quick Consult + Templates** | 30-min call + Python script framework + cron templates | **$79** |
| **AI Workflow Audit** | 30-page written analysis + architecture map + cost model | **$399** |
| **System Blueprint** | 90-min deep dive + custom roadmap + 30-day support | **$699** |
| **Skill Packs** | Budget Watchdog · Cron Recovery · Maker-Checker · Quality Gate · Model Fallback · Prompt Governance · Data Fallback | **$19–99** |

- **Book a call / audit:** see the landing page at [tradingmapclaw.com](https://www.tradingmapclaw.com)
- **Writing:** [Substack @tradingmapclaw](https://tradingmapclaw.substack.com) · [Medium @tradingmapclaw](https://medium.com/@tradingmapclaw)
- **X:** [@Tradingmapclaw](https://x.com/tradingmapclaw) · **LinkedIn:** [@Tradingmapclaw](https://www.linkedin.com/company/tradingmapclaw/)
- **Telegram:** [@tradingmapclaw](https://t.me/tradingmapclaw) · **WhatsApp/Phone:** [+44 7857 086337](https://wa.me/447857086337)
- **Email:** [contact@tradingmapclaw.com](mailto:contact@tradingmapclaw.com)

### Support

If the open-source work or writing helped you, a tip keeps the $55/month system running:

- **PayPal:** [@JiaJunWei162](https://paypal.me/JiaJunWei162)
- **Wise:** @jiajunw59

---

## About / The Story

I build systems that catch their own mistakes. That instinct did not come from a computer science background — I didn't have one until two months before this repository existed. It came from a life that repeatedly forced me to build verification into everything, because there was no room for anyone, including myself, to assume I'd get it right the easy way.

**Not pity. Visibility.**

Before I was twenty, a hit-and-run collision tore the nerves in my right arm — a brachial plexus avulsion that cost me roughly 95% of the function in my right hand. I relearned everything left-handed: tying shoelaces, writing, typing. I sat China's national college entrance exam, the gaokao, one-handed, every subject, every page.

I built a career anyway — back-office operations at **Wells Fargo, Deutsche Bank, UBS, JPMorgan, and eToro**: trade settlement, reconciliation, maker-checker controls, the plumbing that keeps global finance from breaking. Not front office. Not glamorous. But it is where you learn, at a granular level, that every number that reaches a client has already been checked by someone whose job is to doubt it. That habit of mind — never trust a single unverified number — is the same principle now running inside TMC's three-engine cross-verification.

Then came a second, unrelated collapse: ulcerative colitis, an autoimmune disease that attacked my colon. Eight surgeries over eight years. What began as a temporary ileostomy became, after complications, a **permanent ostomy** I manage every day. Two conditions, one body, both mostly invisible unless I choose to talk about them.

In May 2026, with zero prior coding background, I started building anyway. AI became my engineering partner — not a crutch, but a collaborator that could type at the speed of my thoughts, because my left hand alone couldn't keep up with what I wanted to build. Two months later: TradingMapClaw. 502+ Python scripts. 119 scheduled jobs. A three-engine, multi-model council that catches its own errors before they reach a report. It runs around the clock while I sleep, and it does not know or care that it was built by a man with one working hand and a stoma bag.

**Ability first, background second.** The story is why you might stop reading for a second. The 502+ scripts, the 119 cron jobs, and the cross-verification protocol are why you should keep going. → **Read the full story in [STORY.md](STORY.md)**, including the medical history in detail, the career walls that closed and the ones that opened anyway, and what "not pity, visibility" actually asks of you.

If you're living with a brachial plexus injury, ulcerative colitis, IBD, Crohn's, or a permanent ostomy: you are not invisible.

---

## Disclaimer

**For Research Purposes Only. Not Investment Advice.** TradingMapClaw performs no order routing and holds no broker connections. Past research performance does not guarantee future results. `WATCHLIST_ONLY`.

---

## 中文

本项目提供完整的中文文档：[README_CN.md](README_CN.md) · [ARCHITECTURE_CN.md](ARCHITECTURE_CN.md) · [SECURITY_CN.md](SECURITY_CN.md) · [CONTRIBUTING_CN.md](CONTRIBUTING_CN.md) · [CHANGELOG_CN.md](CHANGELOG_CN.md) · [STORY_CN.md](STORY_CN.md)

---

*README v1.8 | 2026-07-04 · © 2026 Mickey Wei · [tradingmapclaw.com](https://www.tradingmapclaw.com)*
