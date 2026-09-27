import json

from hunt import db
from hunt.page import export_page, import_edits


def seed(conn):
    for i in range(3):
        db.upsert(conn, {"key": f"k{i}", "url_key": f"u{i}", "apply_url": f"https://x/{i}", "company": "Acme",
                         "title": f"ML Engineer {i}", "location_label": "remote_open" if i else "restricted",
                         "fit_score": 50.0 + i, "gaps": ["Spark"]})
    conn.commit()


def test_export_writes_chunks_meta_last(tmp_path):
    conn = db.connect(tmp_path / "jobs.db")
    seed(conn)
    r = export_page(conn, out=tmp_path / "page")
    batches = json.loads((tmp_path / "page" / "writes.json").read_text())
    assert r["jobs"] == 3 and len(batches) == 1
    assert batches[-1][-1]["collection"] == "meta"
    chunk = json.loads((tmp_path / "page" / "chunks" / "c00.json").read_text())
    assert {j["k"] for j in chunk["jobs"]} == {"k0", "k1", "k2"}
    assert all(len(b) <= 50 for b in batches)


def test_page_edits_come_back_unless_older_than_a_local_mark(tmp_path):
    conn = db.connect(tmp_path / "jobs.db")
    seed(conn)
    edits = tmp_path / "edits"
    edits.mkdir()
    (edits / "k1.json").write_text(json.dumps({"status": "applied", "notes": "sent", "date_applied": "2026-09-27",
                                               "updated_at": "2026-09-27T10:00:00Z"}))
    (edits / "k2.json").write_text(json.dumps({"status": "skipped", "updated_at": "2020-01-01T00:00:00Z"}))
    (edits / "gone.json").write_text(json.dumps({"status": "applied", "updated_at": "2026-09-27T10:00:00Z"}))
    jid2 = conn.execute("SELECT id FROM jobs WHERE key='k2'").fetchone()[0]
    db.set_status(conn, jid2, "interview")  # a newer local change
    r = import_edits(conn, edits)
    assert r == {"applied": 1, "already_current": 1, "not_in_database": 1}
    row = conn.execute("SELECT status, notes, date_applied FROM jobs WHERE key='k1'").fetchone()
    assert tuple(row) == ("applied", "sent", "2026-09-27")
    assert conn.execute("SELECT status FROM jobs WHERE key='k2'").fetchone()[0] == "interview"
