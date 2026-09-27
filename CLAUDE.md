# Job hunt project

This repo finds ML and AI jobs, scores them against Oluwatobi's CV, and tracks
them. Python code does the finding and scoring. Cover letters are written by
you (Claude Code) inside a session. No API keys, no paid services, and the
tool never submits an application.

Main commands: `python hunt.py run`, `list --new`, `queue --top 15`, `check`,
`mark <id> <status>`, `mark-drafted`, `stats`. Tests: `python -m pytest -q`.

## Writing rules for anything written about Oluwatobi

These apply to every cover letter, "why this company" answer, CV bullet and
message.

1. **Only use facts from `profile/cv.md`.** Never invent experience, skills,
   employers, numbers or dates. If the job asks for something the CV does not
   show, do not claim it. Leave it out.
2. **No em dashes or en dashes anywhere** (no "—", "–" or "−"). Do not use a
   spaced hyphen " - " as a dash either. Use a comma, a full stop or "and".
   This includes titles copied from a job post.
3. Write simply and clearly, like a confident person talking. Short
   sentences. Plain words.
4. No clichés or filler. Never write: "I am excited to apply", "passionate
   about", "leverage", "cutting-edge", "fast-paced environment", "I believe I
   would be a great fit", "delve", "tapestry". The full banned list is in
   `config/writing.yaml`.
5. Open with something specific about the company or the role, taken from
   the job post.
6. Back every claim with a real project or result from the CV, and use its
   numbers where they help. Every number must appear in `profile/cv.md`.
7. Sign off with:

   Oluwatobi Melvyn Mayungbo
   mayungboluwatobi@gmail.com

   Use this email, not the one printed on the CV.

Other facts you may state (from `profile/profile.yaml`): based in Lagos,
Nigeria (WAT, UTC+1), can start immediately, willing to relocate to any
country. Do not mention visas unless the post asks.

After writing, always run `python hunt.py check` and fix every problem it
lists before finishing.

## Daily run and the online tracker page

The tracker page is https://claude.ai/artifact/DBCY7SWfExAuyaTUifxm4G. It
reads records from its own database. Oluwatobi changes status and notes on
the page, and those changes live in the `edits` collection. Follow these
steps in order, so no change made on the page is lost:

1. If `.venv` is missing, run `bash scripts/setup.sh`.
2. Read the page edits: ArtifactData `list` on collection `edits` with
   `out_dir: data/page_in`, then `python hunt.py page-import data/page_in/edits`.
3. `python hunt.py run`
4. `python hunt.py page-import data/page_in/edits` again, because the run
   may have added jobs that the edits point to.
5. `python hunt.py page-export`, then send each batch in
   `data/page/writes.json` with ArtifactData `batch` (each batch is a list
   of writes; send them in order, the last one updates `meta/run`).
6. Report the top new jobs in a few lines.
