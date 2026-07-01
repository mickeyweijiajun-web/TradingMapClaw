# TradingMapClaw (TMC)

> **One Hand. One Bag. One System.**
> A production-grade, dual-engine AI research system for US equities and crypto — built and run solo on a single Mac mini for **~$55/month**.

> ### 🖐️ Read this first → [**STORY.md**](STORY.md)
>
> Eight surgeries. One working hand (right-arm brachial plexus avulsion, ~95% function lost). A permanent ostomy. Zero prior coding background. In **two months**, I taught myself to build everything in this repository.
>
> This project is not a demo of what AI can do. It is proof of what a person can do when they refuse to accept the dimensions of the room they were given. **Not pity. Visibility.** — [full story](STORY.md) · [my 2019 essay on disability & employment](https://www.linkedin.com/in/mickey-wei-5b95aa95/recent-activity/articles/)

[![Status](https://img.shields.io/badge/status-FROZEN%20v1.1.4-2a6b73)](CHANGELOG.md)
[![Scripts](https://img.shields.io/badge/scripts-468%20compile-5ba8b0)](ARCHITECTURE.md)
[![Cron](https://img.shields.io/badge/cron%20jobs-115-5ba8b0)](ARCHITECTURE.md)
[![Coverage](https://img.shields.io/badge/tickers-82-5ba8b0)](#coverage)
[![Bugs](https://img.shields.io/badge/high--severity%20bugs-0-2a6b73)](SECURITY.md)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## What is this

TradingMapClaw is a zero-touch, budget-disciplined research pipeline. It collects market data from **12+ free/low-cost sources**, runs it through a **dual-engine AI council** (Hermes GLM-5.2 as Maker, Codex GPT-5.5 as Checker), passes it through a quality gate, and delivers **13 report types** to Telegram and Feishu — fully automated, overnight, every trading day.

It has **no broker connection and cannot execute trades**. It is a research tool: `WATCHLIST_ONLY`.

### By the numbers

| Metric | Value |
|--------|-------|
| Python scripts | **468** (425/425 compile) |
| Cron jobs | **115** (106 enabled) |
| Coverage tickers | **82** across 5 groups |
| Data sources | **12+** free / low-cost |
| Report types | **13** (T1/T2/T3/T11/T15/T16/T17/T18/T19/T25/T26/R1–R3/Visual) |
| Monthly cost | **~$55 USD** hard cap |
| High-severity bugs | **0** (230 files, Codex-reviewed) |
| Runtime | macOS 26.5.1 · single Mac mini (Apple Silicon) |

---

## Architecture at a glance

```
Layer 1  Data Collection   → 226 scripts · 115 cron jobs · 12+ sources → YAML
Layer 2  Quality Gate      → freshness + completeness + schema (ports 8080/8888)
Layer 3  Dual-Engine Council
           Engine A (Maker)   Hermes GLM-5.2   → fundamentals · valuation · options
           Engine B (Checker) Codex GPT-5.5    → technicals · flow · risk · fact-check A
           Model hierarchy    GLM-5.2 → GPT-5.5 → DeepSeek-V4-Pro → Qwen3-14b (local)
Layer 4  Report + Delivery → 30+ wrappers → Telegram + Feishu
```

Full detail in [ARCHITECTURE.md](ARCHITECTURE.md).

The council is **not a vote** — it is structured adversarial review. Engine B actively tries to find errors in Engine A's numbers. Divergences are flagged, not hidden.

---

## Coverage

82 tickers across 5 groups:

- **A · Macro** (6) — indices, rates, volatility, macro anchors
- **B · Core Holdings** (8) — MSFT · META · NVDA · CRWV · RKLB · AVGO · NOW · SPCX
- **C · Hot + Watchlist** (55) — high-attention names + rolling watchlist
- **D · Crypto** (13) — majors + selected alts

---

## Engineering Constitution

Every AI-assisted change is bound by 10 rules (derived from Karpathy's `CLAUDE.md`):

1. Read before write · 2. Think before code · 3. Simplicity · 4. Surgical changes ·
5. Verification · 6. Goal-driven · 7. Debug, don't guess · 8. No new dependencies without justification ·
9. Communicate uncertainty · 10. Watch failure modes.

This is a survival protocol for a solo-developed system, not a style guide. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Status: FROZEN

TMC is **frozen at v1.1.1**. It is in daily operation and maintenance only. **No new features are accepted.** Bug reports, documentation fixes, and data-source suggestions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

Version history: [CHANGELOG.md](CHANGELOG.md) · Security posture: [SECURITY.md](SECURITY.md)

---

## Work with me

I help solo operators and serious investors build their own low-cost, production-grade AI research systems — without needing to first lose function in one hand.

| Service | What you get | Price |
|---------|--------------|-------|
| **Quick Consult + Templates** | 30-min call + Python script framework + cron templates | **$79** |
| **AI Workflow Audit** | 30-page written analysis + architecture map + cost model | **$399** |
| **System Blueprint** | 90-min deep dive + custom roadmap + 30-day support | **$699** |
| **Skill Packs** | Budget Watchdog · Cron Recovery · Dual-Engine Council · Quality Gate | **$19–99** |

- **Book a call / audit:** see the landing page at [tradingmapclaw.com](https://tradingmapclaw.com)
- **Writing:** [Substack @tradingmapclaw](https://tradingmapclaw.substack.com) · [Medium @tradingmapclaw](https://medium.com/@tradingmapclaw)
- **LinkedIn:** [Mickey Wei](https://www.linkedin.com/in/mickey-wei-5b95aa95/)
- **Telegram:** [@tradingmapclaw](https://t.me/tradingmapclaw) · **WhatsApp/Phone:** [+44 7857 086337](https://wa.me/447857086337)
- **Email:** [mickeyweijiajun@gmail.com](mailto:mickeyweijiajun@gmail.com)

### Support / Tip Jar

If the open-source work or writing helped you, a tip keeps the $55/month system running:

- **PayPal:** [@JiaJunWei162](https://paypal.me/JiaJunWei162)
- **Wise:** @jiajunw59
- **USDT (TRC20, preferred):** `TJTcyqznmky8sGrkhrYtoSHPbz2SoVzKWr`
- **USDT (ERC20):** `0xAc93190b396212d1cbA76a0bbC2ac05dc7413DE8`
- **BTC:** `bc1qqccdn7t6z0wzzwwkh2h6p5augvlanumuu78k2d`

---

## The story

Before I was twenty, a hit-and-run collision tore the nerves in my right arm — a brachial plexus avulsion that cost me ~95% of the function in my right hand. Three surgeries. I relearned everything left-handed and sat the national college entrance exam one-handed. Years later, inside the back offices of **Wells Fargo, Deutsche Bank, UBS, and JPMorgan**, I did the work with one hand and asked for no lowered standard. Then ulcerative colitis took my colon — five more surgeries across eight years, and a **permanent ostomy** I manage every day. Eight surgeries total.

In May 2026, with **no prior coding background**, I started building. AI became my engineering partner — not a crutch, but a collaborator that types at the speed of my thoughts, because my left hand alone couldn't keep up. Two months later: this system. It runs at 4 AM while I sleep, and it does not know or care that it was built by a man with one hand and a stoma bag. That is the point.

**I didn't overcome anything. I refused to be overcome.** → [Read the full story in STORY.md](STORY.md)

If you're living with brachial plexus injury, ulcerative colitis, IBD, Crohn's, or a permanent ostomy: you are not invisible. **Not pity. Visibility.**

---

## Disclaimer

**For Research Purposes Only. Not Investment Advice.** TradingMapClaw performs no order routing and holds no broker connections. Past research performance does not guarantee future results. `WATCHLIST_ONLY`.

---

*README v1.1.4 · © 2026 Mickey Wei · [tradingmapclaw.com](https://tradingmapclaw.com)*
