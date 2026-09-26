# Oluwatobi Melvyn Mayungbo

mlvyn.t@gmail.com | LinkedIn: [linkedin.com/in/oluwatobi-mayungbo-3a567026b](https://linkedin.com/in/oluwatobi-mayungbo-3a567026b) | GitHub: [github.com/MelvTheGoat](https://github.com/MelvTheGoat) | Lagos, Nigeria

I am a Machine Learning & AI Engineer with a Statistics background, specializing in probabilistic ML and production system design. Experience spans classical ML and deep learning — forecasting, credit risk, and sequence-based fraud pipelines through to retrieval-augmented generation and financial reconciliation systems — with consistent depth in temporally honest validation, calibrated decisioning, evaluation design, containerized serving, and operational reliability.

## Education

**University of Ibadan**, January 2021 – March 2025
B.Sc. in Statistics — Oyo, Nigeria

**SQI College of ICT**, July 2025 – Present
Professional Diploma in Artificial Intelligence — Ibadan, Nigeria

## Technical Projects

### Reckon — Payment Reconciliation & Review System

[GitHub](https://github.com/MelvTheGoat/Stack) | [Live App](https://stack-production-d2a4.up.railway.app/review)

**Tech Stack:** Python, PyTorch, DuckDB, FastAPI, React, Docker, Railway, PostgreSQL

- Built and deployed a payment reconciliation system processing multi-source transaction feeds to detect uncollected revenue, duplicate settlements, and payout discrepancies, combining deterministic matching rules with ML-assisted discrepancy resolution.
- Engineered a multi-stage reconciliation pipeline using DuckDB and FastAPI, incorporating temporal join logic and tolerance thresholds to handle asynchronous processor webhooks and bank settlement files.
- Designed an interactive human-in-the-loop review interface using React, presenting match confidence scores, audit trails, and suggested resolution actions to streamline exception handling.
- Containerized and deployed the full service on Railway, implementing structured log collection, automated integration testing, and persistent transaction state tracking.

### Sequence-Based Transaction Fraud Detection System

[GitHub](https://github.com/MelvTheGoat/Fraud-Detection-With-Sequence-Models)

**Tech Stack:** Python, PyTorch, LightGBM, ONNX Runtime, FastAPI, Docker, SHAP

- Built and compared three deep sequence architectures (GRU, Temporal Convolutional Network, and a causally-masked Transformer encoder) over customer transaction histories, using learned embeddings for high-cardinality merchant (~2.9k vocabulary), MCC, and device-type categoricals; all models kept under 115k parameters and CPU-trainable in under 6 minutes.
- Benchmarked all architectures against a strong LightGBM baseline on engineered velocity and deviation features, reporting PR-AUC and precision at fixed review capacity (top 0.1%, 0.5%, 1%) across 3 seeds with a per-attack-type breakdown covering card testing, account takeover, and merchant compromise; sequence models cut expected cost per transaction 27% under an explicit cost model.
- Addressed extreme class imbalance via focal loss and weighted sampling, isolating their distinct failure modes: focal loss degraded probability calibration (ECE 0.0063) while weighted sampling instead cost ranking quality (−0.042 PR-AUC). Corrected calibration with temperature scaling and isotonic regression, reducing ECE to 0.0005.
- Deployed real-time scoring by exporting to ONNX Runtime (2.9× faster than eager PyTorch at batch size 1) and serving via FastAPI, achieving 5.1 ms p99 end-to-end latency against a 50 ms budget, with append-only per-decision audit logging and attention-based attribution of the prior transactions driving each flag

### Nigerian Fintech Compliance RAG Assistant

[GitHub](https://github.com/MelvTheGoat/Nigerian-Fintech-Compliance-RAG) | [Live App](https://nigerian-fintech-regulation-assistant-474115007874.europe-west1.run.app/)

**Tech Stack:** Python, Streamlit, BM25, ONNX Runtime, Reciprocal Rank Fusion, FastAPI, Docker, GCP Cloud Run

- Built and deployed a regulatory question-answering system over Nigerian CBN circulars and the NDPA, combining sparse (BM25) and dense (ONNX-served MiniLM) retrieval fused via reciprocal rank fusion, achieving 0.96 recall@5 and 0.842 MRR against a 50-question labelled golden set with zero retrieval misses in the top 10.
- Engineered section-aware chunking that never merges across a document’s own structural boundaries, keeping every citation attributable to exactly one clause, and validated the approach against a structure-blind fixed-window baseline rather than asserting it was better.
- Designed generation to fail safely under uncertainty: a sentinel-token refusal mechanism enforced across the prompt, output guardrail, and evaluation harness, plus post-generation citation verification that strips any marker the model cited but never actually retrieved.
- Ran retrieval and generation evaluation as fully separate metrics to localize failure by component; diagnosed a 0.40 refusal-correctness result to a lexical-overlap limitation in the offline stub judge specifically, rather than reporting it as deployed-system behavior — flagging re-validation against a live provider as the explicit next step instead of overstating readiness.
- Deployed on GCP Cloud Run via Docker within a ~225MB peak memory footprint (2GB budget), with per-session and daily request caps enforced in application code to bound API cost on a public endpoint.

### Credit Risk Decisioning & Fairness Audit System

[GitHub](https://github.com/MelvTheGoat/Credit-Risk-Decisioning) | [Live App](https://credit-risk-decisioning-702657773047.europe-west1.run.app/)

**Tech Stack:** Python, LightGBM, scikit-learn, SHAP, WOE Scorecards, FastAPI, Docker

- Developed a full credit decisioning system producing calibrated default probabilities, cost-optimal approve/decline cutoffs, adverse action reason codes, and an append-only audit trail enabling any individual decision to be reconstructed months later.
- Benchmarked gradient boosting against a traditional WOE-binned logistic scorecard, prioritizing calibration quality (Brier score, reliability diagrams, expected calibration error) over ranking metrics because expected loss requires true probabilities rather than rankings.
- Audited fairness across sex, age, education, and marital status using demographic parity and equal opportunity differences plus within-group calibration, and presented the accuracy-fairness tradeoff curve as a policy decision rather than silently optimizing it away.

### Self-Operating Demand Forecasting Platform

[GitHub](https://github.com/MelvTheGoat/nyc-taxi-demand-forecast)

**Tech Stack:** Python, Prefect, dbt-core, DuckDB, LightGBM, MLflow, Evidently, FastAPI, Docker, GitHub Actions

- Built an end-to-end hourly demand forecasting system for NYC taxi zones, producing 24-hour quantile forecasts through an orchestrated Prefect pipeline spanning ingestion, dbt/DuckDB transformations, backtesting, drift monitoring and conditional retraining.
- Modelled asymmetric business cost by penalising unmet demand at 3× idle supply and shipping the cost-optimal quantile rather than the median, cutting expected cost by 25% on an identical model and beating a seasonal-naive baseline by 32%.
- Validated with rolling-origin backtesting across 6 expanding-window folds against seasonal-naive and historical-mean baselines, reporting MASE and pinball loss, with automated leakage tests that fail the build if any feature reads past the forecast origin.

## Experience

**SQI College of ICT**, March 2026 – Present
Machine Learning Instructor — Ibadan, Nigeria

- Teaching machine learning and deep learning to student cohorts, covering statistical foundations, classical ML algorithms, neural architectures, sequence models, and production evaluation metrics.
- Instructing students on data analysis, feature engineering, and model building leveraging PyTorch, Scikit-Learn, Pandas, and NumPy.
- Guiding learners through end-to-end ML projects on real-world datasets, translating technical

**Nigerian Institute of Social and Economic Research (NISER)**, May 2024 – July 2024
Internal Auditor — Ibadan, Nigeria

- Analyzed financial and operational records to identify inconsistencies and irregularities, performing manual anomaly detection across complex transactional datasets.

## Technical Skills

- **AI & LLM Systems:** Retrieval-Augmented Generation (RAG), Hybrid Search (BM25, Dense Embeddings, RRF), LLM Evaluation & Guardrails, Prompt Engineering, Citation Verification, Hugging Face, ONNX Runtime
- **Machine Learning:** PyTorch, Scikit-learn, LightGBM, XGBoost, Deep Learning, Sequence Models (GRU, TCN, Transformers), Model Calibration (Isotonic Regression, Temperature Scaling), SHAP, Feature Engineering
- **Statistics & Causal Inference:** Statistical Inference, Experiment Design, Power Analysis, Causal Inference (S/T/X-Learners, Causal Forests), Uplift Modeling, Time-Series Backtesting, Logistic Regression, WOE Scorecards
- **Engineering & MLOps:** Python, SQL, DuckDB, FastAPI, Docker, GCP Cloud Run, Railway, Prefect, dbt-core, MLflow, Evidently, CI/CD (GitHub Actions), Git, Pytest, Streamlit, React
- **Payments & Domain:** Transaction Fraud Detection, Credit Risk Decisioning, Payment Reconciliation, Regulatory Compliance (CBN/NDPA), Demand Forecasting

## Awards & Certificates

- Google Data Analytics Professional Certificate
- Google Advanced Data Analytics Professional Certificate
- Claude Code In Action
