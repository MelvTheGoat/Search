---
job_id: 3597
company: Ramp
title: Software Engineer, Credit
link: https://jobs.ashbyhq.com/ramp/5598f7b8-4ae2-4105-a2b4-2d0f55c54c40
date: 2026-09-27
---

## Cover letter

Ramp's Credit Engineering team turns risk strategy into real-time underwriting and limit decisions, and the post asks for someone obsessed with correctness. Correctness is what I build for.

My double-entry ledger API, built with FastAPI, PostgreSQL 16 and Redis 7, enforces its money rules in the database: every transaction sums to zero, the ledger is append-only, and every write needs an idempotency key. I benchmarked pessimistic against optimistic locking on a hot account and chose pessimistic, which reached 144.8 tps against 41.3 tps while optimistic dropped 46% of writes as conflicts. It has 138 tests against real PostgreSQL and Redis.

On the credit side, I built a decisioning system with calibrated default probabilities, cost-optimal approve and decline cutoffs, adverse action reason codes and an append-only audit trail, so any single decision can be rebuilt months later.

For low-latency risk controls, my fraud scoring service runs on ONNX Runtime behind FastAPI at 5.1 ms p99 end to end against a 50 ms budget, with per-decision audit logging.

I can start immediately and am willing to relocate to New York. I would be glad to talk about the role.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Ramp sits in the flow of every payment its customers make, so a credit decision there moves real money straight away. The Credit team owns underwriting, limits and risk controls end to end, which is where software correctness and credit modelling meet. Both are what my projects are about.

## CV bullets to put first

Put the ledger API (from GitHub) first. For this application it replaces Reckon.

- Built a double-entry ledger and payments API (Python 3.12, FastAPI, PostgreSQL 16, Redis 7) where correctness is enforced in the database: integer minor units, every transaction summing to zero through a deferred constraint trigger, an append-only ledger, idempotency keys on every write, and a transactional outbox; 138 tests against real PostgreSQL and Redis.
- Benchmarked pessimistic against optimistic locking: on a hot single account pessimistic reached 144.8 tps against 41.3 tps (3.5×) while optimistic shed 46% of writes as conflicts.
- Developed a full credit decisioning system producing calibrated default probabilities, cost-optimal approve and decline cutoffs, adverse action reason codes and an append-only audit trail that lets any single decision be reconstructed months later.
- Deployed real-time fraud scoring by exporting to ONNX Runtime (2.9× faster than eager PyTorch at batch size 1) and serving via FastAPI, reaching 5.1 ms p99 end-to-end latency against a 50 ms budget, with append-only per-decision audit logging.
