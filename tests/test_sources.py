"""Parsers for the extra sources, fed with small saved samples."""
from hunt.sources.ats import fetch_personio, fetch_recruitee, fetch_smartrecruiters, fetch_workable
from hunt.sources.boards import fetch_hn_whoishiring, fetch_jobicy, fetch_weworkremotely


class RouteHttp:
    """Returns a payload based on a piece of the URL."""

    def __init__(self, routes):
        self.routes = routes

    def get(self, url, params=None, as_json=True, missing_ok=False, **kw):
        for part, payload in self.routes.items():
            if part in url:
                return payload
        if missing_ok:
            return None
        raise AssertionError(f"unexpected url {url}")

    post = get


CO = {"name": "Co", "token": "co"}


def test_smartrecruiters_fetches_details_only_for_kept_titles():
    http = RouteHttp({
        "/postings/1": {"jobAd": {"sections": {"jobDescription": {"text": "<p>Build ML models in Python.</p>"}}}},
        "/postings": {"totalFound": 2, "content": [
            {"id": "1", "name": "Machine Learning Engineer", "releasedDate": "2026-09-01T00:00:00Z",
             "location": {"city": "Berlin", "country": "de", "remote": False}, "department": {"label": "AI"}},
            {"id": "2", "name": "Office Manager", "location": {"city": "Berlin", "country": "de"}},
        ]},
    })
    jobs = fetch_smartrecruiters(http, {**CO, "ats": "smartrecruiters"}, keep_title=lambda t: "Machine" in t)
    assert len(jobs) == 1
    j = jobs[0]
    assert j.country == "Germany" and "Build ML models" in j.description
    assert j.apply_url == "https://jobs.smartrecruiters.com/co/1"


def test_workable():
    http = RouteHttp({"workable.com": {"name": "Co", "jobs": [
        {"title": "Data Scientist", "url": "https://apply.workable.com/co/j/ABC/", "telecommuting": True,
         "locations": [{"city": "Lagos", "region": "Lagos", "country": "Nigeria"}],
         "description": "<p>SQL and Python</p>", "published_on": "2026-09-10", "department": "Data"}]}})
    j = fetch_workable(http, {**CO, "ats": "workable"})[0]
    assert j.remote and "Lagos" in j.location and "SQL" in j.description


def test_recruitee():
    http = RouteHttp({"recruitee.com": {"offers": [
        {"title": "ML Engineer", "location": "Amsterdam, Netherlands", "country_code": "NL", "remote": False,
         "careers_url": "https://co.recruitee.com/o/ml", "description": "<p>Models</p>", "requirements": "<p>PyTorch</p>",
         "published_at": "2026-09-01 10:00:00 UTC"}]}})
    j = fetch_recruitee(http, {**CO, "ats": "recruitee"})[0]
    assert j.country == "Netherlands" and "PyTorch" in j.description and j.posted_at == "2026-09-01"


def test_personio():
    xml = """<?xml version="1.0" encoding="UTF-8"?><workzag-jobs><position><id>77</id><office>Munich</office>
    <additionalOffices><office>Remote</office></additionalOffices><department>Data</department>
    <name>Junior Data Scientist</name><jobDescriptions><jobDescription><name>Your tasks</name>
    <value><![CDATA[<p>Forecasting with Python</p>]]></value></jobDescription></jobDescriptions>
    <seniority>entry-level</seniority><createdAt>2026-09-02T10:00:00+00:00</createdAt></position></workzag-jobs>"""
    j = fetch_personio(RouteHttp({"personio.de": xml}), {**CO, "ats": "personio"})[0]
    assert j.title == "Junior Data Scientist" and "Forecasting" in j.description
    assert j.apply_url.endswith("/job/77") and j.remote


def test_jobicy():
    http = RouteHttp({"jobicy.com": {"jobs": [
        {"url": "https://jobicy.com/jobs/1", "jobTitle": "AI Engineer", "companyName": "Remote Co",
         "jobGeo": "EMEA", "jobDescription": "<p>LLMs</p>", "pubDate": "2026-09-20 10:00:00"}]}})
    j = fetch_jobicy(http, {"industries": ["data-science"]})[0]
    assert j.location == "Remote (EMEA)" and j.remote


def test_weworkremotely_rss():
    rss = """<?xml version="1.0"?><rss><channel><item><title>Acme: Senior Data Engineer</title>
    <region>Anywhere in the World</region><link>https://weworkremotely.com/remote-jobs/acme-1</link>
    <description>&lt;p&gt;Spark&lt;/p&gt;</description><pubDate>Mon, 21 Sep 2026 10:00:00 +0000</pubDate></item></channel></rss>"""
    j = fetch_weworkremotely(RouteHttp({"weworkremotely.com": rss}), {"feeds": ["remote-jobs"]})[0]
    assert (j.company, j.title, j.posted_at) == ("Acme", "Senior Data Engineer", "2026-09-21")


def test_hn_whoishiring():
    http = RouteHttp({
        "search_by_date": {"hits": [{"title": "Ask HN: Who is hiring? (September 2026)", "objectID": "999"}]},
        "items/999": {"children": [
            {"id": 1, "text": "Acme AI | ML Engineer | Remote (Worldwide) | Full-time<p>We build RAG with PyTorch.",
             "created_at": "2026-09-01T12:00:00Z"},
            {"id": 2, "text": "just a question, no pipes"},
        ]},
    })
    jobs = fetch_hn_whoishiring(http, {})
    assert len(jobs) == 1
    j = jobs[0]
    assert j.company == "Acme AI" and "ML Engineer" in j.title and j.remote
    assert j.apply_url == "https://news.ycombinator.com/item?id=1"
