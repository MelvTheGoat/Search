"""Check every board in companies.yaml. If a token is dead on its ATS, try
the same token on the other supported ATSs. Dead ones move to companies_removed.yaml.

companies.yaml keeps one company per line, so this rewrite keeps your
comments and order."""
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from .config import CONFIG_DIR, load_yaml
from .http import HttpError
from .pipeline import make_http
from .sources.ats import ATS_NAMES, SMARTRECRUITERS, fetch_company

LINE = re.compile(r"^\s*-\s*\{.*\btoken:\s*([^,}\s]+).*\}\s*$")


def _probe(http, company):
    """Return ("ok", count), ("missing", 0) or ("error", message)."""
    try:
        if company["ats"] == "smartrecruiters":
            # Count from the list only, to skip one call per job.
            data = http.get(SMARTRECRUITERS.format(token=company["token"]), params={"limit": 1}, missing_ok=True)
            # An unknown SmartRecruiters id returns an empty list, not a 404.
            found = int((data or {}).get("totalFound", 0))
            return ("ok", found) if found else ("missing", 0)
        if company["ats"] == "greenhouse":
            # Without content=true the list is small and fast.
            data = http.get(f"https://boards-api.greenhouse.io/v1/boards/{company['token']}/jobs", missing_ok=True)
            return ("missing", 0) if data is None else ("ok", len(data.get("jobs", [])))
        jobs = fetch_company(http, company)
    except HttpError as e:
        msg = str(e)
        if re.search(r"HTTP (400|404|410)", msg):
            return "missing", 0
        return "error", msg
    if jobs is None:
        return "missing", 0
    return "ok", len(jobs)


ALTERNATES = ["greenhouse", "lever", "ashby"]


def _check(clients, c):
    """Check one company: its own ATS first, then the others."""
    # Alternates are only tried on the big, fast boards. Workable, Personio
    # and the rest rate-limit hard, so they are only checked for their own
    # companies.
    order = [c["ats"]] + [a for a in ALTERNATES if a != c["ats"]]
    outcomes = {}
    switched = None
    for ats in order:
        outcomes[ats] = _probe(clients[ats], {**c, "ats": ats})
        state, value = outcomes[ats]
        if state == "ok" and value > 0:
            switched = None if ats == c["ats"] else ats
            break
        if ats == c["ats"] and state == "error":
            break  # network trouble: do not guess, keep it as it is
    own_state, own_value = outcomes[c["ats"]]
    if own_state == "ok" and own_value > 0:
        return "live", None, f"{own_value} jobs"
    if switched:
        return "live", switched, f"{outcomes[switched][1]} jobs on {switched} (was {c['ats']})"
    if own_state == "ok":
        return "empty", None, "board exists but has no jobs today"
    if all(o[0] == "missing" for o in outcomes.values()):
        return "dead", None, "not found on any supported ATS"
    errs = [o[1] for o in outcomes.values() if o[0] == "error"]
    return "error", None, (errs[0][:100] if errs else "unknown error")


def verify_companies(write=True, log=print):
    cfg = load_yaml("sources.yaml")
    companies = load_yaml("companies.yaml").get("companies", [])
    # One HTTP client per ATS, so each site keeps its own polite pace.
    # Companies are split by their ATS and checked side by side.
    clients = {}
    for ats in ATS_NAMES:
        clients[ats] = make_http(cfg)
        clients[ats].retries = 2
    results = {}
    by_ats = {a: [c for c in companies if c["ats"] == a] for a in ATS_NAMES}
    done = [0]

    def work(ats):
        for c in by_ats[ats]:
            verdict, switched, note = _check(clients, c)
            results[(c["ats"], c["token"])] = (verdict, switched, note)
            done[0] += 1
            log(f"  [{done[0]}/{len(companies)}] {c['name'][:28]:28} {c['ats']}/{c['token']}: {verdict}, {note}")

    with ThreadPoolExecutor(max_workers=len(ATS_NAMES)) as pool:
        list(pool.map(work, ATS_NAMES))

    count = {v: sum(1 for r in results.values() if r[0] == v) for v in ("live", "empty", "dead", "error")}
    log(f"\n{count['live']} live, {count['empty']} empty, {count['dead']} dead, {count['error']} errors.")
    if count["error"] > len(companies) * 0.3:
        log("Many boards failed with network errors, so nothing was removed. Check your connection and try again.")
        return results
    if not write:
        return results

    path = CONFIG_DIR / "companies.yaml"
    kept, removed = [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = LINE.match(line)
        if not m:
            kept.append(line)
            continue
        ats = re.search(r"\bats:\s*(\w+)", line).group(1)
        verdict, switched, note = results.get((ats, m.group(1)), ("live", None, ""))
        if verdict == "dead":
            removed.append(line.strip() + f"  # removed {date.today()}: {note}")
            continue
        if switched:
            line = re.sub(r"\bats:\s*\w+", f"ats: {switched}", line)
        kept.append(line)
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    if removed:
        rpath = CONFIG_DIR / "companies_removed.yaml"
        old = rpath.read_text(encoding="utf-8") if rpath.exists() else (
            "# Boards that stopped working. Fix the token and move a line back to companies.yaml to retry.\n")
        rpath.write_text(old + "\n".join(removed) + "\n", encoding="utf-8")
    log(f"Updated companies.yaml: removed {len(removed)}, kept {len(companies) - len(removed)}.")
    return results
