"""Company job boards on Greenhouse, Lever and Ashby."""
from datetime import datetime, timezone

from ..countries import ISO_TO_COUNTRY
from ..models import Job
from ..text import html_to_text

GREENHOUSE = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
LEVER = "https://api.lever.co/v0/postings/{token}?mode=json"
LEVER_EU = "https://api.eu.lever.co/v0/postings/{token}?mode=json"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=false"


def _extra(company):
    return {k: company[k] for k in ("known_sponsor", "aliases", "sector") if company.get(k)}


def fetch_greenhouse(http, company):
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


def fetch_lever(http, company):
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


def fetch_ashby(http, company):
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


FETCHERS = {"greenhouse": fetch_greenhouse, "lever": fetch_lever, "ashby": fetch_ashby}


def fetch_company(http, company):
    """Jobs for one companies.yaml entry. None means the board was not found."""
    return FETCHERS[company["ats"]](http, company)
