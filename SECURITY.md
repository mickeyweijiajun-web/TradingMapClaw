# Security Policy

> **TradingMapClaw (TMC) v1.8 | 2026-07-04**

## Security Boundary

TradingMapClaw (TMC) operates within a strict, deliberately constrained security perimeter, designed on a **least-capability** philosophy — only the permissions it needs, nothing extra.

### No Broker API — WATCHLIST_ONLY

TMC is a research tool. It does not execute trades.

- No broker API credentials are stored anywhere in the system.
- None of the **502+ Python scripts** have trade-execution capability.
- The system cannot place, modify, or cancel orders.
- This is an architectural constraint, not a config option — there is no "trading mode" to enable.

### No User Data Collection

- The system collects market data from 12+ public sources. It does not collect, store, or transmit any user data other than the operator's.
- No telemetry, no analytics, no tracking.
- No cloud account or third-party SaaS data-storage dependency.

### Local-Only Storage

- All data files, configuration, and credentials are stored locally on a single Mac mini.
- No cloud storage (AWS S3, Google Cloud, Azure).
- No database exposed to the network.

### Proxy Boundary

- All outbound traffic flows through a single proxy (`127.0.0.1:10808`).
- Collection scripts make no direct internet connections.
- The proxy provides a single network inspection and debugging chokepoint.

---

## Security Practices

### Three-Engine Cross-Audit

- All scripts scanned by Hermes+Codex cross-audit.
- **502+/502+ scripts pass `py_compile`.**
- Two joint Hermes+Codex audit rounds found and fixed **14 bugs total** — including a critical `HERMES_HOME` undefined-variable bug that disabled Engine C memory. See [CHANGELOG.md](CHANGELOG.md) for the full list.
- A joint Hermes+Codex **Monday readiness audit** covering 7 operational risk points passed 7/7 (PASS or FIXED) ahead of the v1.8 seal.

### Credential Isolation

- API keys and tokens live in environment variables and local config files.
- Credentials are never committed to version control.
- The GitHub repository contains no API keys, tokens, account numbers, or personal financial data.

### Frozen Modules

Four critical modules are frozen and cannot be modified without explicit operator approval:

- `send_reports.py` — push delivery infrastructure (1360 lines)
- `runtime_guard` — system health monitoring
- `scheduler` — cron engine
- `stocks.yaml` schema — data schema

### Budget Watchdog

A monthly API spend cap of **$55 USD (¥400)** is enforced continuously, with checks at 23:00 BJT, pausing non-essential API calls near the limit to prevent runaway cost from bugs or misconfiguration. Actual spend runs around ~$7/mo (13.5% of the cap). The tracker aggregates real costs from `codex_usage.jsonl` and `quality_scores.csv` — see [CHANGELOG.md](CHANGELOG.md) for the v1.6.1 fix that made this accurate.

### 4-Level Data Fallback Chain

Every data field goes through direct API → proxy route → Python library → local cache before being marked missing. This reduces the incentive to bypass the proxy boundary or hit undocumented endpoints under pressure to "just get the data." Full detail in [ARCHITECTURE.md](ARCHITECTURE.md#7-data-sources--fallback-chain).

---

## Reporting a Vulnerability

If you believe you have found a security vulnerability in TradingMapClaw:

1. **Do not open a public GitHub Issue.** Security issues should not be disclosed publicly before a fix.
2. **Report privately via [GitHub Security Advisory](https://github.com/mickeyweijiajun-web/TradingMapClaw/security/advisories/new).**
3. Please include: a description, reproduction steps (if applicable), potential impact, and a suggested fix (optional).

### Response Time

The maintainer (Mickey Wei) has a physical disability (right-arm brachial plexus avulsion, permanent ostomy) that limits mobility and typing speed. Acknowledgement will come as fast as possible, but response times may be slower than typical open-source projects. This is a solo-maintained system — there is no security team.

### Scope

**In scope:** vulnerabilities in Python scripts that could cause data leakage, credential exposure, or system compromise; push-pipeline issues (Telegram/Feishu) that could misroute reports; quality-gate bugs that let malformed data reach reports undetected.

**Out of scope:** inability to execute trades (by design); yfinance rate-limiting or Yahoo Finance data accuracy (third-party); LLM output quality (research limitation); lack of real-time Level 2 data (architectural constraint).

---

*Security policy v1.8 | 2026-07-04. A Chinese version is available in [SECURITY_CN.md](SECURITY_CN.md).*
