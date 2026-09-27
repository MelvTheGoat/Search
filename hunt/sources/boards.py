"""Free public job APIs and feeds. Sources that need a free key (Adzuna,
Reed, Jooble, Findwork) are skipped unless the key is in .env."""
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from ..models import Job
from ..text import html_to_text


def fetch_remoteok(http, cfg, log=print):
    # RemoteOK terms: link back to Remote OK and name it as the source.
    # We keep their job URL as the apply link and store source="remoteok".
    data = http.get("https://remoteok.com/api")
    jobs = []
    for j in data:
        if not isinstance(j, dict) or "position" not in j:
            continue  # the first item is their legal notice
        loc = j.get("location") or "Remote"
        jobs.append(Job(
            source="remoteok",
            company=j.get("company", ""),
            title=j.get("position", ""),
            location=loc if "remote" in loc.lower() else f"Remote ({loc})",
            apply_url=j.get("url") or j.get("apply_url", ""),
            description=html_to_text(j.get("description", "")) + ("\nTags: " + ", ".join(j.get("tags") or [])),
            remote=True,
            posted_at=(j.get("date") or "")[:10],
        ))
    return jobs


def fetch_remotive(http, cfg, log=print):
    jobs = []
    for cat in cfg.get("categories", ["data"]):
        try:
            data = http.get("https://remotive.com/api/remote-jobs", params={"category": cat})
        except Exception as e:  # noqa: BLE001
            log(f"  remotive/{cat}: {e}")
            continue
        for j in data.get("jobs", []):
            where = j.get("candidate_required_location") or ""
            jobs.append(Job(
                source="remotive",
                company=j.get("company_name", ""),
                title=j.get("title", ""),
                location=f"Remote ({where})" if where else "Remote",
                apply_url=j.get("url", ""),
                description=html_to_text(j.get("description", "")),
                remote=True,
                posted_at=(j.get("publication_date") or "")[:10],
                department=j.get("category", ""),
            ))
    return jobs


def fetch_arbeitnow(http, cfg, log=print):
    jobs = []
    url = "https://www.arbeitnow.com/api/job-board-api"
    for _ in range(cfg.get("max_pages", 5)):
        data = http.get(url)
        for j in data.get("data", []):
            created = j.get("created_at")
            loc = j.get("location", "") or ""
            jobs.append(Job(
                source="arbeitnow",
                company=j.get("company_name", ""),
                title=j.get("title", ""),
                location=("Remote, " + loc) if j.get("remote") else loc,
                apply_url=j.get("url", ""),
                description=html_to_text(j.get("description", "")),
                remote=bool(j.get("remote")),
                country="Germany" if not loc else "",
                posted_at=datetime.fromtimestamp(created, timezone.utc).date().isoformat() if created else "",
            ))
        url = (data.get("links") or {}).get("next")
        if not url:
            break
    return jobs


def fetch_himalayas(http, cfg, log=print):
    """Himalayas search API, one query at a time, 20 jobs a page."""
    jobs, seen = [], set()
    for q in cfg.get("queries", ["machine learning"]):
        for page in range(1, cfg.get("max_pages", 10) + 1):
            try:
                data = http.get("https://himalayas.app/jobs/api/search", params={"q": q, "page": page})
            except Exception as e:  # noqa: BLE001
                log(f"  himalayas/{q}/page {page}: {e}")
                break
            batch = data.get("jobs", [])
            for j in batch:
                gid = j.get("guid") or j.get("applicationLink")
                if gid in seen:
                    continue
                seen.add(gid)
                limits = j.get("locationRestrictions") or []
                limits = [l if isinstance(l, str) else l.get("name", "") for l in limits]
                where = ", ".join(l for l in limits if l) or "Worldwide"
                seniority = ", ".join(j.get("seniority") or [])
                jobs.append(Job(
                    source="himalayas",
                    company=j.get("companyName", ""),
                    title=j.get("title", ""),
                    location=f"Remote ({where})",
                    apply_url=j.get("applicationLink") or j.get("guid", ""),
                    description=html_to_text(j.get("description") or j.get("excerpt", ""))
                    + (f"\nSeniority: {seniority}" if seniority else ""),
                    remote=True,
                    posted_at=_himalayas_date(j.get("pubDate")),
                    department=", ".join(j.get("categories") or [])[:200],
                    extra={"location_hints": limits} if limits else {},
                ))
            if len(batch) < 20:
                break
    return jobs


def _himalayas_date(v):
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v, timezone.utc).date().isoformat()
    return (v or "")[:10]


ADZUNA_COUNTRY = {
    "gb": "United Kingdom", "us": "United States", "at": "Austria", "au": "Australia", "be": "Belgium",
    "br": "Brazil", "ca": "Canada", "ch": "Switzerland", "de": "Germany", "es": "Spain", "fr": "France",
    "in": "India", "it": "Italy", "mx": "Mexico", "nl": "Netherlands", "nz": "New Zealand", "pl": "Poland",
    "sg": "Singapore", "za": "South Africa",
}


def adzuna_keys():
    return os.environ.get("ADZUNA_APP_ID", "").strip(), os.environ.get("ADZUNA_APP_KEY", "").strip()


def fetch_adzuna(http, cfg, log=print):
    app_id, app_key = adzuna_keys()
    jobs = []
    for cc in cfg.get("countries", []):
        for q in cfg.get("queries", ["machine learning"]):
            try:
                data = http.get(
                    f"https://api.adzuna.com/v1/api/jobs/{cc}/search/1",
                    params={"app_id": app_id, "app_key": app_key, "what": q,
                            "results_per_page": cfg.get("results_per_page", 50),
                            "max_days_old": cfg.get("max_days_old", 30), "content-type": "application/json"},
                )
            except Exception as e:  # noqa: BLE001
                log(f"  adzuna/{cc}/{q}: {e}")
                continue
            for j in data.get("results", []):
                loc = (j.get("location") or {}).get("display_name", "")
                jobs.append(Job(
                    source="adzuna",
                    company=(j.get("company") or {}).get("display_name", ""),
                    title=html_to_text(j.get("title", "")),
                    location=loc,
                    apply_url=j.get("redirect_url", ""),
                    description=html_to_text(j.get("description", "")),
                    remote="remote" in (loc + j.get("title", "")).lower(),
                    country=ADZUNA_COUNTRY.get(cc, ""),
                    posted_at=(j.get("created") or "")[:10],
                ))
    return jobs


def _rss_date(v):
    try:
        return parsedate_to_datetime(v).date().isoformat()
    except (TypeError, ValueError):
        return ""


def fetch_jobicy(http, cfg, log=print):
    # Jobicy asks for a link back and not to poll too often.
    jobs = []
    for industry in cfg.get("industries", ["data-science", "engineering"]):
        try:
            data = http.get("https://jobicy.com/api/v2/remote-jobs", params={"count": 100, "industry": industry})
        except Exception as e:  # noqa: BLE001
            log(f"  jobicy/{industry}: {e}")
            continue
        for j in data.get("jobs", []):
            geo = j.get("jobGeo") or "Anywhere"
            level = j.get("jobLevel") or ""
            jobs.append(Job(
                source="jobicy",
                company=j.get("companyName", ""),
                title=html_to_text(j.get("jobTitle", "")),
                location=f"Remote ({geo})",
                apply_url=j.get("url", ""),
                description=html_to_text(j.get("jobDescription") or j.get("jobExcerpt", "")) + (f"\nLevel: {level}" if level else ""),
                remote=True,
                posted_at=(j.get("pubDate") or "")[:10],
                extra={"location_hints": [geo]},
            ))
    return jobs


def fetch_workingnomads(http, cfg, log=print):
    data = http.get("https://www.workingnomads.com/api/exposed_jobs/")
    jobs = []
    for j in data or []:
        where = j.get("location") or "Anywhere"
        jobs.append(Job(
            source="workingnomads",
            company=j.get("company_name", ""),
            title=j.get("title", ""),
            location=f"Remote ({where})",
            apply_url=j.get("url", ""),
            description=html_to_text(j.get("description", "")) + ("\nTags: " + j["tags"] if j.get("tags") else ""),
            remote=True,
            posted_at=(j.get("pub_date") or "")[:10],
            department=j.get("category_name", ""),
        ))
    return jobs


def fetch_weworkremotely(http, cfg, log=print):
    """We Work Remotely's official RSS feeds."""
    jobs = []
    for feed in cfg.get("feeds", ["remote-jobs"]):
        url = f"https://weworkremotely.com/{feed}.rss" if feed == "remote-jobs" else f"https://weworkremotely.com/categories/{feed}.rss"
        try:
            text = http.get(url, as_json=False)
            root = ET.fromstring(text.encode("utf-8"))
        except Exception as e:  # noqa: BLE001
            log(f"  weworkremotely/{feed}: {e}")
            continue
        for item in root.iter("item"):
            full = (item.findtext("title") or "").strip()
            company, _, title = full.partition(":")
            if not title:
                company, title = "", full
            region = (item.findtext("region") or "Anywhere").strip()
            jobs.append(Job(
                source="weworkremotely",
                company=company.strip(),
                title=title.strip(),
                location=f"Remote ({region})",
                apply_url=(item.findtext("link") or "").strip(),
                description=html_to_text(item.findtext("description") or ""),
                remote=True,
                posted_at=_rss_date(item.findtext("pubDate")),
                extra={"location_hints": [region]},
            ))
    return jobs


def fetch_hn_whoishiring(http, cfg, log=print):
    """The monthly "Ask HN: Who is hiring?" thread, through the official
    Hacker News search API (Algolia). Each top comment is one company."""
    hits = http.get("https://hn.algolia.com/api/v1/search_by_date",
                    params={"tags": "story,author_whoishiring", "hitsPerPage": 5}).get("hits", [])
    story = next((h for h in hits if "who is hiring" in (h.get("title") or "").lower()), None)
    if not story:
        return []
    thread = http.get(f"https://hn.algolia.com/api/v1/items/{story['objectID']}")
    jobs = []
    for c in thread.get("children", []):
        text = html_to_text(c.get("text") or "")
        if not text:
            continue
        head = text.splitlines()[0]
        parts = [p.strip() for p in re.split(r"\s*\|\s*", head) if p.strip()]
        if len(parts) < 2:
            continue
        company = parts[0][:80]
        rest = parts[1:]
        loc_parts = [p for p in rest if re.search(r"remote|on-?site|hybrid|relocat", p, re.I)
                     or re.search(r"[A-Z][a-z]+,\s*[A-Z]{2}\b|\b(US|UK|EU|USA|Canada|Europe|London|Berlin|NYC|SF)\b", p)]
        role_parts = [p for p in rest if p not in loc_parts]
        jobs.append(Job(
            source="hn_whoishiring",
            company=company,
            title=" / ".join(role_parts)[:150] or head[:150],
            location="; ".join(loc_parts)[:200],
            apply_url=f"https://news.ycombinator.com/item?id={c.get('id')}",
            description=text,
            remote=any(re.search(r"remote", p, re.I) for p in loc_parts),
            posted_at=(c.get("created_at") or "")[:10],
        ))
    return jobs


def fetch_themuse(http, cfg, log=print):
    jobs = []
    params = [("category", c) for c in cfg.get("categories", ["Data and Analytics", "Data Science"])]
    params += [("level", lv) for lv in cfg.get("levels", ["Internship", "Entry Level", "Mid Level"])]
    for page in range(cfg.get("max_pages", 10)):
        data = http.get("https://www.themuse.com/api/public/jobs", params=params + [("page", page)])
        for j in data.get("results", []):
            locs = [l.get("name", "") for l in j.get("locations", [])]
            levels = ", ".join(l.get("name", "") for l in j.get("levels", []))
            jobs.append(Job(
                source="themuse",
                company=(j.get("company") or {}).get("name", ""),
                title=j.get("name", ""),
                location="; ".join(locs),
                apply_url=(j.get("refs") or {}).get("landing_page", ""),
                description=html_to_text(j.get("contents", "")) + (f"\nLevel: {levels}" if levels else ""),
                remote=any("remote" in l.lower() or "flexible" in l.lower() for l in locs),
                posted_at=(j.get("publication_date") or "")[:10],
            ))
        if page + 1 >= data.get("page_count", 0):
            break
    return jobs


def fetch_reed(http, cfg, log=print):
    key = os.environ.get("REED_API_KEY", "").strip()
    jobs = []
    for q in cfg.get("queries", ["machine learning"]):
        data = http.get("https://www.reed.co.uk/api/1.0/search", auth=(key, ""),
                        params={"keywords": q, "resultsToTake": 100})
        for j in data.get("results", []):
            jobs.append(Job(
                source="reed",
                company=j.get("employerName", ""),
                title=j.get("jobTitle", ""),
                location=f"{j.get('locationName', '')}, UK",
                apply_url=j.get("jobUrl", ""),
                description=html_to_text(j.get("jobDescription", "")),
                country="United Kingdom",
                posted_at=_uk_date(j.get("date")),
            ))
    return jobs


def _uk_date(v):
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", v or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


def fetch_jooble(http, cfg, log=print):
    key = os.environ.get("JOOBLE_API_KEY", "").strip()
    jobs = []
    for q in cfg.get("queries", ["machine learning engineer"]):
        for where in cfg.get("locations", [""]):
            try:
                data = http.post(f"https://jooble.org/api/{key}", json_body={"keywords": q, "location": where})
            except Exception as e:  # noqa: BLE001
                log(f"  jooble/{q}/{where}: {e}")
                continue
            for j in data.get("jobs", []):
                loc = j.get("location", "")
                jobs.append(Job(
                    source="jooble",
                    company=j.get("company", ""),
                    title=html_to_text(j.get("title", "")),
                    location=loc,
                    apply_url=j.get("link", ""),
                    description=html_to_text(j.get("snippet", "")),
                    remote="remote" in (loc + j.get("title", "")).lower(),
                    posted_at=(j.get("updated") or "")[:10],
                ))
    return jobs


def fetch_findwork(http, cfg, log=print):
    key = os.environ.get("FINDWORK_API_KEY", "").strip()
    jobs = []
    for q in cfg.get("queries", ["machine learning"]):
        data = http.get("https://findwork.dev/api/jobs/", params={"search": q, "sort_by": "date"},
                        headers={"Authorization": f"Token {key}"})
        for j in data.get("results", []):
            loc = j.get("location") or ("Remote" if j.get("remote") else "")
            jobs.append(Job(
                source="findwork",
                company=j.get("company_name", ""),
                title=j.get("role", ""),
                location=loc,
                apply_url=j.get("url", ""),
                description=html_to_text(j.get("text", "")) + ("\nKeywords: " + ", ".join(j.get("keywords") or [])),
                remote=bool(j.get("remote")),
                posted_at=(j.get("date_posted") or "")[:10],
            ))
    return jobs


# Sources that need a key, and the .env names they need.
NEEDS_KEY = {
    "adzuna": ["ADZUNA_APP_ID", "ADZUNA_APP_KEY"],
    "reed": ["REED_API_KEY"],
    "jooble": ["JOOBLE_API_KEY"],
    "findwork": ["FINDWORK_API_KEY"],
}


def has_keys(name):
    return all(os.environ.get(k, "").strip() for k in NEEDS_KEY.get(name, []))


BOARDS = {
    "remoteok": fetch_remoteok,
    "remotive": fetch_remotive,
    "arbeitnow": fetch_arbeitnow,
    "himalayas": fetch_himalayas,
    "jobicy": fetch_jobicy,
    "workingnomads": fetch_workingnomads,
    "weworkremotely": fetch_weworkremotely,
    "hn_whoishiring": fetch_hn_whoishiring,
    "themuse": fetch_themuse,
    "adzuna": fetch_adzuna,
    "reed": fetch_reed,
    "jooble": fetch_jooble,
    "findwork": fetch_findwork,
}
