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
    # The restricted job (k0) is left out of the page.
    assert r["jobs"] == 2 and len(batches) == 1
    assert batches[-1][-1]["collection"] == "meta"
    chunk = json.loads((tmp_path / "page" / "chunks" / "c00.json").read_text())
    assert {j["k"] for j in chunk["jobs"]} == {"k1", "k2"}
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


def test_letter_parts_leave_out_headings_and_file_notes(tmp_path):
    from hunt.page import letter_parts
    f = tmp_path / "l.md"
    f.write_text("---\njob_id: 1\n---\n\n## Cover letter\n\nHello there.\n\nOluwatobi Melvyn Mayungbo\nmlvyn.t@gmail.com\n\n"
                 "## Why this company\n\nGood team.\n\n## Tailored CV\n\noutput/cvs/x.pdf\n")
    p = letter_parts(f)
    assert p["letter"] == "Hello there.\n\nOluwatobi Melvyn Mayungbo\nmlvyn.t@gmail.com"
    assert p["why"] == "Good team."
    assert "##" not in p["letter"] and "output/" not in p["letter"]


def test_out_of_reach_rules():
    from hunt.reach import out_of_reach
    base = {"location_label": "remote_open", "level": "junior", "description": "Python and SQL."}
    assert out_of_reach(base) is None
    assert out_of_reach({**base, "location_label": "restricted", "restriction": "US only"}).startswith("restricted")
    assert "sponsors" in out_of_reach({**base, "location_label": "sponsor_unknown"})
    assert out_of_reach({**base, "level": "senior"}) == "senior role"
    assert "students" in out_of_reach({**base, "description": "You are currently pursuing a degree in CS."})
    assert "Master" in out_of_reach({**base, "description": "A Master's degree in Computer Science is required."})
    assert out_of_reach({**base, "description": "Bachelor's or Master's degree in Statistics."}) is None
    assert out_of_reach({**base, "description": "A PhD is a plus."}) is None
