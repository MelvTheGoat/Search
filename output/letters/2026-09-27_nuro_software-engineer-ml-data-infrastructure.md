---
job_id: 2672
company: Nuro
title: Software Engineer, ML Data Infrastructure
link: https://nuro.ai/careersitem?gh_jid=7895818
date: 2026-09-27
---

## Cover letter

Nuro's ML-first driving system depends on the quantity and diversity of its training and evaluation data, and this team builds the infrastructure that produces it. Data systems that other people's models depend on are what I like building most.

My demand forecasting platform is a pipeline other steps rely on. Prefect orchestrates ingestion, dbt and DuckDB transformations, backtesting, drift monitoring and conditional retraining. I wrote leakage tests that fail the build if any feature reads past the forecast origin, because an evaluation is only as honest as the data behind it.

For reliability, my double-entry ledger API on PostgreSQL 16 has 138 tests against real services, including a concurrency test where exactly half of many simultaneous transfers succeed. I load tested it to find where throughput saturates and cut p99 latency 4.6× by removing a hot account.

For evaluation tooling, I built a record and replay harness for my MCP server and a React review screen with match confidence and audit trails in my reconciliation system, close to the comparison and labelling tools your team builds.

I work mainly in Python, SQL and PostgreSQL, and have not written C++ in production. I can start immediately and am willing to relocate to Mountain View. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Nuro tests its driving system on data from both road logs and simulation, so data quality decides model quality. The team owns pipelines, storage, dashboards and labelling tools for that data, which is broad, practical engineering.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_Nuro_Software_Engineer_ML_Data_Infrastructure.pdf (and .docx)
