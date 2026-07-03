# One Hand. One Bag. One System.

### The story behind TradingMapClaw and the man who built it.

> **v1.6.1 | 2026-07-03**

---

A man who lost 95% of his right arm's function before he was twenty. A man whose colon was removed and whose abdomen now carries a permanent opening. A man who worked inside Wells Fargo, Deutsche Bank, UBS, JPMorgan, and eToro — typing with one hand. A man who, in 2026, built an automated investment research system — 499 Python scripts, 115 scheduled jobs, a dual-engine architecture running a multi-model council — by himself, on a single Mac mini, in two months. His name is Mickey Wei. This is not a story about overcoming adversity. It is a story about a man who refused to accept the dimensions of the room he was given.

---

## Chapter 1: Before Twenty

The car did not stop.

A hit-and-run collision before the age of twenty left Mickey with severe brachial plexus injury — nerve damage so extensive that his right arm and hand lost approximately 95% of their function. The brachial plexus is the network of nerves that controls the entire arm. When it is torn, the arm does not hurt and then heal. It simply stops belonging to you.

The first six months were a medical gauntlet: six hospitalizations, three surgeries under general anesthesia — two brachial plexus nerve transfer operations and one mandibular reconstructive surgery, all within the first half of 2004. The legal proceedings that followed were long and grinding. He was the victim — not the one who caused the crash, not the one who fled — but the one left to rebuild. The legal system, like the medical system, does not move at the speed of a person's desperation.

Then came the relearning. Every action that an able-bodied person performs without thought — tying shoelaces, wringing a towel, opening a bottle cap, cutting fingernails, writing, typing — had to be reconstructed from scratch with his left hand. Each of these was not a milestone. It was a small grief, followed by a struggle, followed by something that resembled but was never quite the same as what had been lost.

He decided to take his life back. He studied. He sat for the gaokao — China's national college entrance examination — using only his left hand for every subject, every answer, every page. He got in.

---

## Chapter 2: The Door That Kept Closing

After graduation, he job-hunted alone. The pattern was consistent: interviews that went well until the interviewer noticed the arm. Then the conversation changed. Then the rejection came. Sometimes it was explicit. More often it was the silence that follows a polite nod.

His first formal employment came through the Disabled Persons' Federation (DPF) — a government channel that exists because the market alone does not hire people like him. He knew this was a compromise. He took it, and then looked for the next opening.

His early career was a patchwork: freelance work, part-time roles, temporary contracts. He never hid this on his résumé. The gaps were not failures. They were the shape of a life that did not fit the standard mold.

The turning point arrived in an interview for a multinational corporation's disability employment program. The interviewer was Indian. Mickey answered in fluent English and spoke about banking operations with a specificity that caught the interviewer off guard. The result was a placement that broke precedent: he was assigned to a top-tier Swiss investment bank — the first disabled employee in their Shanghai office. His colleagues were returnees from universities in the United States, Britain, and Australia. He was the one who had learned to type with one hand.

---

## Chapter 3: The Walls of Finance

He worked in back office operations — the infrastructure layer of global finance. Not the trading floor. Not the client meetings. The machinery beneath: trade lifecycle processing, settlement, reconciliation, maker-checker controls. The work that ensures that when a trade is made, the securities move, the cash moves, the books balance, and the system does not break.

His career spanned five institutions, each a force in the global financial system: Wells Fargo, Deutsche Bank, UBS, JPMorgan, and eToro. Four are the pillars that clear and settle the transactions the world's economy runs on; the fifth, eToro, is the fintech platform that put social, algorithmic trading in the hands of ordinary people. These are not small companies. The fact that he worked there is not a footnote. It is a fact that stands on its own.

He did this work with one functional hand. He did not ask for reduced standards. He did not receive them. And he absorbed something from years of maker-checker discipline that would resurface decades later, encoded directly into software: no number reaches a client, a report, or a decision without someone — or something — independently verifying it first.

---

## Chapter 4: The Second Collapse

During his banking career, he developed ulcerative colitis (UC) — a chronic autoimmune disease in which the immune system attacks the colon. This is not "a sensitive stomach." During flare-ups, the pain is extreme and the condition is debilitating. Standard treatment involves long-term use of corticosteroids and immunosuppressants — both of which carry severe side effects: bone loss, weight gain, increased infection risk, and more.

He did not want to spend his life on these drugs. The only curative option was surgery. It would not be one operation. It would be eight, spread across eight years.

The first two came in 2016. The first removed the entire colon and folded the small intestine into a pouch to replace colon function, with a temporary ileostomy on the abdominal wall. The second — the take-down — connected the pouch to the anus, restoring natural continence. The process took approximately six months. It seemed to be over.

It was not. In 2021, severe pouchitis — inflammation of the replacement pouch — forced a reversal back to an ileostomy. The stoma reopened. In 2022, the stoma prolapsed and had to be surgically relocated and rebuilt. In 2024, the now-idle ileal pouch was permanently removed. The stoma is permanent. A permanent ostomy means the abdomen has an opening that will never close. It means wearing an ostomy bag for the rest of one's life. There is no reversal. There is no adaptation period after which things go back to normal. This is normal now.

Eight surgeries total: three for the arm, five for the colon and stoma, across eight years.

---

## Chapter 5: What He Carries Now

Two conditions occupy the same body. The right arm — 95% function lost, brachial plexus injury, four nerve roots. The abdomen — a permanent stoma, a bag that must be managed every day, a body that has been opened under general anesthesia eight times.

The combination of permanent brachial plexus injury and permanent ostomy in a single person is, in public medical and employment records, extremely rare. Not because it does not happen. Because the people it happens to tend to disappear from public life.

He did not disappear.

---

## Chapter 6: The Answer

In May 2026, Mickey began building. He had no prior coding background. He used AI as his engineering partner — not as a crutch, but as a collaborator that could type at the speed of his thoughts, since his left hand alone could not keep up with what he wanted to build.

In two months, he built TradingMapClaw (TMC), now at v1.6.1:

- 115 scheduled jobs running automatically, including data collection before US market open
- 499 Python scripts — all passing compilation
- Coverage of 82 tickers across 5 groups
- 12+ data sources
- 13 report types, from intraday snapshots to supply chain chokepoint analysis
- A **Dual-Engine architecture** — Hermes Agent (orchestration, fundamentals, macro, sentiment) and Codex/GPT-5.5 (independent technicals and cross-verification) — running a **Multi-Model Council** of DeepSeek V4 Pro, GLM-5.2, and GPT-5.5 across three analysis roles, with mandatory cross-verification before any report is co-authored
- A monthly budget cap of $55 USD, with actual measured spend around $7/month
- Hermes+Codex cross-audit across all 499 scripts, plus a dedicated Codex audit that found and fixed 5 post-refactoring bugs
- Reports delivered to Telegram and Feishu — zero missed deliveries

The system ran into a catastrophic failure during its first month: a single missing `id` field in a cron job configuration crashed the entire scheduler. 115 jobs stopped for three days. He diagnosed it, fixed it, and kept fixing: patched dozens of issues across repair cycles from v1.1 through v1.6.1, brought all scripts to clean compilation, and — most recently — ran a joint Hermes+Codex Monday-readiness audit across 7 operational risk points that passed 7/7. The incident and repair log is published in full in [CHANGELOG.md](CHANGELOG.md) — not as a confession, but as evidence of competence.

One model can be confidently wrong. Two engines catch it. A council of three decides. That principle — cross-verify before you trust a number — did not come from a textbook. It came from years spent in maker-checker roles in banking, where the same rule applied to money instead of code.

TradingMapClaw is not a hobby project. It is an answer. To the job market that closed its doors. To the hospital bed that took his colon. To every standard he was measured against and found lacking because of a hand that does not work and a bag that does not come off. He did not ask anyone to lower the standard. He walked around the door and built his own building.

---

## A Note on Two Invisible Conditions

### Brachial Plexus Injury

The brachial plexus is a bundle of nerves originating from the spinal cord that controls sensation and movement in the shoulder, arm, and hand. Severe trauma — particularly motor vehicle accidents — can tear these nerves. When the tear is pre-ganglionic (before the nerve root ganglion), surgical repair is often impossible and the resulting paralysis is permanent.

Globally, a significant number of traffic accident survivors sustain permanent brachial plexus injuries each year. Rehabilitation can take years. In many cases, full function is never restored. Employment rates among individuals with severe brachial plexus injury are significantly lower than the general population — not because of cognitive limitation, but because the labor market does not accommodate what it has not been forced to imagine.

These patients are nearly invisible in employment data. They are absent from workplace diversity conversations. They are not represented in media. Their disability is physical, visible, and yet socially unseen.

### Ulcerative Colitis and Permanent Ostomy

Ulcerative colitis is a chronic inflammatory bowel disease. The immune system attacks the lining of the colon, causing inflammation, ulceration, bleeding, and pain. It is not caused by diet or stress. It is not "stomach trouble." It is an autoimmune condition with no known cure except surgical removal of the colon.

Approximately 5 million people worldwide live with inflammatory bowel disease (IBD), with ulcerative colitis comprising a major proportion. For many, medication controls the disease. For others, the disease progresses until the colon must be removed.

When the colon is removed and the stoma is made permanent, the patient lives with an ostomy — an opening on the abdomen through which waste exits into a pouch. There are an estimated several million permanent ostomy patients worldwide. They are almost never visible in public life.

The challenges of living with an ostomy extend beyond the physical: workplace discrimination, social stigma, intimacy barriers, and chronic psychological stress. Many ostomy patients hide their condition from employers and colleagues. The silence is not because the condition is shameful. It is because the world has made it feel that way.

### What We Ask

Not pity. Visibility.

If you know an employer, an investor, a journalist, or a platform that reaches people — share this story. Not because Mickey Wei needs a favor. Because the people who share his conditions — the ones who have not built a system, who do not have a voice, who are still in the room with the closed door — need to know that someone is visible.

If you are living with a brachial plexus injury, with an ostomy, with both — you are not alone. Not anymore.

---

## Closing

Mickey Wei built TradingMapClaw with one working hand and a body that has been surgically rebuilt eight times. He did not build it to prove a point. He built it because the world he was given did not have a place for him, so he made one. The system runs before US market open while he sleeps. It collects data, runs a dual-engine, multi-model analysis, and delivers reports to his phone. It does not know or care that it was built by a man with one hand and a stoma bag.

That is the point. The system works. The man who built it works. And the distance between what he was told he could be and what he actually became is the only measurement that matters.

He did not overcome anything. He refused to be overcome.

---

*Read the full technical picture in [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md). A Chinese version of this story is available in [STORY_CN.md](STORY_CN.md).*

*Story v1.6.1 | 2026-07-03.*
