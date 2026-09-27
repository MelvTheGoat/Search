---
job_id: 3799
company: Lendable
title: Data Scientist
link: https://jobs.ashbyhq.com/lendable/805595d4-ce39-47db-82f5-8066c8fdea89
date: 2026-09-27
---

## Cover letter

Lendable offers real rate, risk-based pricing at the point of application, and your data science team builds the credit risk models that set that price. That is the problem my strongest project was built around.

I built a credit risk decisioning system that produces calibrated default probabilities, cost-optimal approve and decline cutoffs, adverse action reason codes and an append-only audit trail. I benchmarked gradient boosting against a WOE-binned logistic scorecard and chose on calibration, using Brier score, reliability diagrams and expected calibration error, because pricing on expected loss needs true probabilities, not just a good ranking. I also audited fairness across sex, age, education and marital status.

Your team deploys and monitors its own models. I work the same way: my projects ship with FastAPI and Docker, and my demand forecasting platform tracks runs in MLflow, watches drift with Evidently and retrains when needed.

For experiments, my uplift modelling study on 64,000 customers includes a power and MDE calculator and a CUPED variance reduction demo.

I work in Python and SQL with NumPy and Pandas, and I teach machine learning at SQI College of ICT. I can start immediately and am open to relocating to London. I would like to talk about the role.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Lendable builds its own underwriting and pricing models and runs them without a separate machine learning engineering team, so a data scientist owns the path from data to decision. That matches how I have built every project. Credit models for loans and cards are also the area I have worked on most.

## CV bullets to put first

- Developed a full credit decisioning system producing calibrated default probabilities, cost-optimal approve and decline cutoffs, adverse action reason codes and an append-only audit trail that lets any single decision be reconstructed months later.
- Benchmarked gradient boosting against a traditional WOE-binned logistic scorecard, choosing on calibration quality (Brier score, reliability diagrams, expected calibration error) because expected loss needs true probabilities rather than rankings.
- Audited fairness across sex, age, education and marital status using demographic parity, equal opportunity differences and within-group calibration, and presented the accuracy and fairness tradeoff as a policy decision.
- Validated forecasts with rolling-origin backtesting across 6 expanding-window folds, reporting MASE and pinball loss, with automated leakage tests that fail the build if any feature reads past the forecast origin.
