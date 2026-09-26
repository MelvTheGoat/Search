"""Check every board in companies.yaml. If a token is dead on its ATS, try
the same token on the other two. Dead ones move to companies_removed.yaml.

companies.yaml keeps one company per line, so this rewrite keeps your
comments and order."""
import re
from datetime import date

from .config import CONFIG_DIR, load_yaml
from .http import HttpError
from .pipeline import make_http
from .sources.ats import fetch_company

LINE = re.compile(r"^\s*-\s*\{.*\btoken:\s*([^,}\s]+).*\}\s*$")


def _probe(http, company):
    """Return ("ok", count), ("missing", 0) or ("error", message)."""
    try:
        jobs = fetch_company(http, company)
    except HttpError as e:
        msg = str(e)
        if re.search(r"HTTP (400|404|410)", msg):
            return "missing", 0
        return "error", msg
    if jobs is None:
        return "missing", 0
    return "ok", len(jobs)


def verify_companies(write=True, log=print):
    cfg = load_yaml("sources.yaml")
    http = make_http(cfg)
    http.retries = 1
    companies = load_yaml("companies.yaml").get("companies", [])
    results = {}
    for i, c in enumerate(companies, start=1):
        outcomes = {c["ats"]: _probe(http, c)}
        state, value = outcomes[c["ats"]]
        switched = None
        if not (state == "ok" and value > 0):
            for other in ("greenhouse", "lever", "ashby"):
                if other == c["ats"]:
                    continue
                outcomes[other] = _probe(http, {**c, "ats": other})
                if outcomes[other][0] == "ok" and outcomes[other][1] > 0:
                    switched = other
                    break
        if state == "ok" and value > 0:
            verdict, note = "live", f"{value} jobs"
        elif switched:
            verdict, note = "live", f"{outcomes[switched][1]} jobs on {switched} (was {c['ats']})"
        elif state == "ok":
            verdict, note = "empty", "board exists but has no jobs today"
        elif all(o[0] == "missing" for o in outcomes.values()):
            verdict, note = "dead", "not found on greenhouse, lever or ashby"
        else:
            errs = [o[1] for o in outcomes.values() if o[0] == "error"]
            verdict, note = "error", errs[0][:100] if errs else "unknown error"
        results[(c["ats"], c["token"])] = (verdict, switched, note)
        log(f"  [{i}/{len(companies)}] {c['name'][:28]:28} {c['ats']}/{c['token']}: {verdict}, {note}")

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
