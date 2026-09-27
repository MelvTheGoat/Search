"""Company job boards: Greenhouse, Lever, Ashby, SmartRecruiters, Workable,
Recruitee, Personio, BambooHR and Breezy. All are the companies' own public job feeds."""
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from ..countries import ISO_TO_COUNTRY
from ..models import Job
from ..text import html_to_text

GREENHOUSE = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
LEVER = "https://api.lever.co/v0/postings/{token}?mode=json"
LEVER_EU = "https://api.eu.lever.co/v0/postings/{token}?mode=json"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=false"
SMARTRECRUITERS = "https://api.smartrecruiters.com/v1/companies/{token}/postings"
WORKABLE = "https://apply.workable.com/api/v1/widget/accounts/{token}?details=true"
RECRUITEE = "https://{token}.recruitee.com/api/offers/"
PERSONIO = "https://{token}.jobs.personio.de/xml?language=en"
BAMBOOHR = "https://{token}.bamboohr.com/careers"
BREEZY = "https://{token}.breezy.hr/json"
_LD_JSON = re.compile(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', re.S)


def _extra(company):
    return {k: company[k] for k in ("known_sponsor", "aliases", "sector") if company.get(k)}


def fetch_greenhouse(http, company, keep_title=None):
    data = http.get(GREENHOUSE.format(token=company["token"]), missing_ok=True)
    if data is None:
        return None
    jobs = []
    for j in data.get("jobs", []):
        loc = (j.get("location") or {}).get("name", "") or ""
        offices = [o.get("location") or o.get("name") or "" for o in j.get("offices", [])]
        extra = _extra(company)
        if offices:
            extra["location_hints"] = [o for o in offices if o and o != loc]
        jobs.append(Job(
            source="greenhouse",
            company=company["name"],
            title=j.get("title", "").strip(),
            location=loc,
            apply_url=j.get("absolute_url", ""),
            description=html_to_text(j.get("content", "")),
            remote="remote" in loc.lower(),
            posted_at=(j.get("updated_at") or "")[:10],
            department=", ".join(d.get("name", "") for d in j.get("departments", [])),
            extra=extra,
        ))
    return jobs


def fetch_lever(http, company, keep_title=None):
    url = (LEVER_EU if company.get("region") == "eu" else LEVER).format(token=company["token"])
    data = http.get(url, missing_ok=True)
    if data is None or isinstance(data, dict):
        return None
    jobs = []
    for j in data:
        cats = j.get("categories") or {}
        loc = cats.get("location", "") or ""
        all_locs = cats.get("allLocations") or []
        parts = [j.get("descriptionPlain") or html_to_text(j.get("description", ""))]
        for block in j.get("lists", []):
            parts.append(f"{block.get('text', '')}\n{html_to_text(block.get('content', ''))}")
        parts.append(j.get("additionalPlain") or html_to_text(j.get("additional", "")))
        extra = _extra(company)
        hints = [l for l in all_locs if l and l != loc]
        if hints:
            extra["location_hints"] = hints
        created = j.get("createdAt")
        jobs.append(Job(
            source="lever",
            company=company["name"],
            title=(j.get("text") or "").strip(),
            location=loc,
            apply_url=j.get("hostedUrl") or j.get("applyUrl", ""),
            description="\n\n".join(p for p in parts if p).strip(),
            remote=(j.get("workplaceType") == "remote") or "remote" in loc.lower(),
            country=ISO_TO_COUNTRY.get((j.get("country") or "").upper(), ""),
            posted_at=datetime.fromtimestamp(created / 1000, timezone.utc).date().isoformat() if created else "",
            department=cats.get("team", "") or cats.get("department", "") or "",
            extra=extra,
        ))
    return jobs


def fetch_ashby(http, company, keep_title=None):
    data = http.get(ASHBY.format(token=company["token"]), missing_ok=True)
    if data is None:
        return None
    jobs = []
    for j in data.get("jobs", []):
        if j.get("isListed") is False:
            continue
        loc = j.get("location", "") or ""
        hints = [s.get("location", "") for s in j.get("secondaryLocations", []) if s.get("location")]
        addr = ((j.get("address") or {}).get("postalAddress") or {})
        if addr.get("addressCountry"):
            hints.append(addr["addressCountry"])
        extra = _extra(company)
        if hints:
            extra["location_hints"] = hints
        jobs.append(Job(
            source="ashby",
            company=company["name"],
            title=(j.get("title") or "").strip(),
            location=loc,
            apply_url=j.get("jobUrl") or j.get("applyUrl", ""),
            description=j.get("descriptionPlain") or html_to_text(j.get("descriptionHtml", "")),
            remote=bool(j.get("isRemote")) or (j.get("workplaceType") or "").lower() == "remote",
            posted_at=(j.get("publishedAt") or "")[:10],
            department=j.get("department", "") or j.get("team", "") or "",
            extra=extra,
        ))
    return jobs


def fetch_smartrecruiters(http, company, keep_title=None):
    """The list has no descriptions, so we fetch details only for titles
    that pass keep_title, to keep the number of calls low."""
    token = company["token"]
    items, offset = [], 0
    while True:
        data = http.get(SMARTRECRUITERS.format(token=token), params={"limit": 100, "offset": offset}, missing_ok=True)
        if data is None:
            return None if offset == 0 else items
        batch = data.get("content", [])
        items += batch
        offset += len(batch)
        if not batch or offset >= data.get("totalFound", 0) or offset >= 1000:
            break
    jobs = []
    for j in items:
        title = (j.get("name") or "").strip()
        if keep_title and not keep_title(title):
            continue
        loc = j.get("location") or {}
        place = loc.get("fullLocation") or ", ".join(x for x in (loc.get("city"), loc.get("region"), (loc.get("country") or "").upper()) if x)
        desc = ""
        try:
            detail = http.get(f"{SMARTRECRUITERS.format(token=token)}/{j['id']}")
            sections = ((detail or {}).get("jobAd") or {}).get("sections") or {}
            desc = "\n\n".join(html_to_text((sections.get(k) or {}).get("text", ""))
                               for k in ("jobDescription", "qualifications", "additionalInformation", "companyDescription"))
        except Exception:  # noqa: BLE001
            pass
        jobs.append(Job(
            source="smartrecruiters",
            company=company["name"],
            title=title,
            location=("Remote, " + place) if loc.get("remote") else place,
            apply_url=f"https://jobs.smartrecruiters.com/{token}/{j['id']}",
            description=desc.strip() + (f"\nExperience level: {(j.get('experienceLevel') or {}).get('label', '')}"),
            remote=bool(loc.get("remote")),
            country=ISO_TO_COUNTRY.get((loc.get("country") or "").upper(), ""),
            posted_at=(j.get("releasedDate") or "")[:10],
            department=(j.get("department") or {}).get("label", "") or "",
            extra=_extra(company),
        ))
    return jobs


def fetch_workable(http, company, keep_title=None):
    data = http.get(WORKABLE.format(token=company["token"]), missing_ok=True)
    if data is None or "jobs" not in data:
        return None
    jobs = []
    for j in data["jobs"]:
        locs = j.get("locations") or [{"city": j.get("city"), "region": j.get("state"), "country": j.get("country")}]
        places = [", ".join(x for x in (l.get("city"), l.get("region"), l.get("country")) if x) for l in locs if not l.get("hidden")]
        places = [p for p in places if p]
        remote = bool(j.get("telecommuting"))
        loc = "; ".join(places) or ("Remote" if remote else "")
        extra = _extra(company)
        jobs.append(Job(
            source="workable",
            company=company["name"],
            title=(j.get("title") or "").strip(),
            location=("Remote, " + loc) if remote and "remote" not in loc.lower() else loc,
            apply_url=j.get("url") or j.get("shortlink") or j.get("application_url", ""),
            description=html_to_text(j.get("description", "")) + (f"\nExperience: {j['experience']}" if j.get("experience") else ""),
            remote=remote,
            posted_at=(j.get("published_on") or j.get("created_at") or "")[:10],
            department=j.get("department", "") or "",
            extra=extra,
        ))
    return jobs


def fetch_recruitee(http, company, keep_title=None):
    data = http.get(RECRUITEE.format(token=company["token"]), missing_ok=True)
    if data is None or "offers" not in data:
        return None
    jobs = []
    for j in data["offers"]:
        loc = j.get("location") or ", ".join(x for x in (j.get("city"), j.get("country")) if x)
        remote = bool(j.get("remote"))
        jobs.append(Job(
            source="recruitee",
            company=company["name"],
            title=(j.get("title") or "").strip(),
            location=("Remote, " + loc) if remote and "remote" not in loc.lower() else loc,
            apply_url=j.get("careers_url", ""),
            description=(html_to_text(j.get("description", "")) + "\n\n" + html_to_text(j.get("requirements", ""))).strip(),
            remote=remote,
            country=ISO_TO_COUNTRY.get((j.get("country_code") or "").upper(), ""),
            posted_at=(j.get("published_at") or "")[:10],
            department=j.get("department", "") or "",
            extra=_extra(company),
        ))
    return jobs


def fetch_personio(http, company, keep_title=None):
    text = http.get(PERSONIO.format(token=company["token"]), as_json=False, missing_ok=True)
    if text is None or "<workzag-jobs" not in text:
        return None
    root = ET.fromstring(text.encode("utf-8"))
    jobs = []
    for pos in root.findall("position"):
        def t(tag):
            el = pos.find(tag)
            return (el.text or "").strip() if el is not None and el.text else ""
        offices = [t("office")] + [(o.text or "").strip() for o in pos.findall("additionalOffices/office")]
        offices = [o for o in offices if o]
        parts = []
        for d in pos.findall("jobDescriptions/jobDescription"):
            name = (d.findtext("name") or "").strip()
            parts.append(f"{name}\n{html_to_text(d.findtext('value') or '')}")
        seniority = t("seniority")
        loc = "; ".join(offices)
        jobs.append(Job(
            source="personio",
            company=company["name"],
            title=t("name"),
            location=loc,
            apply_url=f"https://{company['token']}.jobs.personio.de/job/{t('id')}",
            description="\n\n".join(parts) + (f"\nSeniority: {seniority}" if seniority else ""),
            remote=bool(re.search(r"remote", loc, re.I)),
            posted_at=t("createdAt")[:10],
            department=t("department"),
            extra=_extra(company),
        ))
    return jobs


def fetch_bamboohr(http, company, keep_title=None):
    """BambooHR lists jobs without descriptions, so like SmartRecruiters we
    fetch details only for titles that pass keep_title."""
    base = BAMBOOHR.format(token=company["token"])
    # A missing BambooHR site redirects instead of returning 404.
    data = http.get(f"{base}/list", missing_ok=True, allow_redirects=False)
    if not isinstance(data, dict) or "result" not in data:
        return None
    jobs = []
    for j in data["result"]:
        title = (j.get("jobOpeningName") or "").strip()
        if keep_title and not keep_title(title):
            continue
        detail = {}
        try:
            detail = ((http.get(f"{base}/{j['id']}/detail") or {}).get("result") or {}).get("jobOpening") or {}
        except Exception:  # noqa: BLE001
            pass
        where = detail.get("location") or j.get("location") or {}
        place = ", ".join(x for x in (where.get("city"), where.get("state"), where.get("addressCountry"))
                          if x and x.strip(" ."))
        if not place:
            # Some boards fill only the ATS location (often just a country).
            ats_loc = detail.get("atsLocation") or j.get("atsLocation") or {}
            place = ", ".join(x for x in (ats_loc.get("city"), ats_loc.get("state"), ats_loc.get("country")) if x)
            where = {**where, "addressCountry": where.get("addressCountry") or ats_loc.get("country")}
        remote = bool(j.get("isRemote")) or j.get("locationType") == "1"
        jobs.append(Job(
            source="bamboohr",
            company=company["name"],
            title=title,
            location=("Remote, " + place) if remote else place,
            apply_url=detail.get("jobOpeningShareUrl") or f"{base}/{j['id']}",
            description=html_to_text(detail.get("description", "")),
            remote=remote,
            country=where.get("addressCountry") or "",
            posted_at=(detail.get("datePosted") or "")[:10],
            department=j.get("departmentLabel", "") or "",
            extra=_extra(company),
        ))
    return jobs


def _job_posting_ld(html):
    """The schema.org JobPosting block a job page publishes for search engines."""
    import json
    for block in _LD_JSON.findall(html or ""):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        if isinstance(data, dict) and data.get("@type") == "JobPosting":
            return data
    return {}


def fetch_breezy(http, company, keep_title=None):
    """Breezy lists jobs without descriptions. For titles that pass
    keep_title we read the JobPosting data on the job's own page."""
    data = http.get(BREEZY.format(token=company["token"]), missing_ok=True, allow_redirects=False)
    if not isinstance(data, list):
        return None
    jobs = []
    for j in data:
        title = (j.get("name") or "").strip()
        if keep_title and not keep_title(title):
            continue
        locs = j.get("locations") or [j.get("location") or {}]
        places = [", ".join(x for x in (l.get("city"), (l.get("country") or {}).get("name")) if x) for l in locs]
        places = [p for p in places if p]
        remote = any(l.get("is_remote") for l in locs)
        loc = "; ".join(places) or ("Remote" if remote else "")
        desc = ""
        try:
            desc = html_to_text(_job_posting_ld(http.get(j["url"], as_json=False)).get("description", ""))
        except Exception:  # noqa: BLE001
            pass
        country = ((locs[0] if locs else {}).get("country") or {}).get("id", "")
        jobs.append(Job(
            source="breezy",
            company=company["name"],
            title=title,
            location=("Remote, " + loc) if remote and "remote" not in loc.lower() else loc,
            apply_url=j.get("url", ""),
            description=desc,
            remote=remote,
            country=ISO_TO_COUNTRY.get(country.upper(), ""),
            posted_at=(j.get("published_date") or "")[:10],
            department=j.get("department") or "",
            extra=_extra(company),
        ))
    return jobs


FETCHERS = {
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
    "smartrecruiters": fetch_smartrecruiters,
    "workable": fetch_workable,
    "recruitee": fetch_recruitee,
    "personio": fetch_personio,
    "bamboohr": fetch_bamboohr,
    "breezy": fetch_breezy,
}
ATS_NAMES = list(FETCHERS)


def fetch_company(http, company, keep_title=None):
    """Jobs for one companies.yaml entry. None means the board was not found."""
    return FETCHERS[company["ats"]](http, company, keep_title=keep_title)
