"""Sync with the online tracker page.

The page keeps two kinds of records:
  chunks/<n>   job details from the last run, 100 jobs per record
  meta/run     when the last run happened, plus counts
  letters/<key> the cover letter text for a job
  cvdocs/<key> the tailored CV as a Word file (base64)
  cvpdfs/<key> the tailored CV as a PDF (base64), so the page can save it
               on phones, where fetching the uploaded PDF can fail
  edits/<key>  what you changed on the page: status, notes, date applied

page-export writes JSON files and a list of writes for Claude to send.
page-import reads the edits you made on the page back into data/jobs.db,
so the page and the tracker agree and a fresh start loses nothing."""
import base64
import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .config import DATA_DIR, ROOT, STATUSES, label_rank
from .db import loads, rows

PAGE_DIR = DATA_DIR / "page"
CHUNK = 100
MAX_CHUNKS = 20


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _assets():
    """PDF CVs uploaded to the page: file name -> page URL (output/cvs/assets.json)."""
    path = ROOT / "output" / "cvs" / "assets.json"
    return json.loads(path.read_text()) if path.exists() else {}


def _compact(j, assets=None):
    ev = loads(j["sponsorship_evidence"])
    cv = Path(j["cv_file"]).stem if j.get("cv_file") else ""
    return {
        "k": j["key"], "id": j["id"], "co": j["company"], "t": j["title"], "lvl": j["level"],
        "st": bool(j["stretch"]), "ctry": j["country"] or "", "lab": j["location_label"],
        "sp": j["sponsorship"] or "", "spe": ev[0][:220] if ev else "", "fit": j["fit_score"],
        "why": j["why"] or "", "gaps": loads(j["gaps"])[:8], "proj": loads(j["top_projects"]),
        "url": j["apply_url"], "lf": j["letter_file"] or "", "status": j["status"],
        "df": j["date_found"] or "", "da": j["date_applied"] or "", "notes": j["notes"] or "",
        "su": j["user_updated_at"] or "", "rst": (j["restriction"] or "")[:300], "src": j["source"],
        "loc": (j["location"] or "")[:120], "posted": j["posted_at"] or "",
        "cvn": cv, "cvp": (assets or {}).get(cv + ".pdf", "") if cv else "",
    }


def _letter_text(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines = lines[i + 1:]
                break
    return "\n".join(lines).strip()


def letter_parts(path):
    """Split a letter file into the text to paste (letter body and sign-off)
    and the "why this company" answer. Headings and file notes are left out."""
    parts, cur = {}, "intro"
    for line in _letter_text(path).splitlines():
        m = re.match(r"^##\s+(.*)", line)
        if m:
            cur = m.group(1).strip().lower()
            parts[cur] = []
            continue
        parts.setdefault(cur, []).append(line)
    text = lambda k: "\n".join(parts.get(k, [])).strip()
    return {"letter": text("cover letter") or text("intro"), "why": text("why this company")}


def export_page(conn, top_open=300, top_restricted=0, top_near=150, out=PAGE_DIR):
    """Write the page records as JSON files plus writes.json, a list of
    batches (50 writes each) ready to send with the ArtifactData tool."""
    jobs = rows(conn)
    jobs.sort(key=lambda j: (-(j["fit_score"] or 0), label_rank(j["location_label"])))
    tracked = [j for j in jobs if j["status"] != "new"]
    from .queue import unique_roles
    from .reach import within_reach
    reachable = [j for j in jobs if j["status"] == "new" and within_reach(j)]
    fresh_open = unique_roles(reachable)[:top_open]
    fresh_rest = unique_roles([j for j in jobs if j["status"] == "new" and j["location_label"] == "restricted"])[:top_restricted]
    # Jobs in Africa, or remote and open to Nigeria, need no or little visa
    # help, so the best of them are always shown even below the top list.
    shown = {j["id"] for j in fresh_open}
    near = unique_roles([j for j in reachable if j["id"] not in shown
                         and j["location_label"] in ("remote_open", "nigeria", "africa")])[:top_near]
    chosen = tracked + fresh_open + near + fresh_rest

    if out.exists():
        shutil.rmtree(out)
    (out / "chunks").mkdir(parents=True)
    (out / "letters").mkdir()
    (out / "cvdocs").mkdir()
    (out / "cvpdfs").mkdir()
    (out / "packs").mkdir()
    assets = _assets()
    run = now_utc()
    writes = []
    chunk_ids = []
    for n in range(0, len(chosen), CHUNK):
        cid = f"c{n // CHUNK:02d}"
        chunk_ids.append(cid)
        p = out / "chunks" / f"{cid}.json"
        p.write_text(json.dumps({"run": run, "jobs": [_compact(j, assets) for j in chosen[n:n + CHUNK]]}, ensure_ascii=False))
        writes.append({"op": "set", "collection": "chunks", "doc_id": cid, "file_path": str(p)})
    for n in range(len(chunk_ids), MAX_CHUNKS):
        writes.append({"op": "delete", "collection": "chunks", "doc_id": f"c{n:02d}"})

    letters = 0
    for j in chosen:
        lf = j["letter_file"]
        if lf and (ROOT / lf).exists():
            p = out / "letters" / f"{j['key']}.json"
            lp = letter_parts(ROOT / lf)
            p.write_text(json.dumps({"file": lf, "text": lp["letter"], "why": lp["why"], "run": run}, ensure_ascii=False))
            writes.append({"op": "set", "collection": "letters", "doc_id": j["key"], "file_path": str(p)})
            letters += 1
        if lf or j.get("cv_file"):
            # The full application pack shown on the page: posting, CV, letter.
            from .cv import html_for_job
            p = out / "packs" / f"{j['key']}.json"
            p.write_text(json.dumps({"desc": (j["description"] or "")[:20000], "cv_html": html_for_job(j["id"]),
                                     **(letter_parts(ROOT / lf) if lf and (ROOT / lf).exists() else {"letter": "", "why": ""}),
                                     "run": run}, ensure_ascii=False))
            writes.append({"op": "set", "collection": "packs", "doc_id": j["key"], "file_path": str(p)})
        cvf = j.get("cv_file")
        if cvf and (ROOT / cvf).exists():
            p = out / "cvdocs" / f"{j['key']}.json"
            p.write_text(json.dumps({"name": Path(cvf).name, "b64": base64.b64encode((ROOT / cvf).read_bytes()).decode()}))
            writes.append({"op": "set", "collection": "cvdocs", "doc_id": j["key"], "file_path": str(p)})
            pdf = (ROOT / cvf).with_suffix(".pdf")
            if pdf.exists():
                p = out / "cvpdfs" / f"{j['key']}.json"
                p.write_text(json.dumps({"name": pdf.name, "b64": base64.b64encode(pdf.read_bytes()).decode()}))
                writes.append({"op": "set", "collection": "cvpdfs", "doc_id": j["key"], "file_path": str(p)})

    counts = {
        "status": dict(Counter(j["status"] for j in jobs)),
        "label": dict(Counter(j["location_label"] for j in jobs)),
        "source": dict(Counter(j["source"] for j in jobs)),
        "total": len(jobs),
        "new_today": sum(1 for j in jobs if j["date_found"] == datetime.now().date().isoformat()),
    }
    meta = {"run": run, "chunks": chunk_ids, "counts": counts, "shown": len(chosen), "letters": letters}
    mp = out / "meta.json"
    mp.write_text(json.dumps(meta))
    # meta goes last, so the page only switches to the new run once every chunk is in.
    batches = [writes[i:i + 49] for i in range(0, len(writes), 49)] or [[]]
    batches[-1].append({"op": "set", "collection": "meta", "doc_id": "run", "file_path": str(mp)})
    (out / "writes.json").write_text(json.dumps(batches, indent=1))
    return {"jobs": len(chosen), "chunks": len(chunk_ids), "letters": letters, "batches": len(batches),
            "writes_file": str(out / "writes.json")}


def import_edits(conn, folder):
    """Apply edits made on the page. An edit wins over the database when it
    is newer than your last `mark` or `note` there."""
    folder = Path(folder)
    applied = skipped = missing = 0
    for f in sorted(folder.glob("*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        doc = doc.get("data", doc) if isinstance(doc.get("data"), dict) else doc
        key = f.stem
        row = conn.execute("SELECT id, status, notes, date_applied, user_updated_at FROM jobs WHERE key = ?",
                           (key,)).fetchone()
        if not row:
            missing += 1
            continue
        at = doc.get("updated_at") or ""
        if row["user_updated_at"] and row["user_updated_at"] >= at:
            skipped += 1
            continue
        status = doc.get("status") if doc.get("status") in STATUSES else row["status"]
        conn.execute("UPDATE jobs SET status = ?, notes = ?, date_applied = ?, user_updated_at = ? WHERE id = ?",
                     (status, doc.get("notes", row["notes"]) or None,
                      doc.get("date_applied", row["date_applied"]) or None, at, row["id"]))
        applied += 1
    conn.commit()
    return {"applied": applied, "already_current": skipped, "not_in_database": missing}
