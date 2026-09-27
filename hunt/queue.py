"""Build queue/{date}.md: the best new jobs that need a cover letter."""
from datetime import date

from .config import LETTERS_DIR, QUEUE_DIR, label_rank
from .db import loads, rows
from .text import norm, slug


def letter_path(job, day):
    return LETTERS_DIR / f"{day}_{slug(job['company'], 30)}_{slug(job['title'], 50)}.md"


def unique_roles(jobs):
    """Keep one job per company and title, so a role posted in five cities
    shows once. The list must already be sorted best first."""
    seen, out = set(), []
    for j in jobs:
        k = (norm(j["company"]), norm(j["title"]))
        if k not in seen:
            seen.add(k)
            out.append(j)
    return out


def pick(conn, top):
    jobs = rows(conn, "status = 'new' AND location_label != 'restricted' AND (letter_file IS NULL OR letter_file = '')")
    jobs.sort(key=lambda j: (-round(j["fit_score"] or 0), label_rank(j["location_label"]), -(j["fit_score"] or 0)))
    return unique_roles(jobs)[:top]


def build_queue(conn, top=15, day=None):
    day = day or date.today().isoformat()
    jobs = pick(conn, top)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    path = QUEUE_DIR / f"{day}.md"
    out = [f"# Letter queue for {day}", "",
           f"{len(jobs)} jobs. Write one file per job at the path given. Follow the rules in CLAUDE.md.", ""]
    for n, j in enumerate(jobs, start=1):
        rel = letter_path(j, day).relative_to(LETTERS_DIR.parent.parent)
        ev = "; ".join(loads(j["sponsorship_evidence"]))
        out += [
            f"## {n}. {j['company']}: {j['title']}",
            "",
            f"- job_id: {j['id']}",
            f"- letter file: `{rel.as_posix()}`",
            f"- link: {j['apply_url']}",
            f"- location: {j['location']} ({j['country'] or 'unknown'})",
            f"- location label: {j['location_label']}",
            f"- sponsorship: {j['sponsorship']}" + (f" ({ev})" if ev else ""),
            f"- level: {j['level']}" + (" (stretch)" if j["stretch"] else ""),
            f"- fit score: {j['fit_score']}",
            f"- why: {j['why']}",
            f"- top matching projects: {', '.join(loads(j['top_projects'])) or 'none'}",
            f"- gaps: {', '.join(loads(j['gaps'])) or 'none'}",
            "",
            "### Full description",
            "",
            (j["description"] or "(no description given)").strip(),
            "",
            "---",
            "",
        ]
    path.write_text("\n".join(out), encoding="utf-8")
    return path, jobs
