"""Startup sources.

Two parts:

1. fetch_yc reads the Y Combinator job board (ycombinator.com/jobs). Its
   pages carry each job as data, including the visa rule and the minimum
   years, so it works like any other job board.

2. discover() builds config/startups.yaml, a list of startups and their job
   boards (Greenhouse, Ashby, Lever or Workable), from startup lists:
   the a16z portfolio jobs board, the Breakout List, Next Play and the
   Ramp vendor directory. The daily run then reads those boards like the
   ones in companies.yaml and tags each job with where the startup came
   from. Discovery runs again when the file is more than a week old.

Lenny's Jobs and Founders You Should Know are not used because this
environment's network blocks them, and Cosign needs a login.
"""
import html as htmllib
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from urllib.parse import unquote

import yaml

from ..config import CONFIG_DIR
from ..http import Http
from ..models import Job
from ..text import html_to_text, norm

YC = "https://www.ycombinator.com"
# Each YC list page shows about 40 jobs, so read several views of the board.
YC_PAGES = [
    "/jobs/role/software-engineer",
    "/jobs/role/software-engineer/remote",
    "/jobs/role/software-engineer/san-francisco",
    "/jobs/role/software-engineer/new-york",
    "/jobs/role/software-engineer/seattle",
    "/jobs/role/software-engineer/boston",
    "/jobs/role/software-engineer/austin",
    "/jobs/role/software-engineer/los-angeles",
    "/jobs/role/software-engineer/chicago",
    "/jobs/role/software-engineer/india",
    "/jobs/role/science",
    "/jobs/role/science/remote",
    "/jobs/role/operations",
    "/jobs/role/operations/remote",
]

STARTUPS_FILE = CONFIG_DIR / "startups.yaml"
STALE_DAYS = 7

# a16z portfolio areas worth reading, and the biggest companies left out
# (they are not startups any more and many are in companies.yaml already).
A16Z_MARKETS = {"AI", "Fintech", "Crypto/Web3", "Enterprise"}
A16Z_BIG = {"1K-5K", "5K-10K", "10000+", "5000-10000"}

# Job board links found on a careers page or in an apply link.
ATS_LINKS = [
    ("greenhouse", re.compile(r"(?:boards|job-boards)(?:\.eu)?\.greenhouse\.io/(?:embed/job_board\?for=)?([A-Za-z0-9_-]+)")),
    ("ashby", re.compile(r"jobs\.ashbyhq\.com/([A-Za-z0-9_.%-]+)")),
    ("lever", re.compile(r"jobs\.lever\.co/([A-Za-z0-9_.-]+)")),
    ("workable", re.compile(r"apply\.workable\.com/([A-Za-z0-9_-]+)")),
]
NOT_TOKENS = {"embed", "api", "v1", "jobs", "j", "careers", "static", "assets"}


def _page_data(text):
    """The data-page JSON that YC pages carry."""
    m = re.search(r'data-page="([^"]+)"', text or "")
    return json.loads(htmllib.unescape(m.group(1)))["props"] if m else {}


def _next_payload(text):
    """The text a Next.js page streams to the browser (a16z, Next Play)."""
    parts = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', text or "", re.S)
    out = []
    for p in parts:
        try:
            out.append(json.loads('"' + p + '"'))
        except ValueError:
            continue
    return "".join(out)


def _yc_description(job):
    """Description text with the YC fields the labeller and scorer read."""
    lines = []
    visa = job.get("visa") or ""
    if visa == "US citizen/visa only":
        lines.append("Work authorization required: US citizen or existing US visa only.")
    elif visa == "Will sponsor":
        lines.append("Visa sponsorship available.")
    elif visa:
        lines.append(f"Visa: {visa}.")
    exp = job.get("minExperience") or ""
    if exp and "new grads" in exp.lower():
        lines.append("Experience: new grads welcome.")
    elif exp:
        lines.append(f"Experience: {exp} of experience.")
    if job.get("skills"):
        lines.append("Skills: " + ", ".join(job["skills"]) + ".")
    if job.get("salaryRange"):
        lines.append("Salary: " + job["salaryRange"] + ".")
    if job.get("companyOneLiner"):
        lines.append(f"{job.get('companyName')}: {job['companyOneLiner']}.")
    body = html_to_text(job.get("description") or "")
    return "\n".join(lines + ([body] if body else []))


def _yc_job(p):
    batch = p.get("companyBatchName") or ""
    loc = p.get("location") or ""
    return Job(
        source="yc",
        company=p.get("companyName") or "",
        title=p.get("title") or "",
        location=loc,
        apply_url=YC + (p.get("url") or ""),
        description=_yc_description(p),
        remote="remote" in loc.lower(),
        department=p.get("roleSpecificType") or p.get("prettyRole") or "",
        extra={"startup": f"YC {batch}".strip()},
    )


def fetch_yc(http, cfg, log=print, keep_title=None):
    """Jobs from the YC job board. A job's page is read only when its title
    passes keep_title, to keep the number of calls small."""
    if keep_title is None:
        keep_title = _title_filter()
    seen = {}
    for path in cfg.get("pages", YC_PAGES):
        try:
            props = _page_data(http.get(YC + path, as_json=False))
        except Exception as e:  # noqa: BLE001
            log(f"  yc: {path} failed ({e})")
            continue
        for p in props.get("jobPostings", []):
            if p.get("url") and p["url"] not in seen:
                seen[p["url"]] = p
    jobs = []
    for url, p in seen.items():
        if keep_title and not keep_title(p.get("title") or ""):
            continue
        try:
            full = _page_data(http.get(YC + url, as_json=False)).get("job") or {}
        except Exception:  # noqa: BLE001
            full = {}
        jobs.append(_yc_job({**p, **{k: v for k, v in full.items() if v}}))
    log(f"  yc: {len(seen)} jobs listed, {len(jobs)} kept")
    return jobs


def _title_filter():
    from ..config import load_yaml
    f = load_yaml("scoring.yaml")["filter"]
    return lambda t: (not any(re.search(p, t, re.I) for p in f["drop_titles"])
                      and any(re.search(p, t, re.I) for p in f["keep_titles"]))


# --- discovery -----------------------------------------------------------

def _domain(url):
    m = re.match(r"(?:https?://)?(?:www\.)?([^/?#]+)", (url or "").strip().lower())
    return m.group(1) if m else ""


def a16z_companies(http, log=print):
    """Startups in the a16z portfolio, with their job board taken from
    the apply links on each company's page of jobs.a16z.com."""
    text = _next_payload(http.get("https://jobs.a16z.com/companies", as_json=False))
    i = text.find('"companies":[')
    if i < 0:
        log("  a16z: company list not found")
        return []
    arr, _ = json.JSONDecoder().raw_decode(text[i + len('"companies":'):])
    out = []
    for c in arr:
        if not c.get("jobCount") or c.get("employeeBand") in A16Z_BIG:
            continue
        if not A16Z_MARKETS & set(c.get("markets") or []):
            continue
        out.append({"name": c["name"], "domain": c.get("domain") or "", "a16z_slug": c.get("slug"),
                    "source": "a16z", "note": ", ".join(c.get("markets") or [])})
    log(f"  a16z: {len(out)} startups in AI, fintech, crypto and enterprise")
    return out


def a16z_board(http, slug):
    """(ats, token) from the apply links on a company's a16z jobs page."""
    text = _next_payload(http.get(f"https://jobs.a16z.com/jobs/{slug}", as_json=False))
    for url in re.findall(r'"apply_url":"(https://[^"]+)"', text):
        found = ats_from_text(url)
        if found:
            return found
    return None


def breakout_companies(http, log=print):
    """The Breakout List (breakoutlist.com): startups picked by investors."""
    page = http.get("https://breakoutlist.com/", as_json=False)
    out = []
    # The page lists every company as structured data (schema.org ItemList).
    for block in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', page, re.S):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        for node in data if isinstance(data, list) else data.get("@graph", [data]):
            if node.get("@type") != "ItemList":
                continue
            for el in node.get("itemListElement", []):
                org = el.get("item") or {}
                if org.get("name"):
                    out.append({"name": org["name"], "domain": _domain(org.get("url")), "source": "Breakout List"})
    out = _unique(out)
    log(f"  breakout list: {len(out)} startups")
    return out


def nextplay_companies(http, log=print):
    """Startups hiring through Next Play (nextplay.so), from its jobs and
    companies pages. Logos name each company and its website."""
    out = []
    for path in ("/jobs", "/companies"):
        try:
            text = _next_payload(http.get("https://nextplay.so" + path, as_json=False))
        except Exception as e:  # noqa: BLE001
            log(f"  next play: {path} failed ({e})")
            continue
        for dom, name in re.findall(r'img\.logo\.dev/([a-z0-9.-]+)\?[^"]*","alt":"([^"]+)"', text):
            if dom in {"ashbyhq.com", "greenhouse.io", "lever.co"}:
                continue
            out.append({"name": name, "domain": dom, "source": "Next Play"})
    out = _unique(out)
    log(f"  next play: {len(out)} startups")
    return out


def ramp_vendors(http, log=print):
    """Fast-growing AI vendors from Ramp's vendor directory (ramp.com/vendors),
    which ranks software by real company spending."""
    out = []
    home = http.get("https://ramp.com/vendors", as_json=False)
    cats = sorted(set(re.findall(r'href="(/vendors/categories/[a-z0-9-]+)"', home)))
    for cat in [c for c in cats if "ai" in c.split("/")[-1].split("-")]:
        try:
            page = http.get("https://ramp.com" + cat, as_json=False)
        except Exception:  # noqa: BLE001
            continue
        for slug in set(re.findall(r'href="/vendors/([a-z0-9-]+)"', page)):
            if slug != "categories":
                out.append({"name": slug.replace("-", " ").title(), "domain": "", "source": "Ramp", "slug": slug})
    out = _unique(out)
    log(f"  ramp: {len(out)} AI vendors")
    return out


def _unique(items):
    seen, out = set(), []
    for it in items:
        k = it.get("domain") or norm(it["name"])
        if k and k not in seen:
            seen.add(k)
            out.append(it)
    return out


def ats_from_text(text):
    """First job board link in a page or URL, as (ats, token)."""
    for ats, pat in ATS_LINKS:
        for tok in pat.findall(text or ""):
            tok = unquote(tok.strip(".").split("?")[0])
            if tok and tok.lower() not in NOT_TOKENS:
                return ats, tok
    return None


def _tokens(item):
    """Board names to try when a site does not link its board."""
    name = re.sub(r"[^a-z0-9 ]", "", item["name"].lower())
    stem = (item.get("domain") or "").split(".")[0]
    cands = [name.replace(" ", ""), name.replace(" ", "-"), stem, item.get("slug") or ""]
    out = []
    for c in cands:
        if len(c) >= 4 and c not in out:
            out.append(c)
    return out


def _board_ok(http, ats, token, name):
    """True when the board exists, has jobs and (where the ATS says it)
    belongs to this company."""
    try:
        if ats == "greenhouse":
            info = http.get(f"https://boards-api.greenhouse.io/v1/boards/{token}", missing_ok=True)
            if not info or norm(name)[:6] not in norm(info.get("name") or ""):
                return False
            jobs = http.get(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs", missing_ok=True)
            return bool(jobs and jobs.get("jobs"))
        if ats == "ashby":
            data = http.get(f"https://api.ashbyhq.com/posting-api/job-board/{token}", missing_ok=True)
            return bool(data and data.get("jobs"))
        if ats == "lever":
            data = http.get(f"https://api.lever.co/v0/postings/{token}", params={"mode": "json", "limit": 1},
                            missing_ok=True)
            return bool(data)
    except Exception:  # noqa: BLE001
        return False
    return False


def resolve(http, item):
    """Find a startup's job board: the a16z apply links, then links on its
    own site, then common board names."""
    if item.get("a16z_slug"):
        try:
            found = a16z_board(http, item["a16z_slug"])
        except Exception:  # noqa: BLE001
            found = None
        if found:
            return found
    dom = item.get("domain")
    if dom:
        for path in ("/careers", "/jobs", "/"):
            try:
                page = http.get(f"https://{dom}{path}", as_json=False, missing_ok=True)
            except Exception:  # noqa: BLE001
                page = None
            found = ats_from_text(page or "")
            if found:
                return found
    # Guessing a board name is only safe when it is the company's own name.
    for tok in _tokens(item):
        for ats in ("ashby", "greenhouse", "lever"):
            if _board_ok(http, ats, tok, item["name"]):
                return ats, tok
    return None


def known_boards():
    from ..pipeline import load_companies
    return {(c["ats"], c["token"].lower()): c["name"] for c in load_companies(startups=False)}


def discover(http, log=print, lists=None, workers=8):
    """Build config/startups.yaml. Returns the number of startups with a board."""
    lists = lists or [a16z_companies, breakout_companies, nextplay_companies, ramp_vendors]
    items = []
    for fn in lists:
        try:
            items += fn(http, log=log)
        except Exception as e:  # noqa: BLE001
            log(f"  {fn.__name__}: failed ({e})")
    # One entry per company, keeping every list that named it.
    merged = {}
    for it in items:
        k = norm(it["name"])
        if k in merged:
            if it["source"] not in merged[k]["sources"]:
                merged[k]["sources"].append(it["source"])
            for f in ("domain", "a16z_slug"):
                merged[k][f] = merged[k].get(f) or it.get(f)
        else:
            merged[k] = {**it, "sources": [it["source"]]}
    known = known_boards()
    known_names = {norm(n) for n in known.values()}
    # Company sites are many different hosts, so check several at once with
    # short timeouts: a site that does not answer is skipped, not retried.
    fast = Http(min_interval=0.3, per_host=getattr(http, "per_host", {}), retries=1, backoff=1.0, timeout=10) \
        if isinstance(http, Http) else http
    todo = [it for it in merged.values() if norm(it["name"]) not in known_names]
    boards, done = {}, 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(resolve, fast, it): norm(it["name"]) for it in todo}
        for fut in as_completed(futures):
            try:
                boards[futures[fut]] = fut.result()
            except Exception:  # noqa: BLE001
                boards[futures[fut]] = None
            done += 1
            if done % 50 == 0:
                log(f"  {done}/{len(todo)} startups checked")
    found, missing = [], []
    for it in merged.values():
        entry = {"name": it["name"], "sources": it["sources"]}
        if it.get("domain"):
            entry["domain"] = it["domain"]
        if norm(it["name"]) in known_names:
            # Already read through companies.yaml; only tag it.
            found.append({**entry, "in_companies": True})
            continue
        board = boards.get(norm(it["name"]))
        if board and board[0] in ("greenhouse", "ashby", "lever", "workable"):
            entry.update(ats=board[0], token=board[1])
            if (board[0], board[1].lower()) in known:
                entry["in_companies"] = True
            found.append(entry)
        else:
            missing.append(entry)
    STARTUPS_FILE.write_text(
        "# Startups found by `python hunt.py startups` from the a16z jobs board,\n"
        "# the Breakout List, Next Play and the Ramp vendor directory.\n"
        "# Made by the tool; it is rebuilt every week, so edit companies.yaml instead.\n"
        + yaml.safe_dump({"updated": date.today().isoformat(), "startups": found, "no_board_found": missing},
                         sort_keys=False, allow_unicode=True, width=200))
    log(f"Startups: {len(found)} with a job board, {len(missing)} without one found")
    return len(found)


def load_startups():
    if not STARTUPS_FILE.exists():
        return {}
    return yaml.safe_load(STARTUPS_FILE.read_text()) or {}


def stale():
    data = load_startups()
    try:
        age = (date.today() - date.fromisoformat(str(data.get("updated")))).days
    except (TypeError, ValueError):
        return True
    return age >= STALE_DAYS


def startup_names():
    """Normalised company name -> label like "a16z, Breakout List"."""
    out = {}
    for s in load_startups().get("startups", []):
        out[norm(s["name"])] = ", ".join(s.get("sources", []))
    return out
