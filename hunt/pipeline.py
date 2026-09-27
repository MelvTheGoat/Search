"""The full run: fetch, dedupe, filter, label, score, store, export."""
import re
import time
from collections import Counter
from datetime import date

from . import db
from .config import load_env, load_yaml
from .dedupe import dedupe
from .export import export, sync_from_xlsx
from .http import Http
from .labels import Labeller
from .h1b import H1B
from .registers import load_registers
from .scoring import Scorer, is_relevant
from .sources import cached
from .sources.ats import ATS_NAMES, fetch_company
from .sources.boards import BOARDS, NEEDS_KEY, has_keys


def make_http(cfg):
    h = cfg.get("http", {})
    return Http(min_interval=h.get("min_interval", 1.0), per_host=h.get("per_host", {}),
                retries=h.get("retries", 4), backoff=h.get("backoff", 2.0), timeout=h.get("timeout", 30))


def load_companies():
    data = load_yaml("companies.yaml")
    return [c for c in data.get("companies", []) if c.get("token") and c.get("ats")]


def fetch_all(http, cfg, log=print, only=None):
    """Fetch every enabled source. One broken source never stops the run."""
    jobs, counts, errors = [], Counter(), []
    companies = load_companies()
    ats_on = [a for a in ATS_NAMES if cfg.get(a, {}).get("enabled", True)]
    if only:
        ats_on = [a for a in ats_on if a in only]
    todo = [c for c in companies if c["ats"] in ats_on]
    if todo:
        log(f"Fetching {len(todo)} company boards...")
    scoring = load_yaml("scoring.yaml")

    def keep_title(title):
        # Used by boards that need one extra call per job for the description.
        f = scoring["filter"]
        return (not any(re.search(p, title, re.I) for p in f["drop_titles"])
                and any(re.search(p, title, re.I) for p in f["keep_titles"]))

    for i, c in enumerate(todo, start=1):
        try:
            found = fetch_company(http, c, keep_title=keep_title)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{c['ats']}/{c['token']}: {e}")
            continue
        if found is None:
            errors.append(f"{c['ats']}/{c['token']}: board not found (run `python hunt.py verify-companies`)")
            continue
        jobs += found
        counts[c["ats"]] += len(found)
        if i % 25 == 0:
            log(f"  {i}/{len(todo)} boards, {len(jobs)} jobs so far")

    for name, fn in BOARDS.items():
        scfg = cfg.get(name, {})
        if not scfg.get("enabled", True) or (only and name not in only):
            continue
        if not has_keys(name):
            log(f"  {name}: skipped (add {' and '.join(NEEDS_KEY[name])} to .env to use it)")
            continue
        try:
            found = cached(name, scfg.get("refetch_hours", 6), lambda: fn(http, scfg, log=log), log=log)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: {e}")
            continue
        jobs += found
        counts[name] += len(found)
        log(f"  {name}: {len(found)} jobs")
    return jobs, counts, errors


def process(conn, jobs, labeller, scorer, log=print, today=None):
    """Steps 1 to 4 for already-fetched jobs. Returns stats."""
    raw = len(jobs)
    jobs = dedupe(jobs)
    deduped = len(jobs)
    cfg = scorer.cfg
    jobs = [j for j in jobs if j.title and is_relevant(j.title, j.description, cfg)]
    log(f"{raw} fetched, {deduped} after dedupe, {len(jobs)} related to data, ML or AI")
    t0 = time.time()
    scorer.prepare(jobs)
    if jobs:
        log(f"Embedded {len(jobs)} jobs in {time.time() - t0:.0f}s")
    new = 0
    for j in jobs:
        lab = labeller.label(j)
        sc = scorer.score(j)
        row = {
            "key": j.key, "url_key": j.url_key, "apply_url": j.apply_url, "source": j.source,
            "company": j.company, "title": j.title, "location": j.location,
            "country": lab.country or j.country, "remote": j.remote, "description": j.description,
            "posted_at": j.posted_at, "department": j.department,
            "location_label": lab.label, "restriction": lab.restriction,
            "sponsorship": lab.sponsorship, "sponsorship_evidence": lab.evidence,
            **sc,
        }
        _, is_new = db.upsert(conn, row, today=today)
        new += is_new
    conn.commit()
    return {"fetched": raw, "unique": deduped, "relevant": len(jobs), "new": new}


def run(log=print, only=None, skip_fetch=False):
    load_env()
    cfg = load_yaml("sources.yaml")
    http = make_http(cfg)
    conn = db.connect()
    if skip_fetch:
        jobs, counts, errors = [], Counter(), []
    else:
        jobs, counts, errors = fetch_all(http, cfg, log=log, only=only)
    log("Loading sponsor registers...")
    registers = load_registers(http, log=log)
    labeller = Labeller(registers=registers, h1b=H1B(http, log=log))
    scorer = Scorer(log=log)
    stats = process(conn, jobs, labeller, scorer, log=log)
    sync_from_xlsx(conn, log=log)
    out, n_open, n_restricted = export(conn, log=log)
    stats.update({"by_source": dict(counts), "errors": errors, "tracker": str(out),
                  "open": n_open, "restricted": n_restricted, "date": date.today().isoformat()})
    return conn, stats


def rescore(log=print):
    """Label and score every stored job again, for example after you change
    config/scoring.yaml. Your status and notes are kept."""
    from .models import Job
    load_env()
    conn = db.connect()
    http = make_http(load_yaml("sources.yaml"))
    labeller = Labeller(registers=load_registers(http, log=log), h1b=H1B(http, log=log))
    scorer = Scorer(log=log)
    companies = {c["name"]: c for c in load_companies()}
    jobs = []
    for r in db.rows(conn):
        c = companies.get(r["company"], {})
        extra = {k: c[k] for k in ("known_sponsor", "aliases") if c.get(k)}
        jobs.append(Job(source=r["source"], company=r["company"], title=r["title"], location=r["location"] or "",
                        apply_url=r["apply_url"] or "", description=r["description"] or "", remote=bool(r["remote"]),
                        posted_at=r["posted_at"] or "", department=r["department"] or "", extra=extra))
    scorer.prepare(jobs)
    for j in jobs:
        lab = labeller.label(j)
        sc = scorer.score(j)
        db.upsert(conn, {"key": j.key, "url_key": j.url_key, "country": lab.country, "location_label": lab.label,
                         "restriction": lab.restriction, "sponsorship": lab.sponsorship,
                         "sponsorship_evidence": lab.evidence, **sc})
    conn.commit()
    sync_from_xlsx(conn, log=log)
    export(conn, log=log)
    log(f"Rescored {len(jobs)} jobs")
    return conn
