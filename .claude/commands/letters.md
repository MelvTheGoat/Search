---
description: Write cover letters for the newest letter queue
---

Write cover letters for the jobs in the newest queue file.

1. Read `CLAUDE.md` (the writing rules), `profile/cv.md`,
   `profile/projects.md` (extra GitHub projects) and `profile/profile.yaml`. Then read the newest file in `queue/` (the one with
   the latest date in its name). $ARGUMENTS may limit which jobs to do, for
   example "top 3" or "jobs 12 and 15". If it is empty, do every job in the
   queue.

2. For each job, write one file at the exact "letter file" path the queue
   gives. Use this format:

   ```
   ---
   job_id: <job_id from the queue>
   company: <company>
   title: <job title, with any dash replaced by a comma>
   link: <link>
   date: <today, YYYY-MM-DD>
   ---

   ## Cover letter

   <150 to 250 words>

   Oluwatobi Melvyn Mayungbo
   mlvyn.t@gmail.com

   ## Why this company

   <2 to 4 plain sentences>

   ## CV bullets to put first

   - <3 or 4 bullets taken from profile/cv.md>
   ```

   How to write each part:
   - Cover letter: open with something specific from the post about the
     company or role. Pick the one or two CV projects that fit the job best
     (the queue lists the top matching projects) and show what was built and
     the result, with the CV's own numbers. GitHub projects in
     `projects.md` count as real work too. Say plainly what the role needs
     and how the work shown matches it. Do not claim any skill listed under
     "gaps". End with a short, direct line about talking further. Keep it
     between 150 and 250 words, counting only the letter body and sign-off.
   - Why this company: short and concrete, based on what the post says the
     team does. No flattery.
   - CV bullets: choose the 3 or 4 bullets that match this job best, from
     `profile/cv.md` or `profile/projects.md`. When a GitHub project fits the
     job better than a CV project (for example the ledger API for a payments
     backend role, or web3-risk-mcp for a crypto fraud role), put it first
     and say which CV project it should replace for this application. Keep
     the facts and numbers. You may shorten them, but remove every dash
     character and write "0.042 lower PR-AUC" style text instead of a minus
     sign.

3. Run `python hunt.py check`. Fix every problem it lists (dashes, banned
   phrases, numbers not in the CV, length, sign-off), then run it again
   until it passes.

4. Run `python hunt.py mark-drafted` to link each letter to its job and set
   the status to drafted.

5. Reply with a short list: company, role, letter file, and anything the
   person should check before applying (for example a gap the post cares
   about). Never submit an application.
