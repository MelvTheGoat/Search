---
job_id: 10185
company: N26
title: Data Scientist
link: https://n26.com/en-eu/careers/positions/8260904?gh_jid=8260904
date: 2026-10-08
---

## Cover letter

N26's Data Science team builds machine learning for financial crime prevention and credit risk assessment that reaches customers, and wants someone strong on imbalanced data, validation and calibration. Those three topics are the core of my work.

My fraud detection system benchmarks deep sequence models against a strong LightGBM baseline across 3 seeds, with a breakdown by card testing, account takeover and merchant compromise. I isolated the failure modes of imbalance handling: focal loss degraded calibration to an ECE of 0.0063, while weighted sampling cost 0.042 PR-AUC. I then corrected calibration to 0.0005 and served the model through FastAPI at 5.1 ms p99.

For credit risk, I built a decisioning system with calibrated default probabilities, cost-optimal cutoffs and adverse action reason codes, comparing gradient boosting with a WOE-binned logistic scorecard. For time series, my demand forecasting platform uses rolling-origin backtesting across 6 folds and automated leakage tests, with CI on GitHub Actions.

My experience comes from projects rather than industry years, and I have not used TensorFlow. I hold a B.Sc. in Statistics, can start immediately and am willing to relocate to Berlin. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

N26 is a mobile bank, so fraud and credit decisions are made by models at the moment a customer acts. Building those models carefully and well calibrated is the work I want to do.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_N26_Data_Scientist.pdf (and .docx)
