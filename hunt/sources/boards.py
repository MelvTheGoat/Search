"""Free public job APIs: RemoteOK, Remotive, Arbeitnow, Himalayas and Adzuna."""
import os
from datetime import datetime, timezone

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
    jobs = []
    limit = 20
    for page in range(cfg.get("max_pages", 20)):
        data = http.get("https://himalayas.app/jobs/api", params={"limit": limit, "offset": page * limit})
        batch = data.get("jobs", [])
        for j in batch:
            limits = j.get("locationRestrictions") or []
            limits = [l if isinstance(l, str) else l.get("name", "") for l in limits]
            where = ", ".join(l for l in limits if l) or "Worldwide"
            jobs.append(Job(
                source="himalayas",
                company=j.get("companyName", ""),
                title=j.get("title", ""),
                location=f"Remote ({where})",
                apply_url=j.get("applicationLink") or j.get("guid", ""),
                description=html_to_text(j.get("description") or j.get("excerpt", "")),
                remote=True,
                posted_at=_himalayas_date(j.get("pubDate")),
                department=", ".join(j.get("categories") or [])[:200],
                extra={"location_hints": limits} if limits else {},
            ))
        if len(batch) < limit:
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


BOARDS = {
    "remoteok": fetch_remoteok,
    "remotive": fetch_remotive,
    "arbeitnow": fetch_arbeitnow,
    "himalayas": fetch_himalayas,
    "adzuna": fetch_adzuna,
}
