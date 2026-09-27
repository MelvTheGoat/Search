---
job_id: 3260
company: Qube Research & Technologies
title: Production Support Engineer, LLM Platform
link: https://job-boards.greenhouse.io/quberesearchandtechnologies/jobs/8759003002
date: 2026-09-27
---

## Cover letter

QRT's LLM gateway serves engineers and business users across the firm, and this role keeps it available by working out whether a problem is on the platform or upstream. Debugging API-driven services is the part of my projects I have spent the most hours on.

For web3-risk-mcp, I built an HTTP layer that talks to several outside data providers. It caches responses, sets rate limits per source and retries with exponential backoff and jitter, and when one provider fails the investigation carries on with lower confidence instead of breaking. Deciding what should fail loudly and what should degrade quietly is most of that work.

For my ledger API on PostgreSQL 16 and Redis 7, I load tested to find throughput saturating at about 250 to 260 requests per second, and cut transfer p99 from 1800 ms to 390 ms by removing a hot account. My compliance assistant, a public LLM endpoint, has per-session and daily request caps in code to bound API cost.

I write Python and SQL, use Docker and PostgreSQL in my projects, and hold the Claude Code in Action certificate. I have not worked a formal support rotation yet. I can start immediately and am willing to relocate to Hong Kong. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

QRT runs its research and trading on data and technology, and the LLM gateway is becoming shared infrastructure for the whole firm. Keeping it reliable means working across providers, platform and users, which is practical, varied engineering.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_Qube_Research_Technologies_Production_Support_Engineer_LLM_Platform.pdf (and .docx)
