import html
import json

import yaml

from hunt import db
from hunt.page import export_page
from hunt.sources import startups as S


def yc_page(props):
    return f'<div data-page="{html.escape(json.dumps({"component": "X", "props": props}))}"></div>'


POST = {"id": 1, "title": "Machine Learning Engineer", "url": "/companies/acme/jobs/abc-ml-engineer",
        "location": "San Francisco, CA, US / Remote (US)", "visa": "US citizen/visa only",
        "minExperience": "3+ years", "skills": ["PyTorch"], "companyName": "Acme",
        "companyBatchName": "W24", "companyOneLiner": "Fraud checks for payments", "roleSpecificType": "Machine learning"}


class FakeHttp:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def get(self, url, params=None, as_json=True, missing_ok=False, **kw):
        self.calls.append(url)
        if url not in self.pages:
            if missing_ok:
                return None
            raise RuntimeError("HTTP 404")
        return self.pages[url]


def test_yc_jobs_carry_visa_years_and_batch():
    http = FakeHttp({
        S.YC + "/jobs/role/software-engineer": yc_page({"jobPostings": [POST, {**POST, "id": 2, "title": "Sales Lead",
                                                                               "url": "/companies/acme/jobs/x"}]}),
        S.YC + POST["url"]: yc_page({"job": {**POST, "description": "<p>Build fraud models.</p>"}}),
    })
    jobs = S.fetch_yc(http, {"pages": ["/jobs/role/software-engineer"]},
                      keep_title=lambda t: "learning" in t.lower())
    assert len(jobs) == 1  # the sales job's page is never read
    j = jobs[0]
    assert j.source == "yc" and j.company == "Acme" and j.extra["startup"] == "YC W24"
    assert j.apply_url == "https://www.ycombinator.com/companies/acme/jobs/abc-ml-engineer"
    assert "Work authorization required" in j.description and "3+ years of experience" in j.description
    assert "Build fraud models." in j.description and j.remote


def test_ats_links_are_found_in_pages_and_urls():
    assert S.ats_from_text('<a href="https://jobs.ashbyhq.com/acme/123">') == ("ashby", "acme")
    assert S.ats_from_text("https://job-boards.greenhouse.io/acmeai/jobs/9") == ("greenhouse", "acmeai")
    assert S.ats_from_text("https://jobs.ashbyhq.com/American%20Terawatt") == ("ashby", "American Terawatt")
    assert S.ats_from_text("https://boards.greenhouse.io/embed/job_board?for=acme") == ("greenhouse", "acme")
    assert S.ats_from_text("no board here") is None


def test_breakout_list_reads_the_structured_company_list():
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "name": "Breakout List"},
        {"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "item": {"@type": "Organization", "name": "Aaru", "url": "https://aaru.com"}},
            {"@type": "ListItem", "item": {"@type": "Organization", "name": "Exa", "url": "https://www.exa.ai/"}}]}]}
    page = f'<script type="application/ld+json">{json.dumps(ld)}</script><a href="https://x.com/someone">@someone</a>'
    out = S.breakout_companies(FakeHttp({"https://breakoutlist.com/": page}), log=lambda *a: None)
    assert [(c["name"], c["domain"]) for c in out] == [("Aaru", "aaru.com"), ("Exa", "exa.ai")]


def test_resolve_prefers_links_on_the_company_site():
    http = FakeHttp({"https://acme.ai/careers": '<a href="https://jobs.lever.co/acme-ai">Jobs</a>'})
    assert S.resolve(http, {"name": "Acme", "domain": "acme.ai"}) == ("lever", "acme-ai")


def test_resolve_only_trusts_a_guessed_greenhouse_board_with_the_same_name():
    http = FakeHttp({
        "https://boards-api.greenhouse.io/v1/boards/normal": {"name": "Normal Gear Co"},
        "https://boards-api.greenhouse.io/v1/boards/normal/jobs": {"jobs": [{"id": 1}]},
    })
    assert S.resolve(http, {"name": "Normal Computing"}) is None
    http.pages["https://boards-api.greenhouse.io/v1/boards/normalcomputing"] = {"name": "Normal Computing"}
    http.pages["https://boards-api.greenhouse.io/v1/boards/normalcomputing/jobs"] = {"jobs": [{"id": 1}]}
    assert S.resolve(http, {"name": "Normal Computing"}) == ("greenhouse", "normalcomputing")


def test_discover_merges_lists_and_skips_known_companies(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "STARTUPS_FILE", tmp_path / "startups.yaml")
    monkeypatch.setattr(S, "known_boards", lambda: {("ashby", "openai"): "OpenAI"})
    lists = [
        lambda http, log: [{"name": "Exa", "domain": "exa.ai", "source": "Breakout List"},
                           {"name": "OpenAI", "domain": "openai.com", "source": "Breakout List"}],
        lambda http, log: [{"name": "Exa", "domain": "exa.ai", "source": "Next Play"},
                           {"name": "Nowhere", "domain": "nowhere.dev", "source": "Next Play"}],
    ]
    http = FakeHttp({"https://exa.ai/careers": '<a href="https://jobs.ashbyhq.com/exa">'})
    assert S.discover(http, log=lambda *a: None, lists=lists) == 2
    data = yaml.safe_load((tmp_path / "startups.yaml").read_text())
    by = {s["name"]: s for s in data["startups"]}
    assert by["Exa"]["ats"] == "ashby" and by["Exa"]["sources"] == ["Breakout List", "Next Play"]
    assert by["OpenAI"]["in_companies"] and "ats" not in by["OpenAI"]
    assert [m["name"] for m in data["no_board_found"]] == ["Nowhere"]
    assert S.startup_names()["exa"] == "Breakout List, Next Play"
    assert not S.stale()


def test_startup_jobs_get_their_own_place_on_the_page(tmp_path):
    conn = db.connect(tmp_path / "jobs.db")
    for i in range(4):
        db.upsert(conn, {"key": f"k{i}", "url_key": f"u{i}", "apply_url": f"https://x/{i}", "company": f"Co{i}",
                         "title": f"ML Engineer {i}", "location_label": "remote_open", "fit_score": 50.0 + i,
                         "startup": "YC W24" if i == 0 else None})
    conn.commit()
    # Only one slot in the main list, yet the startup job (lowest fit) is still shown.
    export_page(conn, top_open=1, top_near=0, out=tmp_path / "page")
    jobs = json.loads((tmp_path / "page" / "chunks" / "c00.json").read_text())["jobs"]
    assert {j["k"]: j["sup"] for j in jobs} == {"k3": "", "k0": "YC W24"}
