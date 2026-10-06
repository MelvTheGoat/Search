---
job_id: 8719
company: DRW
title: Quantitative Researcher, Prediction Markets
link: https://job-boards.greenhouse.io/drweng/jobs/8256366
date: 2026-10-06
---

## Cover letter

DRW's Prediction Markets team builds systematic strategies across prediction markets, and wants a researcher who tests and validates results rigorously through backtesting. Pricing an uncertain event well is the core of my forecasting work.

My Premier League predictor forecasts outcomes and scorelines each gameweek and retrains itself after every gameweek, keeping a public record of every past prediction. It blends a LightGBM classifier over a 204-column feature table with a multinomial logistic regression, trained on log loss so draws keep realistic probability. Backtested gameweek by gameweek over 1,050 matches, it reached 52.1% outcome accuracy against 43.2% for always picking the home side, and log loss 0.9948 against 1.0061 for an Elo-only baseline, with well calibrated probabilities.

I care about calibration because a price is a probability. In my fraud work, I reduced expected calibration error from 0.0063 to 0.0005 with temperature scaling and isotonic regression. My demand forecasting platform uses rolling-origin backtesting across 6 expanding-window folds, with automated leakage tests that fail the build if any feature reads past the forecast origin.

I have not traded professionally. I hold a B.Sc. in Statistics, can start immediately and am willing to relocate to New York. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Prediction markets reward whoever prices uncertain events most accurately, which makes calibration and honest backtesting the whole game. That is the kind of problem I enjoy most.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_DRW_Quantitative_Researcher_Prediction_Marke.pdf (and .docx)
