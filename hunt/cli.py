"""Command line: python hunt.py <command>. Run `python hunt.py -h` for help."""
import argparse
import re
import sys
import textwrap
from collections import Counter
from datetime import date

from . import db
from .config import LETTERS_DIR, ROOT, STATUSES, label_rank


def _table(rows, headers):
    widths = [max(len(str(h)), *(len(str(r[i])) for r in rows)) if rows else len(str(h)) for i, h in enumerate(headers)]
    line = "  ".join(str(h).ljust(w) for h, w in zip(headers, widths))
    print(line)
    print("-" * len(line))
    for r in rows:
        print("  ".join(str(v).ljust(w) for v, w in zip(r, widths)))


def _short(s, n):
    s = s or ""
    return s if len(s) <= n else s[: n - 3] + "..."


def print_jobs(jobs):
    rows = [(j["id"], round(j["fit_score"] or 0), j["location_label"], j["level"] + ("*" if j["stretch"] else ""),
             _short(j["company"], 18), _short(j["title"], 44), _short(j["country"], 14)) for j in jobs]
    _table(rows, ["id", "fit", "label", "level", "company", "title", "country"])
    if any(j["stretch"] for j in jobs):
        print("* stretch (mid level)")


def cmd_run(args):
    from .pipeline import run
    conn, s = run(only=args.only, skip_fetch=args.skip_fetch)
    print()
    print(f"Run finished: {s['fetched']} fetched, {s['unique']} unique, {s['relevant']} relevant, {s['new']} new.")
    if s["by_source"]:
        print("By source this run: " + ", ".join(f"{k} {v}" for k, v in sorted(s["by_source"].items())))
    if s["errors"]:
        print(f"{len(s['errors'])} sources had problems:")
        for e in s["errors"][:25]:
            print("  - " + e)
        if len(s["errors"]) > 25:
            print(f"  ... and {len(s['errors']) - 25} more")
    print(f"Tracker: {s['tracker']} ({s['open']} open, {s['restricted']} restricted) and tracker.csv")
    print()
    show_stats(conn)
    print()
    print("Top 10 jobs:")
    from .queue import unique_roles
    jobs = [j for j in db.rows(conn, "location_label != 'restricted'")]
    jobs.sort(key=lambda j: (-round(j["fit_score"] or 0), label_rank(j["location_label"])))
    print_jobs(unique_roles(jobs)[:10])


def cmd_rescore(args):
    from .pipeline import rescore
    rescore()


def cmd_list(args):
    conn = db.connect()
    where, params = ["1=1"], []
    if args.new:
        where.append("date_found = ? AND status = 'new'")
        params.append(date.today().isoformat())
    if args.status:
        where.append("status = ?")
        params.append(args.status)
    if args.label:
        where.append("location_label = ?")
        params.append(args.label)
    elif not args.all:
        where.append("location_label != 'restricted'")
    jobs = db.rows(conn, " AND ".join(where), params)
    jobs.sort(key=lambda j: (-round(j["fit_score"] or 0), label_rank(j["location_label"])))
    if not jobs:
        print("No jobs match." + (" Nothing new today; try `python hunt.py list`." if args.new else ""))
        return
    from .queue import unique_roles
    jobs = unique_roles(jobs)
    print_jobs(jobs[: args.top])
    print(f"\nShowing {min(args.top, len(jobs))} of {len(jobs)} roles. See one with `python hunt.py show <id>`.")


def cmd_show(args):
    conn = db.connect()
    j = conn.execute("SELECT * FROM jobs WHERE id = ?", (args.id,)).fetchone()
    if not j:
        sys.exit(f"No job with id {args.id}")
    j = dict(j)
    for k in ("id", "company", "title", "location", "country", "location_label", "restriction", "sponsorship",
              "level", "fit_score", "why", "apply_url", "status", "date_found", "date_applied", "letter_file", "notes"):
        if j.get(k) not in (None, ""):
            print(f"{k:15} {j[k]}")
    print(f"{'evidence':15} {'; '.join(db.loads(j['sponsorship_evidence']))}")
    print(f"{'projects':15} {', '.join(db.loads(j['top_projects']))}")
    print(f"{'gaps':15} {', '.join(db.loads(j['gaps']))}")
    print(f"{'score parts':15} {j['score_parts']}")
    if args.full:
        print("\n" + (j["description"] or ""))
    else:
        print("\n" + textwrap.shorten(j["description"] or "", 600) + "\n(use --full for the whole description)")


def cmd_queue(args):
    from .queue import build_queue
    conn = db.connect()
    path, jobs = build_queue(conn, top=args.top)
    print(f"Wrote {path.relative_to(ROOT)} with {len(jobs)} jobs.")
    if jobs:
        print_jobs(jobs)
        print("\nNext: type /letters in Claude Code.")


def cmd_check(args):
    from .checker import check_all
    paths = [p for p in map(lambda s: ROOT / s if not s.startswith("/") else s, args.files)] if args.files else None
    problems, n = check_all(paths)
    for p in problems:
        print(p)
    if problems:
        print(f"\n{len(problems)} problems in {len({p.file for p in problems})} of {n} letter files.")
        sys.exit(1)
    print(f"All {n} letter files pass.")


def cmd_mark(args):
    conn = db.connect()
    try:
        db.set_status(conn, args.id, args.status, note=args.note)
    except (KeyError, ValueError) as e:
        sys.exit(str(e))
    j = conn.execute("SELECT company, title, status, date_applied FROM jobs WHERE id = ?", (args.id,)).fetchone()
    print(f"{args.id}: {j['company']}, {j['title']} is now {j['status']}"
          + (f" (applied {j['date_applied']})" if j["status"] == "applied" else ""))
    _quiet_export(conn)


def cmd_note(args):
    conn = db.connect()
    try:
        db.add_note(conn, args.id, args.text)
    except KeyError as e:
        sys.exit(str(e))
    print(f"Note added to job {args.id}.")
    _quiet_export(conn)


def _quiet_export(conn):
    from .export import export, sync_from_xlsx
    try:
        sync_from_xlsx(conn, log=lambda *_: None)
        export(conn, log=print)
    except Exception as e:  # noqa: BLE001
        print(f"(tracker not updated: {e})")


def _job_id(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            m = re.match(r"\s*job_id:\s*(\d+)", line)
            if m:
                return int(m.group(1))
    return None


def cmd_mark_drafted(args):
    from .checker import check_all
    conn = db.connect()
    files = sorted(LETTERS_DIR.glob("*.md"))
    problems, _ = check_all(files)
    bad = {p.file for p in problems}
    marked = 0
    for f in files:
        jid = _job_id(f)
        if jid is None:
            print(f"skip {f.name}: no job_id in the front matter")
            continue
        if str(f) in bad and not args.force:
            print(f"skip {f.name}: fails `python hunt.py check`")
            continue
        row = conn.execute("SELECT status, letter_file FROM jobs WHERE id = ?", (jid,)).fetchone()
        if not row:
            print(f"skip {f.name}: job {jid} is not in the database")
            continue
        rel = f.relative_to(ROOT).as_posix()
        if row["letter_file"] == rel and row["status"] != "new":
            continue
        db.set_letter(conn, jid, rel)
        marked += 1
        print(f"job {jid}: letter {rel}")
    print(f"Marked {marked} jobs as drafted.")
    _quiet_export(conn)


def show_stats(conn):
    jobs = db.rows(conn)
    print(f"{len(jobs)} jobs in the database.")
    for title, field in (("By status", "status"), ("By location label", "location_label"),
                         ("By source", "source"), ("By country (top 20)", "country")):
        c = Counter((j[field] or "unknown") for j in jobs)
        items = c.most_common(20) if field == "country" else sorted(c.items(), key=lambda kv: -kv[1])
        if field == "status":
            items = [(s, c.get(s, 0)) for s in STATUSES]
        if field == "location_label":
            items = sorted(c.items(), key=lambda kv: label_rank(kv[0]))
        print(f"\n{title}:")
        for k, v in items:
            print(f"  {k:22} {v}")


def cmd_stats(args):
    show_stats(db.connect())


def cmd_page_export(args):
    from .page import export_page
    r = export_page(db.connect(), top_open=args.open, top_restricted=args.restricted)
    print(f"Page files ready: {r['jobs']} jobs in {r['chunks']} chunks, {r['letters']} letters, "
          f"{r['batches']} write batches in {r['writes_file']}")


def cmd_page_import(args):
    from .page import import_edits
    conn = db.connect()
    r = import_edits(conn, args.folder)
    print(f"Page edits: {r['applied']} applied, {r['already_current']} already current, "
          f"{r['not_in_database']} for jobs not in the database yet")
    _quiet_export(conn)


def cmd_verify(args):
    from .verify import verify_companies
    verify_companies(write=not args.dry_run)


def main(argv=None):
    p = argparse.ArgumentParser(prog="hunt.py", description="Find, score and track ML/AI jobs.")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("run", help="fetch, label, score, store and export")
    s.add_argument("--only", nargs="+", help="only these sources, e.g. greenhouse remotive")
    s.add_argument("--skip-fetch", action="store_true", help="do not fetch, just re-export")
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("rescore", help="label and score stored jobs again (after changing config)")
    s.set_defaults(fn=cmd_rescore)

    s = sub.add_parser("list", help="best jobs in the terminal")
    s.add_argument("--new", action="store_true", help="only jobs found today with status new")
    s.add_argument("--top", type=int, default=20)
    s.add_argument("--status", choices=STATUSES)
    s.add_argument("--label", help="only this location label")
    s.add_argument("--all", action="store_true", help="include restricted jobs")
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("show", help="all details of one job")
    s.add_argument("id", type=int)
    s.add_argument("--full", action="store_true")
    s.set_defaults(fn=cmd_show)

    s = sub.add_parser("queue", help="write queue/{date}.md for /letters")
    s.add_argument("--top", type=int, default=15)
    s.set_defaults(fn=cmd_queue)

    s = sub.add_parser("check", help="check letter files for dashes, banned phrases and numbers")
    s.add_argument("files", nargs="*")
    s.set_defaults(fn=cmd_check)

    s = sub.add_parser("mark", help="set a job's status, e.g. mark 12 applied")
    s.add_argument("id", type=int)
    s.add_argument("status", choices=STATUSES)
    s.add_argument("--note")
    s.set_defaults(fn=cmd_mark)

    s = sub.add_parser("note", help="add a note to a job")
    s.add_argument("id", type=int)
    s.add_argument("text")
    s.set_defaults(fn=cmd_note)

    s = sub.add_parser("mark-drafted", help="link letter files to jobs and set them to drafted")
    s.add_argument("--force", action="store_true", help="mark even if the checker finds problems")
    s.set_defaults(fn=cmd_mark_drafted)

    s = sub.add_parser("stats", help="counts by status, source, country and label")
    s.set_defaults(fn=cmd_stats)

    s = sub.add_parser("page-export", help="write files for the online tracker page")
    s.add_argument("--open", type=int, default=300, help="how many new open jobs to show")
    s.add_argument("--restricted", type=int, default=60, help="how many new restricted jobs to show")
    s.set_defaults(fn=cmd_page_export)

    s = sub.add_parser("page-import", help="apply status and notes changed on the online page")
    s.add_argument("folder", help="folder of edits/<key>.json files")
    s.set_defaults(fn=cmd_page_import)

    s = sub.add_parser("verify-companies", help="check every board in companies.yaml and remove dead ones")
    s.add_argument("--dry-run", action="store_true", help="report only, do not change companies.yaml")
    s.set_defaults(fn=cmd_verify)

    args = p.parse_args(argv)
    args.fn(args)
