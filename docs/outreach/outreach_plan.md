# Outreach plan and message templates

Owner: Oluwatobi Mayungbo, ML/AI Engineer (fraud, credit risk, forecasting, RAG). GitHub: github.com/MelvTheGoat

## Two tracks
- **Web3 (priority, remote only, no Nigeria-based companies).** Short casual X DMs that lead with something built. Before DMing, reply thoughtfully to 1-2 of the person's recent posts.
- **Nigeria fintech/AI.** LinkedIn connection note, then the follow-up once they accept. For small startups message the CTO/technical co-founder; for big companies message a senior data scientist on the fraud/credit team, not the CEO.

## Weekly plan
1. Setup: LinkedIn headline "ML Engineer | Fraud, Credit Risk & RAG Systems", pin fraud + credit projects, fix CV cut-off lines (SQI bullet ends mid-sentence; fraud project runs into RAG title).
2. Build the Polymarket calibration project (measure how well-calibrated Polymarket prices are on resolved markets, write up with a chart). It becomes the opening line for every Web3 forecasting message and a possible Kalshi builders grant.
3. Week 1: Web3 Tier 1 + Nigeria Tier 1. 3-4 new contacts a day.
4. Week 2: Tier 2 of both tracks; send follow-ups to anyone who accepted.
5. Week 3: Established/Tier 3: apply on careers pages, then message someone on the relevant team saying you applied.
6. Follow up once after ~7 days of no reply, then move on.
7. Refill from the Backlog with another Grok batch when a tier runs dry.
Success check: 3-5 real conversations per 20 contacts.

## Verify before messaging
Anything with a verify_note, "(People tab)", "name unconfirmed", or no handle: confirm name, spelling and role on LinkedIn/X first.

## Templates (fill [Name], [Company], [focus])

### web3_forecasting (X DM)
Hey [Name], big fan of what you're building with [Company].

I'm an ML engineer focused on forecasting and calibration. I recently [built X, e.g. analyzed how well-calibrated Polymarket prices are across resolved markets: link]. Before that I built quantile forecasting and fraud models where getting probabilities right actually mattered (took calibration error from 0.0063 to 0.0005).

Would love to help on the ML side at [Company], full-time, contract, or a trial task. Open to a quick chat?

GitHub: github.com/MelvTheGoat

### web3_fraud (X DM)
Hey [Name], been following [Company]'s work on [focus, e.g. Sybil detection / wallet scoring].

I'm an ML engineer who builds fraud and risk models. Most relevant: a sequence-based fraud system (GRU, TCN, Transformer) over transaction histories that beat a strong LightGBM baseline, served at 5ms p99. Also built calibrated credit scoring with reason codes.

On-chain behavior is the same problem with better data, and I'd love to work on it with you. Full-time, contract, or a trial task, whatever works. Open to a quick chat?

GitHub: github.com/MelvTheGoat

### ng_linkedin — connection note (under 300 characters)
Hi [Name], I'm an ML engineer in Lagos building fraud and credit risk systems (sequence fraud models, calibrated credit decisioning). [Company]'s work on [focus] is exactly what I want to work on. Would love to connect.

### ng_linkedin — follow-up after they accept
Thanks for connecting, [Name].

I've been following [Company]'s work on [specific thing], and it lines up closely with what I've been building.

Most relevant to you:
- A sequence-based fraud detection system (GRU, TCN, Transformer) that beat a LightGBM baseline and cut expected cost per transaction by 27%, served via ONNX at 5 ms p99 latency
- A credit decisioning system with calibrated default probabilities, adverse action reason codes, and a fairness audit
- A RAG assistant over CBN circulars and the NDPA, deployed on GCP Cloud Run

I have a Statistics degree from UI and currently teach ML at SQI College of ICT. GitHub: github.com/MelvTheGoat

I'd really like to contribute to [Company]'s ML work, whether that's a full-time role, a contract, or a trial project. Would you be open to a 15-minute call, or could you point me to the right person on your team?

Thanks,
Oluwatobi

Bullet order: compliance companies (Youverify, Prembly, Pastel) lead with the RAG assistant; credit companies (Mida, Periculum, FairMoney) lead with credit decisioning; language AI (Awarri, Intron) lead with RAG.
