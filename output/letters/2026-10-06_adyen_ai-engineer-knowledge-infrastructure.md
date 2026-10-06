---
job_id: 8735
company: Adyen
title: AI Engineer, Knowledge Infrastructure
link: https://job-boards.greenhouse.io/adyen/jobs/8255817
date: 2026-10-06
---

## Cover letter

Adyen's Documentation Tooling team is turning static documentation into structured, queryable knowledge for developers and AI agents, with retrieval interfaces built for agents and automated checks for documentation drift. I have built retrieval over structured documents and tools for AI assistants.

My compliance assistant answers questions over regulatory circulars, combining BM25 and dense retrieval through reciprocal rank fusion, and reached 0.96 recall@5 and 0.842 MRR on a 50-question labelled golden set. Section-aware chunking never merges across a document's own structure, so every citation points to exactly one clause, and I tested that against a structure-blind baseline rather than assuming it was better.

My web3-risk-mcp server gives AI assistants six read-only tools over several external sources, with caching, rate limits and retries. My ledger API requires an Idempotency-Key on every write, so a replayed request returns the original response and creates nothing, which matters for pipelines that update knowledge safely.

I have deployed on AWS ECS Fargate and GCP Cloud Run. I have not used Kubernetes or a graph database. I hold a B.Sc. in Statistics, can start immediately and am willing to relocate to Amsterdam. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Adyen's documentation is how developers and now AI agents learn to integrate payments, so accurate and fresh knowledge directly affects customers. Building retrieval that people and agents can rely on is the work I most want to do.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_Adyen_AI_Engineer_Knowledge_Infrastructure.pdf (and .docx)
