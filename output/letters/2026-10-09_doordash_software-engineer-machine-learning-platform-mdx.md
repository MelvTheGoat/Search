---
job_id: 10371
company: DoorDash
title: Software Engineer, Machine Learning Platform, MDX
link: https://job-boards.greenhouse.io/doordashusa/jobs/8264534
date: 2026-10-09
---

## Cover letter

DoorDash's ML Platform team builds the systems that let data scientists develop, train and deploy models across search, dasher assignment and ETA prediction, with reliable training and inference at very large scale. I have built small versions of each part of that platform.

My demand forecasting platform runs as an orchestrated Prefect pipeline covering ingestion, dbt and DuckDB transformations, backtesting, drift monitoring and conditional retraining, with MLflow tracking and automated tests that fail the build if any feature leaks past the forecast origin. It ships the cost-optimal quantile rather than the median, which cut expected cost by 25% on an identical model.

For inference, I exported my fraud models to ONNX Runtime, 2.9× faster than eager PyTorch at batch size 1, and served them through FastAPI at 5.1 ms p99 against a 50 ms budget. My churn model is tracked in MLflow and deployed on AWS ECS Fargate behind a load balancer with CloudWatch logs and CI/CD.

My experience comes from projects rather than industry years, and I have not used Spark, Airflow or TensorFlow. I hold a B.Sc. in Statistics, can start immediately and am willing to relocate to San Francisco or Seattle. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

DoorDash's ML platform decides how quickly every model in the company reaches production. Building the reliable systems around models is the engineering I enjoy most.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_DoorDash_Software_Engineer_Machine_Learning_Platf.pdf (and .docx)
