---
job_id: 805
company: Glean
title: Machine Learning Engineer, Assistant Quality
link: https://job-boards.greenhouse.io/gleanwork/jobs/4711484005
date: 2026-09-27
---

## Cover letter

Glean wants its assistant and agents to be useful and grounded in real enterprise work, and this role builds the evaluation loops and signals that make them better. Grounding and evaluation are where I have put most of my LLM work.

My compliance assistant retrieves over regulatory documents with BM25 and dense embeddings fused by reciprocal rank fusion, reaching 0.96 recall@5 and 0.842 MRR on a 50-question labelled set with no retrieval misses in the top 10. I built section-aware chunking so each citation maps to one clause, and tested it against a fixed-window baseline. Retrieval and generation are scored separately so a quality drop points to one component, and a check strips any citation the model gave but never retrieved.

For agents, my MCP server gives AI assistants like Claude Desktop and Cursor six tools to check crypto risk. I chose a rule-based, fully explainable scorer there over a model, because a simple, reliable system was the better answer for the job.

For production, I have served models through FastAPI and Docker, including one at 5.1 ms p99 with ONNX Runtime.

I can start immediately and am willing to relocate to San Francisco. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Glean connects to the tools companies already use, so its assistant has to be right on messy, real enterprise data. The role is about shipping quality improvements, not pure research, which is the kind of AI work I enjoy.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_Glean_Machine_Learning_Engineer_Assistant_Qual.pdf (and .docx)
