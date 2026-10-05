---
job_id: 6076
company: AiMi
title: Full Stack AI Engineer
link: https://news.ycombinator.com/item?id=49552714
date: 2026-10-05
---

## Cover letter

AiMi's agents read venue and vendor notifications and drive change management for exchanges, and the role includes building MCP-based connectors, running evals on agent accuracy, and making long-running LLM calls resilient. I have built each of those pieces.

My web3-risk-mcp project is an MCP server that gives AI assistants six read-only tools. Its HTTP layer has caching, per-source rate limits, and retries with exponential backoff and jitter, so one failing source never breaks an investigation, and missing data lowers confidence instead of the score. I measured it with a record and replay harness on 34 hand-checked addresses.

My compliance assistant has an evaluation harness that scores retrieval and generation separately, so a failure can be traced to one component, and a refusal rule enforced across the prompt, the output guardrail and the harness. On the front end, I built a React review screen for my deployed reconciliation system.

My backend work is in Python with FastAPI. I have not used Node.js or AWS Lambda, and I would learn them quickly. I hold the Claude Code In Action certificate, can start immediately and work in UTC+1. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

AiMi runs agents in live production for exchanges, where a missed notification has real cost. Making agents dependable, with connectors, evals and resilience, is the work I enjoy most.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_AiMi_Full_Stack_AI_Engineer.pdf (and .docx)
