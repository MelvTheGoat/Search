---
job_id: 10152
company: Stripe
title: Machine Learning Engineer, Radar
link: https://stripe.com/jobs/search?gh_jid=8243617
date: 2026-10-08
---

## Cover letter

Stripe's Radar ML team owns 10 real-time deep learning models that protect the payment network from fraud, and is building new products against token theft, free trial abuse and scripted attacks. Real-time deep learning for fraud is the project I am proudest of.

I built three sequence architectures over customer transaction histories, a GRU, a Temporal Convolutional Network and a causally-masked Transformer encoder, with learned embeddings for about 2.9k merchants, MCC and device type. I benchmarked them against a strong LightGBM baseline across 3 seeds, reporting PR-AUC and precision at fixed review capacity, with a breakdown by card testing, account takeover and merchant compromise. Under an explicit cost model, the sequence models cut expected cost per transaction by 27%.

I handled extreme class imbalance, showed that focal loss hurt calibration while weighted sampling hurt ranking, and corrected calibration from an ECE of 0.0063 to 0.0005. For serving, I exported to ONNX Runtime, 2.9× faster than eager PyTorch, and reached 5.1 ms p99 against a 50 ms budget, with per-decision audit logs.

I have not used Spark. I hold a B.Sc. in Statistics, can start immediately and am willing to relocate to Seattle. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Radar's models protect millions of businesses at once, so each improvement shows up directly in money saved. Fraud detection with sequence models is the work I most want to do.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_Stripe_Machine_Learning_Engineer_Radar.pdf (and .docx)
