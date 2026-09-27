"""End to end with saved API payloads, no network and no model download."""
import json
from pathlib import Path

from hunt import db
from hunt.labels import Labeller
from hunt.registers import Registers
from hunt.scoring import Embedder, Scorer
from hunt.sources.ats import fetch_ashby, fetch_greenhouse, fetch_lever
from hunt.sources.boards import fetch_remotive

FIX = Path(__file__).parent / "fixtures"


class FakeHttp:
    def __init__(self, payload):
        self.payload = payload

    def get(self, url, params=None, as_json=True, missing_ok=False, **kw):
        return self.payload


def load(name):
    return json.loads((FIX / name).read_text())


def fetch_fixture_jobs():
    jobs = []
    jobs += fetch_greenhouse(FakeHttp(load("greenhouse.json")), {"name": "AcmePay", "ats": "greenhouse", "token": "acmepay"})
    jobs += fetch_lever(FakeHttp(load("lever.json")), {"name": "LagosCo", "ats": "lever", "token": "lagosco"})
    jobs += fetch_ashby(FakeHttp(load("ashby.json")), {"name": "RagCo", "ats": "ashby", "token": "ragco"})
    jobs += fetch_remotive(FakeHttp(load("remotive.json")), {"categories": ["data"]})
    return jobs


def test_parsers_fill_the_schema():
    jobs = fetch_fixture_jobs()
    assert len(jobs) == 6
    gh = jobs[0]
    assert "visa sponsorship" in gh.description and "<" not in gh.description
    lever = jobs[3]
    assert lever.country == "Nigeria" and "Spark" in lever.description
    ashby = jobs[4]
    assert ashby.remote and ashby.extra["location_hints"] == ["EMEA"]


def test_full_process_queue_and_export(tmp_path, monkeypatch):
    from hunt import queue as queue_mod
    from hunt.export import export
    from hunt.pipeline import process

    monkeypatch.setattr(queue_mod, "QUEUE_DIR", tmp_path / "queue")
    conn = db.connect(tmp_path / "jobs.db")
    emb = Embedder(cache_path=tmp_path / "emb.db", log=lambda *_: None)
    emb.fallback = True  # word-hash vectors, so the test needs no model
    scorer = Scorer(embedder=emb, log=lambda *_: None)
    stats = process(conn, fetch_fixture_jobs(), Labeller(registers=Registers()), scorer, log=lambda *_: None)
    assert stats["relevant"] == 5  # the account executive is dropped

    jobs = {j["title"]: j for j in db.rows(conn)}
    grad = jobs["Machine Learning Engineer, Fraud (Graduate)"]
    assert grad["location_label"] == "sponsor_yes" and grad["level"] == "graduate"
    assert "Kubernetes" in db.loads(grad["gaps"])
    assert jobs["Data Scientist"]["location_label"] == "restricted"
    assert jobs["Senior ML Engineer"]["location_label"] == "nigeria"
    assert jobs["AI Engineer (LLM)"]["location_label"] == "remote_open"
    assert jobs["Junior Data Analyst"]["location_label"] == "remote_open"
    assert grad["fit_score"] > jobs["Senior ML Engineer"]["fit_score"]
    assert db.loads(grad["top_projects"])

    path, picked = queue_mod.build_queue(conn, top=15, day="2026-09-26")
    assert all(j["location_label"] != "restricted" for j in picked)
    text = path.read_text()
    assert "job_id:" in text and "Full description" in text and "top matching projects" in text

    out, n_open, n_restricted = export(conn, xlsx=tmp_path / "t.xlsx", csv_path=tmp_path / "t.csv", log=lambda *_: None)
    # Restricted and senior jobs are left out of the tracker.
    assert (n_open, n_restricted) == (3, 0)
