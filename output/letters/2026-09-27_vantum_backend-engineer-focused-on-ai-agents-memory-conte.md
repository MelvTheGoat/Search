---
job_id: 6527
company: Vantum
title: Backend Engineer focused on AI Agents, Memory & Context
link: https://himalayas.app/companies/vantum/jobs/backend-engineer-chat-context
date: 2026-09-27
---

## Cover letter

Ask Vantum's harness decides what the model sees each turn, what it remembers and which tools it calls, and your post asks for someone who can tell a prompt problem from a retrieval or tool problem. That diagnosis is the part of LLM work I have practised most.

In my compliance assistant, I evaluate retrieval and generation separately, so a bad answer points to one component. When refusal correctness came out at 0.40, I traced it to a lexical-overlap limit in the offline judge rather than the prompt, and reported that instead of changing prompts blindly. The assistant enforces one refusal rule across the prompt, output guardrail and evaluation harness, and strips any citation the model gave but never retrieved, so it never claims something it cannot back up.

For tools, my MCP server gives AI assistants six tools with per-source rate limits and retries, and a failing source lowers confidence instead of breaking the answer. For safe persistence, my ledger API on PostgreSQL uses idempotency keys so a replayed request never creates anything twice, with 138 tests.

My backend work is in Python and FastAPI. I have not written TypeScript in production, and I would learn it quickly on your existing harness. I work in UTC+1, can start immediately and would be glad to walk you through any of these projects.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Vantum is a small team where the chat harness is the core of the product, so one engineer's work on memory and context decides how users feel. The founders value demonstrated ability and honest testing over credentials, which is how I work.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_Vantum_Backend_Engineer_focused_on_AI_Agents_Me.pdf (and .docx)
