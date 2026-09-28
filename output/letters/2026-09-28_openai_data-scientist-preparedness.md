---
job_id: 253
company: OpenAI
title: Data Scientist, Preparedness
link: https://jobs.ashbyhq.com/openai/efcc3430-14c8-4022-8350-8146ffb867ab
date: 2026-09-28
---

## Cover letter

Your post describes work beyond running evals: finding why a classifier blocks too much or too little, and building monitoring that shows whether a mitigation keeps working. Error analysis and measurement are what my projects are built on.

In my fraud detection system I judged models by precision in the top 0.1%, 0.5% and 1% of scored transactions, across 3 seeds and by attack type, because a single average hides where a detector fails. I found that focal loss hurt calibration while weighted sampling hurt ranking, then brought expected calibration error down to 0.0005 with temperature scaling and isotonic regression, so thresholds mean what they say.

For AI systems, I built a retrieval assistant that refuses when the sources do not support an answer, and I scored retrieval and generation separately to find which part fails. When refusal correctness came out at 0.40, I traced it to my offline judge rather than calling it model behaviour.

I also ran a causal study showing a non-randomised list overstates an effect by 7.5×, and built a power and CUPED demo. I hold a B.Sc. in Statistics, can start immediately and am willing to relocate to San Francisco. I would be glad to talk.

Oluwatobi Melvyn Mayungbo
mlvyn.t@gmail.com

## Why this company

The Preparedness team decides whether mitigations for frontier models actually work, which is a measurement problem with high stakes. The role asks for classifier evaluation, calibration and thresholding, the parts of my work I care about most.

## Tailored CV

output/cvs/Oluwatobi_Mayungbo_CV_OpenAI_Data_Scientist_Preparedness.pdf (and .docx)
