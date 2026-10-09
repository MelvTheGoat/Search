---
job_id: 10575
company: AB InBev
title: AI Engineer
link: https://himalayas.app/companies/ab-inbev/jobs/ai-engineer
date: 2026-10-09
---

## Cover letter

AB InBev's Growth Group wants an AI Engineer to build agent systems with RAG, evaluation frameworks that track agent success and failure, and guardrails against prompt injection. I have built each of those in my own projects.

My compliance assistant combines BM25 and dense retrieval through reciprocal rank fusion and reached 0.96 recall@5 and 0.842 MRR on a 50-question labelled golden set. Its guardrails work at every layer: a refusal rule enforced across the prompt, the output check and the evaluation harness, and a check that strips any citation the model gave but never retrieved. I scored retrieval and generation separately, so each failure points to one component.

My web3-risk-mcp server gives AI assistants six tools and refuses any call outside a read-only allow-list, so an agent cannot take actions it should not. For inference speed, I served a fraud model through ONNX Runtime at 5.1 ms p99, 2.9× faster than eager PyTorch, and I have deployed on GCP Cloud Run and AWS ECS Fargate with CI/CD.

I have not used C++, Go, Kubernetes, Azure or LangChain. I hold a B.Sc. in Statistics, can start immediately and work in UTC+1. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

AB InBev's digital products such as BEES serve businesses across many countries, so agents there must be reliable and secure. Building agents with real evaluation and guardrails is the AI work I most want to do.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_AB_InBev_AI_Engineer.pdf (and .docx)
