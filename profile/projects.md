# More projects from GitHub

Extra projects from github.com/MelvTheGoat that are not on the CV. Every fact
and number here is taken from the project's own README or docs. Letters may use
these the same way as the CV, and may put one of them first when it fits a job
better than a CV project.

## Projects

### web3-risk-mcp: Web3 Fraud Risk MCP Server

[GitHub](https://github.com/MelvTheGoat/web3-risk-mcp)

**Tech Stack:** Python, MCP (Model Context Protocol), Etherscan V2, GoPlus, DexScreener, public RPC nodes, Docker, GitHub Actions

- Built an MCP server that gives AI assistants (Claude Desktop, Cursor) tools to check a crypto wallet, token or smart contract for risk before someone interacts with it, returning a 0 to 100 risk score with a reason for every point.
- Six read-only tools: score_risk, get_wallet_profile, check_token_risk, inspect_contract, trace_funds and list_supported_chains, covering Ethereum, Base, Arbitrum One, Polygon PoS and BNB Chain.
- Detects honeypot tokens, rug pull signs, hidden owner powers (mint, blacklist, pause), buy and sell tax, holder concentration, unlocked liquidity, and fund links to mixers, sanctioned wallets, exploiters and phishing addresses over 1 or 2 hops.
- Rule-based, fully explainable scorer: tools produce findings with stable IDs, a public rule table turns them into points, and decisive findings set a floor of 75 so trust signals can never hide them. Each score carries a confidence level based on how many sources answered.
- Resilient HTTP layer: caching, per-source rate limits, retries with exponential backoff and jitter; one failing source never breaks an investigation, and missing data lowers confidence instead of the score.
- Read-only by design: never asks for a private key, never signs or sends transactions, and the RPC client refuses any method outside a read-only allow-list.
- Evaluation set of 34 hand-checked addresses (12 risky, 22 safe) with a record and replay harness reporting ROC AUC, precision and recall, run twice to show what the signals catch without the local list of known bad addresses.

### Production-Grade Double-Entry Ledger API

[GitHub](https://github.com/MelvTheGoat/Production-Grade-Double-Entry-Ledger-API)

**Tech Stack:** Python 3.12, FastAPI, PostgreSQL 16, Redis 7, Alembic, Docker

- Built a double-entry ledger and payments API where correctness under concurrency, retries, partial failure and replay is enforced in the database: money as integer minor units, every transaction summing to zero through a deferred constraint trigger, and an append-only ledger where corrections are reversals.
- Every mutating endpoint requires an Idempotency-Key; replaying a key returns the original response and creates nothing. Events go out through a transactional outbox.
- Benchmarked pessimistic against optimistic locking: on a hot single account pessimistic reached 144.8 tps against 41.3 tps (3.5×), while optimistic shed 46% of writes as conflicts; spread across 16 accounts it was 206.5 tps against 112.6 tps.
- Load tests showed throughput saturating at about 250 to 260 req/s, and removing the hot account cut transfer p99 from 1800 ms to 390 ms (4.6×) at 50 users.
- 138 tests, all against real PostgreSQL and real Redis, including a headline concurrency test where exactly half of N simultaneous transfers succeed and no balance goes negative.

### Uplift Modelling for Campaign Targeting

[GitHub](https://github.com/MelvTheGoat/Uplift-Modelling-Decision)

**Tech Stack:** Python, scikit-learn, LightGBM, EconML, pytest, GitHub Actions

- Causal inference study answering which customers to contact under a fixed budget, on the Hillstrom randomised e-mail trial (64,000 customers), delivered as a two-page decision memo for a marketing director.
- Hand-implemented S-, T- and X-learners over a swappable scikit-learn and LightGBM base, plus an EconML causal forest, validated first on synthetic data with a known individual treatment effect.
- Showed the campaign works (1.25% conversion against 0.57%) but that a non-randomised campaign list overstates the effect by 7.5×, and that a response model mails five times as many customers the campaign harms as an uplift model does.
- Evaluated with Qini curves, AUUC, decile tables and bootstrap intervals, with no AUC; uplift targeting was worth about $1,390 against about $3,170 for raising the budget.
- Reported a negative result openly: the targeting gain failed the placebo test on the primary campaign.
- Added a power and MDE calculator and a CUPED variance-reduction demo; 135 tests on synthetic data, CI on Python 3.10 to 3.12.

### Premier League Match Predictor

[GitHub](https://github.com/MelvTheGoat/Premier-League)

**Tech Stack:** Python, LightGBM, scikit-learn, pandas, SQLite, Flask, Vercel

- Predicts Premier League outcomes and scorelines each gameweek and retrains itself after every gameweek, keeping a public record of every past prediction.
- Blend of a LightGBM classifier over a 204-column feature table and a multinomial logistic regression over core strength and form features, trained on log loss so draws keep realistic probability.
- Turned context (fixture congestion, missing players, manager changes, motivation) into measurable features built in one strictly chronological pass, with no hand-tuned adjustments.
- Backtested gameweek by gameweek over 1,050 matches: 52.1% outcome accuracy against 43.2% for always picking the home side, and log loss 0.9948 against 1.0061 for an Elo-only baseline, with well calibrated probabilities.

### FPL AI Manager

[GitHub](https://github.com/MelvTheGoat/Fantasy-Premier-League)

**Tech Stack:** Python, SQLite, FastAPI, React, Docker, Render

- Two models that play Fantasy Premier League for the 2026/27 season against the live FPL API: a Manager that carries one squad all season under real transfer, budget and chip rules, and a Best XI optimiser that rebuilds the best legal squad each gameweek.
- Built a rules engine (squad validity, formations, automatic substitutions, captaincy, selling prices, chips), an expected-points model over a multi-gameweek horizon, and a backfill from gameweek 1 with no leakage.
- Cached, rate-limited API client, scheduled jobs, live updates and one-command deployment; 574 tests, most needing no network or database.

### Telco Customer Churn, End to End

[GitHub](https://github.com/MelvTheGoat/Customer-Churn)

**Tech Stack:** Python, XGBoost, MLflow, FastAPI, Gradio, Docker, GitHub Actions, AWS ECS Fargate, Application Load Balancer, CloudWatch

- Built and deployed a churn prediction model: feature engineering and an XGBoost classifier with experiments tracked in MLflow.
- Served it through a FastAPI /predict endpoint with a Gradio UI, containerised with Docker and deployed on AWS ECS Fargate behind an Application Load Balancer, with CloudWatch logs.
- CI/CD with GitHub Actions building and pushing the image and updating the ECS service; fixed failing load balancer health checks and container import paths along the way.

### Market Anomaly Detector

[GitHub](https://github.com/MelvTheGoat/Anomaly-Detector)

**Tech Stack:** Python, SQLite, CoinGecko API

- ETL pipeline that fetches live cryptocurrency prices, stores history in SQLite, and flags price moves above a set volatility threshold.

## Extra skills shown in these projects

Model Context Protocol (MCP), Redis, Alembic, transactional outbox, idempotency, database concurrency control, EconML, Qini and AUUC, CUPED, AWS ECS Fargate, Application Load Balancer, CloudWatch, Gradio, XGBoost, Vercel, Render
