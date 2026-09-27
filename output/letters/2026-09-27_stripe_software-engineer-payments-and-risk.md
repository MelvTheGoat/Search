---
job_id: 1860
company: Stripe
title: Software Engineer, Payments and Risk
link: https://stripe.com/jobs/search?gh_jid=6717520
date: 2026-09-27
---

## Cover letter

Stripe's Payments and Risk teams build Radar and Authorization Boost, and help Stripe tell real businesses from bad actors. Correct money movement and catching fraud are the two areas my projects are built around.

My double-entry ledger API enforces correctness in the database: integer minor units, every transaction summing to zero through a deferred constraint trigger, and an append-only ledger where corrections are reversals. Every write needs an Idempotency-Key, so a replayed request returns the original response and creates nothing, and events leave through a transactional outbox. I benchmarked pessimistic against optimistic locking on a hot account, 144.8 against 41.3 tps, and wrote 138 tests against real PostgreSQL and Redis.

On risk, my fraud detection system models transaction sequences, measures precision at fixed review capacity by attack type, and serves decisions at 5.1 ms p99 with per-decision audit logs. Reckon, my reconciliation service, matches processor webhooks with bank settlement files to catch duplicates and payout gaps.

My work history is in teaching and audit rather than software teams, and I think the work above shows how I would approach Stripe's problems. I can start immediately and am willing to relocate to Dublin. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Stripe runs payments for millions of businesses, so a small gain in authorisation or fraud accuracy is worth a lot. The Dublin org covers payments, risk and AI-assisted investigation, the three areas I have built in.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_Stripe_Software_Engineer_Payments_and_Risk.pdf (and .docx)
