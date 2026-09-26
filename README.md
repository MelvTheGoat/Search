# Job hunt

A small Python tool that finds ML and AI jobs in any country, scores each one
against your CV, and keeps them all in a tracker. Cover letters are written
by Claude Code inside a session with the `/letters` command, using your
Claude plan. No API keys and no paid services are needed. The tool never
applies for you. You read each job and apply yourself.

## What it does

1. Reads jobs from free, official sources:
   - company boards on Greenhouse, Lever and Ashby (list in `config/companies.yaml`)
   - RemoteOK, Remotive, Arbeitnow and Himalayas
   - Adzuna, only if you add a free key to `.env`
2. Puts them in one format and removes duplicates (same apply link, or same
   company, title and location).
3. Drops jobs clearly unrelated to data, ML or AI.
4. Gives each job a location label, best first:
   - `remote_open`: remote and open to Nigeria, Africa, EMEA or worldwide
   - `nigeria`: onsite or hybrid in Nigeria
   - `sponsor_yes`: abroad, and the post offers a visa or relocation
   - `sponsor_likely`: abroad, and the company is a known sponsor (UK or
     Netherlands register, or marked in `companies.yaml`)
   - `sponsor_unknown`: abroad, and the post says nothing about it
   - `restricted`: no sponsorship, needs existing right to work, remote for
     one country only, or needs citizenship or clearance. These go on their
     own tab with the exact sentence that restricts them. Nothing is deleted.
5. Scores each job from 0 to 100 on your computer (no AI calls):
   embedding match to your CV and projects, skills overlap, level and role.
   It also writes a one-line `why`, the `gaps` and the top matching projects.
6. Saves everything in `data/jobs.db` and writes `tracker.xlsx` and
   `tracker.csv`.

## Setup

You need Python 3.10 or newer.

```bash
git clone https://github.com/MelvTheGoat/Search.git
cd Search
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The first run downloads the small `all-MiniLM-L6-v2` model (about 90 MB)
once. It runs on CPU.

If `pip` pulls a very large PyTorch with GPU parts, install the CPU build
first, then the rest:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

Optional: Adzuna. Get a free key at https://developer.adzuna.com/, then:

```bash
cp .env.example .env     # then put your ADZUNA_APP_ID and ADZUNA_APP_KEY in .env
```

Check the company list once (and any time you add companies):

```bash
python hunt.py verify-companies
```

It tests every board. If a token is dead, it tries the same name on the
other two ATSs, and moves boards that are gone to `config/companies_removed.yaml`.

## Daily routine

```bash
python hunt.py run               # 1. fetch, label, score, update the tracker
python hunt.py list --new        # 2. look at today's best new jobs
python hunt.py queue --top 15    # 3. write queue/<date>.md for letters
```

4. Open Claude Code in this folder and type `/letters`. Claude writes a cover
   letter, a short "why this company" answer and the CV bullets to put first
   for each job, into `output/letters/`. It then runs `python hunt.py check`,
   fixes what it flags, and runs `python hunt.py mark-drafted`.
   You can also type `/letters top 3` to do fewer.
5. Read each letter, apply yourself, then record it:

```bash
python hunt.py mark 42 applied               # sets today's date as date applied
python hunt.py mark 42 interview --note "call on Monday"
python hunt.py note 42 "recruiter: Ada"
```

Status values: `new`, `drafted`, `applied`, `interview`, `rejected`, `offer`, `skipped`.

You can also change `status`, `notes` and `date applied` right in
`tracker.xlsx`. The next run reads your edits back before it writes the
file again, so they are kept. Close the file before a run.

## All commands

| Command | What it does |
| --- | --- |
| `python hunt.py run` | Full pipeline and tracker export, then stats and the top 10 |
| `python hunt.py run --only greenhouse remotive` | Only some sources |
| `python hunt.py list --new` | Today's best new jobs |
| `python hunt.py list --top 50 --label nigeria` | Filter by label (`--all` includes restricted) |
| `python hunt.py show 42 --full` | Everything about one job |
| `python hunt.py queue --top 15` | Build the letter queue |
| `python hunt.py check` | Check letters for dashes, banned phrases and numbers not in your CV |
| `python hunt.py mark-drafted` | Link letters to jobs and set them to drafted |
| `python hunt.py mark <id> <status>` | Change a status |
| `python hunt.py note <id> "text"` | Add a note |
| `python hunt.py stats` | Counts by status, source, country and label |
| `python hunt.py rescore` | Score stored jobs again after you change the config |
| `python hunt.py verify-companies` | Test all company boards and remove dead ones |

A re-run never changes your status, notes, date applied, letter file or the
date a job was first found.

## Files you can change

- `profile/cv.md`: your CV. Letters may only use facts from here.
- `profile/profile.yaml`: contact details, level and target roles.
- `config/companies.yaml`: company boards, one per line. Add more any time.
- `config/scoring.yaml`: score weights, level scores, title patterns and the
  keyword filter. Run `python hunt.py rescore` after a change.
- `config/skills.yaml`: skills to look for. Missing ones show up as `gaps`.
- `config/sponsorship.yaml`: phrases that mean "we sponsor" or "we do not".
- `config/sources.yaml`: turn sources on or off, rate limits and page counts.
- `config/writing.yaml`: banned phrases and letter length for `check`.
- `CLAUDE.md`: the writing rules Claude follows in every session.

## How the score works

Each part is between 0 and 1, and the fit score is their weighted average
times 100. Weights live in `config/scoring.yaml`.

- CV match: cosine similarity between the job text and your whole CV.
- Project match: the same, against your best matching project.
- Skills: share of the skills named in the job that are also in your CV.
- Level: intern, graduate, junior and entry score highest. Mid is marked
  "stretch". Senior, staff, principal, lead and manager score low but are kept.
- Role: target titles (ML, AI, data science, research, fraud and risk) score
  higher than related ones (data analyst, analytics engineer).
- Domain: a small bonus for fraud, risk, credit and payments work.

Embeddings are cached in `data/embeddings.db`, so re-runs are fast.

## Sponsor registers

The tool downloads the UK Register of Licensed Sponsors and the Netherlands
IND register of recognised sponsors, keeps them in `data/registers/`, and
downloads them again when they are more than a week old. A company found in
either list gets `sponsor_likely` (unless the post itself says yes or no),
with the register entry saved as evidence.

## Being polite to sources

Every request sends a clear User-Agent, waits between calls to the same site,
and retries with growing waits on errors. Aggregator results are cached for
some hours (Remotive asks for no more than four calls a day). RemoteOK asks
that you link back to them, so their job links are kept as the apply link.

## Run it every day on a schedule

### Mac or Linux (cron)

Run `crontab -e` and add a line like this (runs at 7:00 every day; change
the path to your folder):

```cron
0 7 * * * cd /path/to/Search && .venv/bin/python hunt.py run >> data/run.log 2>&1
```

### Windows (Task Scheduler)

1. Open Task Scheduler and choose **Create Basic Task**.
2. Name it "Job hunt" and pick **Daily** at a time you like.
3. Action: **Start a program**.
   - Program: `C:\path\to\Search\.venv\Scripts\python.exe`
   - Arguments: `hunt.py run`
   - Start in: `C:\path\to\Search`
4. Finish. Right-click the task and choose **Run** once to test it.

Or from a command prompt:

```bat
schtasks /Create /SC DAILY /ST 07:00 /TN "Job hunt" /TR "cmd /c cd /d C:\path\to\Search && .venv\Scripts\python.exe hunt.py run >> data\run.log 2>&1"
```

## Tests

```bash
python -m pytest -q
```

They cover dedupe, location labels, the "never overwrite my status" rule,
tracker edits, the writing checker, and a full offline run with sample data.

## What is not saved in git

`.env`, `data/` (database, caches, registers), `tracker.xlsx`,
`tracker.csv` and `queue/` stay on your computer. Letters in
`output/letters/` are saved in git so you keep them.
