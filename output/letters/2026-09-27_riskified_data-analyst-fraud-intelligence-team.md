---
job_id: 3884
company: Riskified
title: Data Analyst, Fraud Intelligence Team
link: https://www.riskified.com/careers/job-description/?gh_jid=8813470002
date: 2026-09-27
---

## Cover letter

Your Fraud Intelligence team studies new fraud patterns across Riskified's merchants and turns them into detection logic. Finding the pattern in transaction data and proving it holds is the work I do best.

In my sequence-based fraud detection project, I modelled customer transaction histories and broke the results down by attack type: card testing, account takeover and merchant compromise. I measured precision at fixed review capacity (top 0.1%, 0.5% and 1%) across 3 seeds, because a review team can only look at so many cases. Under an explicit cost model, the sequence models cut expected cost per transaction by 27% against a strong LightGBM baseline.

I also built Reckon, a payment reconciliation system that finds duplicate settlements and payout discrepancies across processor webhooks and bank settlement files, with DuckDB at its core. Before that, as an internal auditor at NISER, I searched financial records by hand for inconsistencies and irregularities.

The role also asks for watching detection logic for drift. My demand forecasting platform runs drift monitoring with Evidently and retrains when the data moves.

Python and SQL are my main tools. I can start immediately and am happy to relocate to Lisbon. I would welcome a conversation about the role.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Riskified guarantees merchants against chargebacks, so the quality of its detection shows up directly in its own losses. The Fraud Intelligence team sits at the start of that chain, spotting new fraud methods before they spread. I want to work where research turns into decisions that carry real money.

## CV bullets to put first

- Benchmarked three deep sequence models against a strong LightGBM baseline, reporting PR-AUC and precision at fixed review capacity (top 0.1%, 0.5%, 1%) across 3 seeds, with a per-attack-type breakdown covering card testing, account takeover and merchant compromise; the sequence models cut expected cost per transaction 27% under an explicit cost model.
- Built and deployed Reckon, a payment reconciliation system over multi-source transaction feeds that detects uncollected revenue, duplicate settlements and payout discrepancies, combining deterministic matching rules with ML-assisted discrepancy resolution.
- Internal Auditor at NISER: analyzed financial and operational records to identify inconsistencies and irregularities, performing manual anomaly detection across complex transactional datasets.
- Handled extreme class imbalance with focal loss and weighted sampling and isolated their failure modes: focal loss hurt calibration (ECE 0.0063) and weighted sampling cost 0.042 PR-AUC; temperature scaling and isotonic regression brought ECE down to 0.0005.
