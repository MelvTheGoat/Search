---
job_id: 8370
company: Scarlet
title: Machine Learning Engineer
link: https://www.arbeitnow.co.uk/jobs/companies/scarlet/machine-learning-engineer-london-299291
date: 2026-10-04
---

## Cover letter

Scarlet's Applied Machine Learning team builds agents that search thousands of pages of technical evidence for medical device certification, and every answer has to show exactly where it came from. Source attribution is how I built my retrieval assistant.

It answers regulatory questions over official circulars, combining BM25 and dense retrieval through reciprocal rank fusion, and reached 0.96 recall@5 and 0.842 MRR on a 50-question labelled golden set. Section-aware chunking keeps every citation attributable to exactly one clause, and a check after generation strips any citation the model gave but never retrieved. When the evidence is not there, it refuses rather than guesses.

You want people who are suspicious of benchmarks that do not match reality. I evaluated retrieval and generation separately, and when the offline stub judge gave a 0.40 refusal-correctness result, I traced it to a limit in the judge itself rather than reporting it as system behaviour.

I deployed the assistant on GCP Cloud Run with Docker within about 225MB of peak memory, with request caps to bound API cost. My experience shipping software comes from projects rather than years in industry. I hold a B.Sc. in Statistics, can start immediately and am willing to relocate to London. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

Scarlet certifies AI-enabled medical devices, so its own AI has to show its evidence and leave the final judgement to assessors. Building retrieval that can be checked against its sources is the work I do best.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_Scarlet_Machine_Learning_Engineer.pdf (and .docx)
