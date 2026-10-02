---
job_id: 7644
company: GitLab
title: Backend Engineer (Python), AI Engineering, Agent Foundations
link: https://job-boards.greenhouse.io/gitlab/jobs/8704363002
date: 2026-10-02
---

## Cover letter

GitLab's Agent Foundations team builds the platform that lets AI agents work across software delivery, with Python services in the AI Gateway, well-tested APIs and evaluations of agent behaviour. My recent work covers the same three pieces: Python backends, tools for AI agents and evaluation.

I built web3-risk-mcp, an MCP server that gives AI assistants such as Claude Desktop and Cursor six read-only tools. It has caching, per-source rate limits and retries with exponential backoff, so one failing source never breaks an investigation, and I evaluated it with a record and replay harness on 34 hand-checked addresses.

On the backend side, my double-entry ledger API in FastAPI, PostgreSQL and Redis requires an Idempotency-Key on every mutating endpoint and publishes events through a transactional outbox. Load tests found throughput saturating at about 250 to 260 req/s, and removing the hot account cut transfer p99 from 1800 ms to 390 ms. It has 138 tests against real PostgreSQL and real Redis.

I have not used LangGraph in production, but I have built agent tools and their evaluations in Python. I work in UTC+1, can start immediately and would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

GitLab is building agents that work across the whole software lifecycle, and this team owns the platform they run on. Building reliable tools and tests for AI agents is the work I most want to do.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_GitLab_Backend_Engineer_Python_AI_Engineering_A.pdf (and .docx)
