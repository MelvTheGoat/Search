---
job_id: 6051
company: Balerion AI
title: Software, FDE and AI Engineers
link: https://news.ycombinator.com/item?id=49525600
date: 2026-09-27
---

## Cover letter

Your post says that in loan extraction a wrong number is much worse than a missing one, and that a good demo does not survive a lender's compliance team. I agree, and I have built my AI work around the same idea.

My compliance assistant answers questions over central bank circulars and data protection law. It is designed to fail safely: a refusal rule is enforced across the prompt, the output guardrail and the evaluation harness, and after generation it strips any citation the model gave but never retrieved. I evaluate retrieval and generation separately, reaching 0.96 recall@5 on a 50-question labelled set, so a failure points to one component.

On the lending side, I built a credit decisioning system with calibrated default probabilities, adverse action reason codes and an append-only audit trail, so any decision can be rebuilt months later.

For durable workflows, my double-entry ledger API on PostgreSQL handles retries, partial failure and replay with idempotency keys and a transactional outbox, and my MCP server's HTTP layer keeps going when one data source fails.

I work in Python and Postgres, can start immediately and would relocate to San Francisco. My GitHub is github.com/MelvTheGoat. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Balerion works on mortgage underwriting, where hundreds of pages of documents meet thousands of pages of guidelines, and most of it is still done by hand. The team puts real effort into evaluation infrastructure, which is the part of AI engineering I care about most.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_Balerion_AI_Software_FDE_and_AI_Engineers.pdf (and .docx)
