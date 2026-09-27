"""US H-1B sponsorship history, from the public Department of Labor filings
as listed on h1bdata.info. One lookup per company, cached for 30 days.

A company counts as a US sponsor when it has at least MIN_FILINGS H-1B
filings under its own name, with at least one in the last three years."""
import json
import re
import time
from datetime import date
from urllib.parse import quote_plus

from .config import DATA_DIR
from .registers import GENERIC, clean_name

CACHE = DATA_DIR / "registers" / "us_h1b.json"
URL = "https://h1bdata.info/index.php?em={name}&job=&city=&year=all+years"
MAX_AGE_DAYS = 30
MIN_FILINGS = 5
_ROW = re.compile(r"<tr><td><a [^>]*>([^<]+)</a></td>.*?<td class=[\"']d-sm-none[\"']>(\d\d)/(\d\d)/(\d{4})</td>", re.S)


def same_company(employer, company):
    """True if the filing's employer is the company, allowing legal endings
    and generic words ("Glean Technologies Inc" for "Glean")."""
    e, c = clean_name(employer), clean_name(company)
    if not c:
        return False
    if e == c:
        return True
    if e.startswith(c + " "):
        return all(w in GENERIC for w in e[len(c):].split())
    return False


def parse(html, company):
    """(filings under this company's name, latest filing year)."""
    count, latest = 0, 0
    for employer, _m, _d, year in _ROW.findall(html or ""):
        if same_company(employer, company):
            count += 1
            latest = max(latest, int(year))
    return count, latest


class H1B:
    def __init__(self, http=None, log=print):
        self.http = http
        self.log = log
        try:
            self.cache = json.loads(CACHE.read_text())
        except (OSError, ValueError):
            self.cache = {}

    def _save(self):
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(self.cache))

    def record(self, company):
        key = clean_name(company)
        if not key:
            return None
        hit = self.cache.get(key)
        if hit and time.time() - hit.get("at", 0) < MAX_AGE_DAYS * 86400:
            return hit
        if self.http is None:
            return hit
        try:
            html = self.http.get(URL.format(name=quote_plus(key.upper())), as_json=False)
        except Exception as e:  # noqa: BLE001
            self.log(f"  H-1B lookup for {company} failed ({e})")
            return hit
        count, latest = parse(html, company)
        hit = {"filings": count, "latest": latest, "at": time.time()}
        self.cache[key] = hit
        self._save()
        return hit

    def lookup(self, company):
        """Evidence strings if the company usually sponsors H-1B visas."""
        hit = self.record(company)
        if not hit or hit["filings"] < MIN_FILINGS or hit["latest"] < date.today().year - 3:
            return []
        return [f"US H-1B filings: {hit['filings']} under this name (latest {hit['latest']})"]
