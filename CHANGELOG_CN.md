# 更新日志

> **TradingMapClaw（TMC）v1.8 | 2026-07-04**

TradingMapClaw（TMC）的所有重要变更都记录在本文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)。

---

## [v1.8] — 2026-07-04 — 活跃开发中

### 三引擎委员会正式确立

委员会结构正式确立为**三引擎架构**（Engine A / B / C），并明确权重分配——Engine A（Hermes/GLM-5.2：基本面、估值、内部人，40%）、Engine B（Codex/GPT-5.5：技术面、资金流、期权、交叉核验，35%）、Engine C（Hermes/GLM-5.2：宏观、行业、情绪、监管，25%）——并配备了针对争议判断的**委员会作战室**决胜协议（DeepSeek → GLM-5.2 → GPT-5.5），建立在现有的全部必须完成关卡之上。

### 两轮联合审计——累计修复 14 个 bug

在 v1.6 审计基础上，又进行了两轮 Hermes+Codex 联合审计，累计修复达到 **14 个 bug**，其中包括一个严重的 `HERMES_HOME` 未定义变量 bug，该 bug 一直在静默禁用 Engine C 的记忆功能。

### 规模与预算

- **502+ 个 Python 脚本**（全部通过编译），较之前的 499 个有所增长。
- **119 个定时任务**（约 110 个已启用），较之前的 115 个有所增长。
- **93+ 个 SKILL.md** 文件。
- **82 个标的**，12+ 个数据源。
- 预算：实际支出约每月 7 美元，相对于每月 55 美元硬上限（上限的 13.5%）。

### 官网与支付

上线官网与技能包；支付方式转为仅法定货币（PayPal/Wise），移除加密货币打赏箱。

---

## [v1.6.1] — 2026-07-03 — 活跃开发中

### 预算跟踪器修复

`budget_status.json` 此前每月都显示 ¥0.00，原因是大多数定时任务没有调用 `token_tracker.record_usage()`，而 Codex CLI 的成本单独记录在 `codex_usage.jsonl`（248 条记录，含真实 `cost_cny` 字段）中，却从未被输入跟踪器。`token_budget_check.py`（每晚 23:00 定时运行）被外科手术式地重写，从三个来源聚合真实成本：

1. `codex_usage.jsonl`——读取每条记录，按当月筛选，累加真实 `cost_cny` 字段。
2. `quality_scores.csv`——统计 Hermes agent 的 LLM 调用次数，用模型定价估算成本。
3. `token_tracker.budget_status()`——保留作为未来 `flush_monthly()` 调用的回退。

验证输出：`🟢 预算：¥1.84/400（0.5%）— GREEN | Codex：28 次调用 ¥1.58 | Hermes：10 次调用 ¥0.26`。仪表盘现在显示按模型和按任务的成本细分，每晚更新。

### T26 竞态条件修复

T26 数据管线和 T26 洋葱报告此前都安排在周一 21:00 运行，存在洋葱报告读取到不完整 `sc_alpha_*.json` 输出的风险。修复：数据管线提前至 **20:30**，比 21:00 的洋葱报告早 30 分钟。

### 多引擎超时修复

多引擎深度分析流程（4 个标的 × 3 次引擎调用 × 300 秒超时）可能超过调度器 2700 秒的上限。修复：`MAX_TICKERS_PER_RUN` 从 4 降至 2。

### 周一就绪审计 — 7/7 全部通过

在 v1.6.1 封版前，Hermes+Codex 联合审计覆盖 7 个运营风险点：

| # | 风险 | 结论 | 采取的行动 |
|---|------|---------|-------------|
| 1 | T26 竞态条件（数据管线 vs 洋葱报告均在周一 21:00） | FAIL → FIXED | 数据管线提前至 20:30 |
| 2 | 多引擎超时（4 标的 × 3 次调用 × 300 秒 > 2700 秒上限） | WARN → FIXED | `MAX_TICKERS_PER_RUN` 从 4 降至 2 |
| 3 | yfinance 冷缓存（约 60 次调用，首次运行需 5-10 分钟） | WARN | 可接受——后续运行通过 7 天 TTL 缓存已预热 |
| 4 | 数据新鲜度（技术面/情绪/行情数据在 21:00 前就绪） | PASS ✅ | 全部在 T26/分析运行前 1-3 小时完成采集 |
| 5 | 预算跟踪器运行且输出有效 JSON | PASS ✅ | ¥1.84/¥400，GREEN 状态 |
| 6 | `collect_market_data --check-only` API 连通性 | PASS ✅ | Finnhub 正常，CoinGecko 正常 |
| 7 | 22 个修改文件的 `py_compile` 检查 | PASS ✅ | 零错误 |

### 新增

- 官网（tradingmapclaw.com）与作者故事整合。

### 验证

- **499/499 脚本通过编译**（`py_compile`）
- 周一就绪审计：7/7 PASS/FIXED
- 预算跟踪器：确认真实成本聚合准确

---

## [v1.6] — 2026-07-03

### Codex 审计：发现并修复 5 个重构后遗留 bug

在 v1.5 全部改动完成后，Codex（GPT-5.5）执行了一次完整的工程质量审计：完整阅读全部 19 个被修改的 Python 文件（不只是改动部分）、对全部 19 个文件运行 `py_compile`（全部通过）、对关键文件运行 `importlib.import_module()`（全部导入正常）、验证跨文件依赖关系、检查 `scripts/` 与 `cron/scripts/` 副本的同步状态，并确认冻结模块未被触碰。

| # | 严重程度 | 文件 | Bug | 修复 | 验证 |
|---|----------|------|-----|-----|-------------|
| 1 | 严重 | `codex_analyst_wrapper.py` 第 766 行 | `HERMES_HOME` 未定义 → Engine C 的宏观/情绪数据从未加载（被 except 静默捕获，不崩溃但功能失效） | 改为 `SCRIPTS_ROOT`（第 39 行已定义） | ✅ `_load_engine_c_memory('AVGO')` 现在能返回真实数据 |
| 2 | 高 | `scripts/collect_market_data.py` 第 29 行 | `scripts/` 副本缺少 `from pathlib import Path`（`cron/scripts/` 副本已修复） | 添加导入 | ✅ `py_compile` 通过 |
| 3 | 中 | `codex_options.py` 第 116、121、135-139 行 | 输出标题（"策略分析"）和审查 prompt 中残留中文字符串 | 转换为英文 | ✅ 输出行中 0 处非注释中文 |
| 4 | 低 | `scripts/codex_position_risk_wrapper.py` | `scripts/` 副本仍有 39 行中文（`cron/scripts/` 副本已是英文） | 同步：`cp cron/scripts/ → scripts/` | ✅ MD5 匹配 |
| 5 | 低 | `codex_bullbear.py` 第 161、170 行 | 中文调试打印语句（"采集数据..."、"分析..."） | 转换为英文 | ✅ 0 处中文打印 |

### 多引擎深度分析

引入 Engine C → Engine A → Engine B → 综合 的四步流程，强制交叉核验、联合撰写和全部必须完成的关卡机制（见 [ARCHITECTURE_CN.md](ARCHITECTURE_CN.md#3-三引擎多模型分析流程)）。深度分析模板由中文重写为英文（8 段式）。新增成本分析（约 $7/月实际支出 vs $55/月上限）。新增竞品对比矩阵。

### 冻结模块验证（修复后）

| 模块 | 状态 |
|--------|--------|
| `send_reports.py` | ✅ 未修改 |
| `bilingual_send.py` | ✅ 未修改 |
| `runtime_guard` | ✅ 未修改 |
| `scheduler` | ✅ 未修改 |
| `stocks.yaml` schema | ✅ 未修改 |

---

## [v1.5] — 2026-07-03

### T26 管线修复（9 项）

| # | 严重程度 | 问题 | 修复 |
|---|----------|-------|-----|
| 1 | P0 | `collect_market_data.py` 缺少 `from pathlib import Path` → 全部 T1/T2/T3 报告使用过期价格 | 添加导入（两个副本） |
| 2 | P0 | T26 评分图 `depth==0` 过滤器排除了第 3 层候选 | 移除该过滤器 |
| 3 | P0 | `get_hot_sectors()` 读取了错误的数据结构 → 8 个行业中只扫描了 3 个 | 重写为读取 `apewisdom_ranking` |
| 4 | P0 | `ALL_CANDIDATES` 一直为空 → 评分引擎漏掉标的 | 从 `STATIC_SUPPLY_CHAIN` 填充 |
| 5 | P0 | T26 的 `collect_tech()` 读取了错误的 JSON 路径 → RSI/MACD 始终为空 | 添加 `.get("indicators", {})` |
| 6 | P0 | T26 `max_cap_usd=10B` 过滤掉了 ASML/AMAT/LRCX/KLAC/MU | 改为 500B |
| 7 | P0 | 深度分析的中文校验标题 → 遇到英文时总是失败 | 改为英文标题 |
| 8 | P0 | `_write_engine_c_memory()` 使用中文正则 → 静默失败 | 改为英文正则 |
| 9 | P1 | T16 输出为 `.json` 但内容是 markdown | 改为 `.md`（两个副本） |

### 功能增强（15 项）

供应链图谱从 43 家扩展至 49 家供应商；T26 现在扫描全部 8 个行业（此前只扫前 3 个），消除了 62.5% 的盲区；爬取深度从 2 增加到 3；T11 alpha_score 阈值从 0.3 降到 0.15；T11 的 yfinance 数据补充扩展到全部标的（此前上限 20 个）；新增市值缓存（7 天 TTL）；alpha 评分维度从 5 个扩展到 8 个；T26 报告改为读取结构化的 `sc_alpha` 分数而非编造；T26 的 prompt 转为通俗语言；T11 定时任务减少为每日一次；`codex_analyst_wrapper` 引入多引擎流程（单次调用 → 四步流程，全部必须完成的关卡）；新增交叉核验逻辑（Engine B 核验 A，通过则置信度 +0.1）；6 个 no_agent 脚本由中文转换为英文。

### Prompt 精简（5 项）

`codex_analyst_wrapper`、`codex_position_analyst`、`codex_bullbear`、`codex_council` 等脚本的报告生成 prompt 全面收紧——更短的长度目标、通俗语言、去掉铺垫、修复解析器优先级。

---

## [v1.1.4] — 2026-07-01 — 已被取代

### 数据采集管线修复

数据采集入口点的一处 `NameError` 悄悄让全部 T1/T2/T3 报告降级为过期缓存。已根因定位、修复并交叉审计。**此时 468/468 脚本通过编译。Hermes+Codex 交叉审计通过。v1.1 → v1.1.4 共计 32 处修复。**

### 修复
- **P0：** `collect_market_data.py` 第 1004 行使用了 `Path(__file__)`，但文件头缺少 `from pathlib import Path` → `NameError` 崩溃。这是全部 T1/T2/T3 报告的数据采集入口点——崩溃后所有报告都退回到过期缓存（数据新鲜度超出阈值 43-54 倍；价格数据滞后 25-27 小时）。修复：添加导入。
- **P0：** `collect_social_sentiment_v2.py` 存在同样缺失的导入 → 情绪采集崩溃。修复：添加导入。
- **P2：** `t1r3_wrapper.py`——DeepSeek V4 Pro 生成了 `||` 双竖线表格前缀。修复：正则后处理 `_fix_deepseek_tables()`。
- **P2：** `t1r2_wrapper.py`——防御性地添加同样的表格修复（Codex 交叉审计建议）。
- **P1：** `generate_monday_report.py` 周一校验错误地将 R2/R3 标记为缺失。确认现有 `should_run_on_date()` 逻辑正确；误报来自旧版本。无需代码改动。

### 验证
- 468/468 脚本通过编译（`py_compile`）
- `Path()` 导入全扫描：118 个脚本全部通过
- Hermes+Codex 交叉审计：通过
- Finnhub / Yahoo Finance / CoinGecko 连通性：HTTP 200
- 定时调度器：运行正常；推送链路（Telegram + 飞书）已验证

---

## [v1.1.3] — 2026-06-30 — 已被取代

### 双重 Codex 审计

针对 v1.1.2 运行了第二次独立 Codex 审计。发现一项，经核实为误报。+1 处修复。此时累计 27 处修复。

### 修复
- **P2：** 双重 Codex 审计标记了 SKILL.md 体积告警 + 上下文残留 + t1r1 未空跑。核实：磁盘上 SKILL.md 99K ✓，无新增上下文错误 ✓，t1r1 编译通过 ✓。误报——无需代码改动。

### 被取代
被 v1.1.4 取代，因为发现了数据采集管线的 `NameError`。

---

## [v1.1.2] — 2026-06-30 — 已被取代

### 最终封版

在 v1.1.1 之后对托管缓存和网关模块重载进行了清理。+2 处修复。

### 修复
- **P2：** 托管方 `.pyc` 缓存未清理——删除全部 `__pycache__`。
- **P2：** 网关内存中保留了旧插件模块——禁用/启用触发重载。

### 被取代
被 v1.1.3（双重 Codex 审计）取代。

---

## [v1.1.1] — 2026-06-30 — 已被取代

### Codex 审查后修复

系统在 2026-06-29 于 v1.1 封版。随后的 Codex 代码审查发现了 4 个额外问题。本次全部修复。**此时 425/425 脚本通过编译（后随上游文件重新生成，先增长到 468，再到 499）。**

### 修复
- **P0：** 批量 sys.path 补丁破坏了 `cron/scripts/` 中的 11 个脚本和 `scripts/` 中的 8 个脚本，出现 IndentationError——`_CRON_ROOT` 代码块被插入到 `try:` 块内的第 0 列。修复：将 `_CRON_ROOT` 移到模块顶层，把 `from lib.*` 导入重新缩进回 `try:` 块内。全部 425 个脚本现在均通过编译。
- **P0：** T1 R4 C 组部分标的的 analyst_net 数据缺失——LLM 未能正确读取全部标的的 `analyst.yaml`。修复：将 `analyst_net`/`buy`/`hold`/`sell` 从 `analyst.yaml` 直接合并进 `stocks.yaml`。更新 `collect_market_data.py` 使其在每次采集时自动合并。
- **P1：** 仓位风险封装器中的 `mock_prices()` 引用了未定义变量。修复：替换为明确的模拟价格字典。`--mock-risks` 空跑模式现在可用。
- **P2：** `codex_analyst` 配置文件的 SKILL.md 超过 100K 字符限制。修复：将部分内容移至 references 子文件。

### 验证
- 425/425 脚本通过编译（`py_compile`）
- 34/34 封装脚本通过语法检查
- 定时调度器运行正常
- T3 盘前报告成功生成
- 推送链路（`send_reports.py`）：空跑测试通过
- Telegram + 飞书凭证：可读取
- Hermes-Codex 协作桥：运行中

---

## [v1.1] — 2026-06-29 — 已被取代

### 事故后修复

根因：`L13_LogCleanup` 任务缺少 `id` 字段 → `get_due_jobs()` 抛出 KeyError → 整个定时调度器崩溃 → 115 个任务停止运行 3 天（2026-06-26 至 2026-06-29）。

共应用 20 处修复：5 个 P0，8 个 P1，5 个 P2，2 个 P3。

### 修复
- **P0：** `L13_LogCleanup` 缺少 `id` 字段 → KeyError 崩溃。为 `jobs.json` 中的任务记录添加 `id` 字段。
- **P0：** `get_due_jobs()` 不安全的 `job["id"]` 访问（20 处）。改为带 `.get()` 容错的 `_normalize_job_record()`。
- **P0：** `audit_utils.py` 导入 `lib.universe` 失败——sys.path 未设置。插入 `_CRON_ROOT` sys.path 保护。
- **P0：** `t3_wrapper.py` 调用了一个不存在的函数。改为调用 `sanitize_positions()`。
- **P0：** 18 个封装脚本在 exec() 上下文中使用了未定义的 `__file__`。批量修补全部 18 个封装器。
- **P1：** `no_agent` 脚本执行器丢弃了 `command` 字段参数。为调度器添加 `_parse_command_args()`。
- **P1：** 封装器错误占位符被当作"报告"推送到 Telegram/飞书。添加黑名单+抑制过滤器。
- **P1：** 事件日历催化剂前瞻期太短（14 天）。延长至 30 天。
- **P1：** `collect_news.py` 缺少 `import sys` → NameError。添加导入。
- **P1：** 部分标的 analyst_net 数据过期/缺失。手动运行 yfinance 分析师数据采集器。
- **P1：** 仓位风险报告的权重/集中度数据缺失。添加 `_merge_position_shares()`。
- **P1：** T1/T2 新闻情绪偶尔缺失。LLM 现在从标题文本推断情绪。
- **P2：** 托管插件钩子签名不匹配。移除 4 个回调中的未使用参数。
- **P2：** 3 个 SKILL.md 文件超过 100,000 字符限制。将内容移至 references 子文件。
- **P2：** 未安装 `pandas_ta_classic`。已安装。
- **P2：** 79 个脚本在没有 sys.path 修复的情况下导入 `from lib.*`。批量修补 158 个脚本。
- **P2：** `codex_position_risk_wrapper.py` 出现 ModuleNotFoundError。应用 sys.path 修复。
- **P3：** `codex_screening_engine` 缺少上游文件。根因：调度器中断 3 天。
- **P3：** `panel_data_writer.py` 被报告缺失。误报——文件实际存在。

### 被取代
被 v1.1.1 取代，因为 Codex 代码审查发现 19 个脚本存在批量补丁缩进 bug。

---

## [v1.0] — 2026-06-29 — 已被取代

### 初始封版

完成全系统审计。7 个维度，232 个脚本，115 个定时任务，65k 行代码。

### 新增
- 采用 Chuanmu 6 维度评分（0-12 分制）的 T11 双轨 alpha 雷达
- T26 供应链卡位评分（AMAT/LRCX/KLAC）
- `backtrader` 本地回测引擎
- 工程宪法（10 条规则，源自 Karpathy）
- 完整数据采集管线：12+ 数据源，226 个采集脚本
- 13 种报告类型：T1/T2/T3/T11/T15/T16/T17/T18/T19/T25/T26/R1-R3/可视化
- 双引擎 AI 委员会：Hermes GLM-5.2（基本面）+ Codex GPT-5.5（技术面）
- 模型回退链：GLM-5.2 → GPT-5.5 → DeepSeek V4 Pro → Qwen3 14B（本地）
- Telegram + 飞书交付：30+ 个封装脚本
- 预算看门狗：$55/月硬性上限
- 覆盖范围：82 个标的，分 5 组

### 被取代
因严重的定时调度器事故（`L13_LogCleanup` 缺少 `id`）被 v1.1 取代。

---

## 版本历史摘要

| 版本 | 日期 | 状态 | 关键变更 |
|---------|------|--------|-------------|
| v1.0 | 2026-06-29 | 已被取代 | 初始封版。全系统审计。 |
| v1.1 | 2026-06-29 | 已被取代 | 事故后修复。20 处修复（5P0/8P1/5P2/2P3）。 |
| v1.1.1 | 2026-06-30 | 已被取代 | Codex 审查后修复。4 处修复（2P0/1P1/1P2）。 |
| v1.1.2 | 2026-06-30 | 已被取代 | 最终封版。+2 处修复（托管 pyc + 网关重载）。 |
| v1.1.3 | 2026-06-30 | 已被取代 | 双重 Codex 审计通过。+1 处修复（误报核实）。累计 27 处。 |
| v1.1.4 | 2026-07-01 | 已被取代 | 数据管线修复。+5 处修复。468/468 通过编译。Hermes+Codex 交叉审计通过。 |
| v12.1 | 2026-07-01 | 已被取代 | Hermes+Codex 联合审计：修复 16 处运行时导入 P0 问题。 |
| v12.2 | 2026-07-01 | 已被取代 | BullBear 缓存回退 + Sympathy Play 结构化新闻。 |
| v13 | 2026-07-02 | 已被取代 | 双语报告交付：30 条 prompt 转英文，DeepSeek 翻译，33 个脚本切换。 |
| v1.5 | 2026-07-03 | 已被取代 | T26 管线修复（9 个 bug），T11 扩展，8 维度评分，6 个脚本中文转英文。 |
| v1.6 | 2026-07-03 | 已被取代 | Codex 审计：发现并修复 5 个重构后 bug。多引擎深度分析（四步流程、交叉核验、联合撰写、全部必须完成关卡）。成本分析（约 $7/月实际支出）。竞品对比矩阵。 |
| v1.6.1 | 2026-07-03 | 已被取代 | 预算跟踪器修复（读取真实 Codex CLI 日志 + quality_scores.csv）。T26 竞态条件修复（数据管线 21:00→20:30）。多引擎超时修复（MAX_TICKERS 4→2）。周一就绪审计：7/7 通过。新增官网 + 作者故事。 |
| **v1.8** | **2026-07-04** | **活跃开发中** | **三引擎委员会正式确立（A 40%/B 35%/C 25%），配备委员会作战室决胜机制。又进行两轮联合审计——累计修复 14 个 bug。502+ 个脚本，119 个定时任务（约 110 个已启用），93+ 个 SKILL.md，82 个标的。预算约 $7/月 vs $55/月上限。上线官网 + 技能包 + 仅法定货币支付；移除加密货币打赏箱。** |

v1.0 → v1.8 累计修复：**74+ 项**，历经十个修复/增强周期。

---

*更新日志 v1.8 | 2026-07-04。英文版本见 [CHANGELOG.md](CHANGELOG.md)。*
