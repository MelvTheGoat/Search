"""Parsers for the extra sources, fed with small saved samples."""
from hunt.sources.ats import fetch_bamboohr, fetch_breezy, fetch_workday, fetch_personio, fetch_recruitee, fetch_smartrecruiters, fetch_workable
from hunt.sources.boards import fetch_amazon, fetch_hn_whoishiring, fetch_jobicy, fetch_weworkremotely


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


def test_bamboohr_fetches_details_only_for_kept_titles():
    http = RouteHttp({
        "/careers/7/detail": {"result": {"jobOpening": {
            "jobOpeningShareUrl": "https://co.bamboohr.com/careers/7", "description": "<p>Fraud models in Python.</p>",
            "location": {"city": "Lekki", "state": "Lagos", "addressCountry": "Nigeria"}, "datePosted": "2026-09-20"}}},
        "/careers/list": {"result": [
            {"id": "7", "jobOpeningName": "Data Scientist, Fraud", "location": {"city": "Lekki", "state": "Lagos"},
             "departmentLabel": "Risk", "isRemote": None, "locationType": "0"},
            {"id": "8", "jobOpeningName": "Office Assistant", "location": {"city": "Accra"}},
        ]},
    })
    jobs = fetch_bamboohr(http, {**CO, "ats": "bamboohr"}, keep_title=lambda t: "Data" in t)
    assert len(jobs) == 1
    j = jobs[0]
    assert j.location == "Lekki, Lagos, Nigeria" and j.country == "Nigeria"
    assert "Fraud models" in j.description and j.apply_url.endswith("/careers/7")


def test_bamboohr_missing_board_is_none():
    assert fetch_bamboohr(RouteHttp({}), {**CO, "ats": "bamboohr"}) is None


def test_amazon_reads_country_search():
    http = RouteHttp({"amazon.jobs": {"jobs": [{
        "id_icims": "1", "title": "Data Scientist", "normalized_location": "Cape Town, Western Cape, ZAF",
        "country_code": "ZAF", "job_path": "/en/jobs/1/data-scientist", "posted_date": "September 23, 2026",
        "description": "<p>Build models.</p>", "basic_qualifications": "- Python", "job_category": "Data Science"}]}})
    jobs = fetch_amazon(http, {"countries": ["ZAF"], "queries": ["data"]})
    assert len(jobs) == 1
    j = jobs[0]
    assert j.country == "South Africa" and j.posted_at == "2026-09-23"
    assert j.apply_url == "https://www.amazon.jobs/en/jobs/1/data-scientist" and "Python" in j.description


def test_breezy_reads_job_page_data():
    page = ('<script type="application/ld+json">{"@type":"JobPosting","title":"Data Analyst",'
            '"description":"<p>SQL and Python for fraud.</p>"}</script>')
    http = RouteHttp({
        "/p/1-data-analyst": page,
        "breezy.hr/json": [
            {"name": "Data Analyst", "url": "https://co.breezy.hr/p/1-data-analyst", "published_date": "2026-09-01T00:00:00Z",
             "locations": [{"city": "Nairobi", "country": {"name": "Kenya", "id": "KE"}, "is_remote": False}]},
            {"name": "Chef", "url": "https://co.breezy.hr/p/2-chef", "locations": []},
        ],
    })
    jobs = fetch_breezy(http, {**CO, "ats": "breezy"}, keep_title=lambda t: "Data" in t)
    assert len(jobs) == 1
    j = jobs[0]
    assert j.location == "Nairobi, Kenya" and j.country == "Kenya" and "SQL and Python" in j.description


def test_workday_searches_and_reads_details():
    class WD(RouteHttp):
        def post(self, url, json_body=None, **kw):
            if json_body["searchText"] == "data" and json_body["offset"] == 0:
                return {"total": 2, "jobPostings": [
                    {"title": "Data Scientist", "externalPath": "/job/Johannesburg/Data-Scientist_R-1"},
                    {"title": "Universal Banker", "externalPath": "/job/Nairobi/Universal-Banker_R-2"}]}
            return {"total": 0, "jobPostings": []}
    http = WD({"/job/Johannesburg/Data-Scientist_R-1": {"jobPostingInfo": {
        "title": "Data Scientist", "jobDescription": "<p>Credit models in Python.</p>", "location": "Johannesburg",
        "country": {"descriptor": "South Africa"}, "startDate": "2026-09-01", "remoteType": "Hybrid",
        "externalUrl": "https://absa.wd3.myworkdayjobs.com/site/job/Johannesburg/Data-Scientist_R-1"}}})
    jobs = fetch_workday(http, {**CO, "ats": "workday", "token": "absa/wd3/site", "queries": ["data"]},
                         keep_title=lambda t: "Data" in t)
    assert len(jobs) == 1
    j = jobs[0]
    assert j.location == "Johannesburg, South Africa" and j.country == "South Africa"
    assert "Credit models" in j.description and j.apply_url.endswith("Data-Scientist_R-1")


def test_h1b_parse_counts_only_the_same_company():
    from hunt.h1b import parse
    row = ("<tr><td><a href='x'>{e}</a></td><td><a>DATA SCIENTIST</a></td><td><a>1</a></td>"
           "<td><a>SF, CA</a></td><td class='d-sm-none'>06/08/{y}</td><td class='d-sm-none'>10/01/{y}</td></tr>")
    html = (row.format(e="GLEAN TECHNOLOGIES INC", y=2025) + row.format(e="GLEAN ANALYTICS INC", y=2022)
            + row.format(e="GLEAN TECHNOLOGIES INC", y=2023))
    assert parse(html, "Glean") == (2, 2025)
