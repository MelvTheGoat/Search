---
job_id: 9148
company: Ambient.ai
title: Software Engineer, AI Infrastructure, LVM Inference and Evaluation
link: https://jobs.ashbyhq.com/ambient.ai/e56b113b-69a1-4d38-8b9c-eb3460b9447e
date: 2026-10-09
---

## Cover letter

Ambient.ai wants an engineer to build the infrastructure for real-time inference and evaluation of its vision and language models, including low-latency serving and automated quality gates. Fast inference and careful evaluation are two things I have built.

For inference, I exported deep sequence models to ONNX Runtime, 2.9× faster than eager PyTorch at batch size 1, and served them through FastAPI at 5.1 ms p99 against a 50 ms budget, with append-only per-decision audit logging. All the models were kept under 115k parameters and trainable on a CPU in under 6 minutes, because the latency budget shaped the design.

For evaluation, my compliance assistant has a harness that scores retrieval and generation separately on a 50-question labelled golden set, so a regression points to one component. My web3-risk-mcp project uses a record and replay harness on 34 hand-checked addresses, which works like a regression test for each release. I have deployed services with Docker on GCP Cloud Run and AWS ECS Fargate with CI/CD.

I have not worked with CUDA, vLLM or computer vision models, and my experience comes from projects. I hold a B.Sc. in Statistics, can start immediately and am willing to relocate to Redwood City. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Ambient.ai's models watch real security cameras, so slow or wrong inference has real consequences. Building fast, well-tested inference for that setting is engineering I would value.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_Ambient_ai_Software_Engineer_AI_Infrastructure_LVM_.pdf (and .docx)
