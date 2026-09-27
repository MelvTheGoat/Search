"""SQLite store. Re-runs update job details and scores, but never touch the
fields you own: status, notes, date applied, letter file and date found."""
import json
import sqlite3
from datetime import date, datetime, timezone

from .config import DB_PATH, STATUSES

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    url_key TEXT,
    apply_url TEXT,
    source TEXT,
    company TEXT,
    title TEXT,
    location TEXT,
    country TEXT,
    remote INTEGER,
    description TEXT,
    posted_at TEXT,
    department TEXT,
    level TEXT,
    stretch INTEGER,
    location_label TEXT,
    restriction TEXT,
    sponsorship TEXT,
    sponsorship_evidence TEXT,
    fit_score REAL,
    why TEXT,
    gaps TEXT,
    top_projects TEXT,
    score_parts TEXT,
    last_seen TEXT,
    -- fields you own; a re-run never changes these
    date_found TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    date_applied TEXT,
    notes TEXT,
    letter_file TEXT,
    user_updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_url ON jobs(url_key);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
"""

# Fields a run is allowed to write on an existing row.
MACHINE_FIELDS = [
    "url_key", "apply_url", "source", "company", "title", "location", "country", "remote", "description",
    "posted_at", "department", "level", "stretch", "location_label", "restriction", "sponsorship",
    "sponsorship_evidence", "fit_score", "why", "gaps", "top_projects", "score_parts", "last_seen",
]
USER_FIELDS = ["date_found", "status", "date_applied", "notes", "letter_file", "user_updated_at"]


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def connect(path=None):
    path = path or DB_PATH
    if str(path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _encode(v):
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, bool):
        return int(v)
    return v


def upsert(conn, row, today=None):
    """Insert a new job or refresh an existing one. Returns (id, is_new)."""
    today = today or date.today().isoformat()
    data = {k: _encode(row.get(k)) for k in MACHINE_FIELDS if k in row}
    data["last_seen"] = today
    existing = conn.execute("SELECT id FROM jobs WHERE key = ?", (row["key"],)).fetchone()
    if existing is None and row.get("url_key"):
        existing = conn.execute("SELECT id FROM jobs WHERE url_key = ?", (row["url_key"],)).fetchone()
    if existing:
        sets = ", ".join(f"{k} = ?" for k in data)
        conn.execute(f"UPDATE jobs SET {sets} WHERE id = ?", [*data.values(), existing["id"]])
        return existing["id"], False
    data["key"] = row["key"]
    data["date_found"] = today
    data["status"] = "new"
    cols = ", ".join(data)
    cur = conn.execute(f"INSERT INTO jobs ({cols}) VALUES ({', '.join('?' * len(data))})", list(data.values()))
    return cur.lastrowid, True


def set_status(conn, job_id, status, note=None):
    if status not in STATUSES:
        raise ValueError(f"status must be one of: {', '.join(STATUSES)}")
    row = conn.execute("SELECT id, date_applied FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not row:
        raise KeyError(f"no job with id {job_id}")
    now = utc_now()
    applied = row["date_applied"]
    if status == "applied" and not applied:
        applied = date.today().isoformat()
    conn.execute("UPDATE jobs SET status = ?, date_applied = ?, user_updated_at = ? WHERE id = ?",
                 (status, applied, now, job_id))
    if note:
        add_note(conn, job_id, note)
    conn.commit()


def add_note(conn, job_id, note):
    row = conn.execute("SELECT notes FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not row:
        raise KeyError(f"no job with id {job_id}")
    notes = f"{row['notes']}\n{note}" if row["notes"] else note
    conn.execute("UPDATE jobs SET notes = ?, user_updated_at = ? WHERE id = ?",
                 (notes, utc_now(), job_id))
    conn.commit()


def set_letter(conn, job_id, letter_file):
    """Record a letter; moves a job from new to drafted, never backwards."""
    # Counts as your change, so an older tracker.xlsx cannot undo it.
    conn.execute("UPDATE jobs SET letter_file = ?, status = CASE WHEN status = 'new' THEN 'drafted' ELSE status END, "
                 "user_updated_at = ? WHERE id = ?", (letter_file, utc_now(), job_id))
    conn.commit()


def rows(conn, where="1=1", params=(), order="fit_score DESC"):
    return [dict(r) for r in conn.execute(f"SELECT * FROM jobs WHERE {where} ORDER BY {order}", params)]


def loads(v, default=None):
    if not v:
        return default if default is not None else []
    try:
        return json.loads(v)
    except (TypeError, ValueError):
        return default if default is not None else []
