---
job_id: 10151
company: Stripe
title: Backend Engineer, Payments and Risk
link: https://stripe.com/jobs/search?gh_jid=8260985
date: 2026-10-08
---

## Cover letter

Stripe's Payments and Risk organisation wants backend engineers to build APIs and systems that reliably handle billions of money movement requests, including its balance management platform. Correct money movement under pressure is what my ledger project is about.

I built a double-entry ledger and payments API where correctness is enforced in the database: money as integer minor units, every transaction summing to zero through a deferred constraint trigger, and an append-only ledger where corrections are reversals. Every mutating endpoint requires an Idempotency-Key, so a replayed request returns the original response and creates nothing, and events go out through a transactional outbox.

I measured it under load. On a hot single account, pessimistic locking reached 144.8 tps against 41.3 tps for optimistic, which shed 46% of writes as conflicts, and removing the hot account cut transfer p99 from 1800 ms to 390 ms. It has 138 tests against real PostgreSQL and Redis, including one where exactly half of N simultaneous transfers succeed and no balance goes negative.

My experience comes from projects rather than industry years. I have not used Kubernetes. I hold a B.Sc. in Statistics, can start immediately and am willing to relocate to Toronto. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Stripe moves money for millions of businesses, where one double charge or lost payout breaks trust. Building systems where correctness is guaranteed, not hoped for, is the backend work I enjoy most.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_Stripe_Backend_Engineer_Payments_and_Risk.pdf (and .docx)
