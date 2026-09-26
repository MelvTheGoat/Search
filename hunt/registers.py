"""UK and Netherlands sponsor registers, downloaded and cached for a week."""
import csv
import io
import json
import re
import time
from datetime import date

from .config import DATA_DIR
from .text import norm

REG_DIR = DATA_DIR / "registers"
UK_PAGE = "https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers"
NL_PAGE = "https://ind.nl/en/public-register-recognised-sponsors/public-register-regular-labour-and-highly-skilled-migrants"
MAX_AGE_DAYS = 7

# Endings that differ between a brand name and a legal name.
SUFFIXES = {
    "ltd", "limited", "plc", "llp", "llc", "inc", "incorporated", "corp", "corporation", "co", "company",
    "bv", "b v", "nv", "n v", "gmbh", "ag", "sa", "sas", "sarl", "ab", "as", "oy", "srl", "spa", "pty",
    "uk", "europe", "emea", "holdings", "holding", "group", "the", "and",
}


def clean_name(name):
    words = [w for w in norm(name).split() if w not in SUFFIXES]
    return " ".join(words)


class Registers:
    def __init__(self, uk_names=(), nl_names=()):
        self.sets = {}
        self.index = {}
        for tag, names in (("UK Register of Licensed Sponsors", uk_names), ("NL IND register of recognised sponsors", nl_names)):
            for raw in names:
                c = clean_name(raw)
                if not c:
                    continue
                self.index.setdefault((tag, c.split()[0]), []).append((c, raw))

    def lookup(self, names):
        """Evidence strings for any register entry that matches one of the names."""
        hits = []
        for name in names:
            c = clean_name(name or "")
            if not c:
                continue
            first = c.split()[0]
            for tag in ("UK Register of Licensed Sponsors", "NL IND register of recognised sponsors"):
                for reg_clean, raw in self.index.get((tag, first), []):
                    # Exact match, or the register name starts with the company
                    # name (for example "Monzo" and "Monzo Bank Limited").
                    if reg_clean == c or (len(c) >= 5 and reg_clean.startswith(c + " ")):
                        hits.append(f"{tag}: \"{raw}\"")
                        break
        return list(dict.fromkeys(hits))[:3]


def _fresh(path):
    return path.exists() and (time.time() - path.stat().st_mtime) < MAX_AGE_DAYS * 86400


def _download_uk(http):
    page = http.get(UK_PAGE, as_json=False)
    m = re.search(r"https://assets\.publishing\.service\.gov\.uk/[^\"'\s]+\.csv", page)
    if not m:
        raise RuntimeError("could not find the UK register CSV link on the gov.uk page")
    text = http.get(m.group(0), as_json=False)
    names = []
    for row in csv.DictReader(io.StringIO(text)):
        route = row.get("Route", "") or ""
        if "worker" in route.lower():
            names.append(row.get("Organisation Name", "").strip())
    return sorted(set(n for n in names if n))


def _download_nl(http):
    page = http.get(NL_PAGE, as_json=False)
    names = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S | re.I):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S | re.I)
        if cells:
            name = re.sub(r"<[^>]+>", "", cells[0]).strip()
            if name and name.lower() not in {"organisation", "organization", "name"}:
                names.append(name)
    return sorted(set(names))


def load_registers(http, log=print):
    """Load both registers, downloading any that are missing or older than a week.
    If a download fails, use the old copy if there is one."""
    REG_DIR.mkdir(parents=True, exist_ok=True)
    result = {}
    for key, fn in (("uk", _download_uk), ("nl", _download_nl)):
        path = REG_DIR / f"{key}_sponsors.json"
        if not _fresh(path):
            try:
                names = fn(http)
                if len(names) < 50:
                    raise RuntimeError(f"only {len(names)} names found, the page format may have changed")
                path.write_text(json.dumps({"fetched": date.today().isoformat(), "names": names}))
                log(f"  {key.upper()} sponsor register: downloaded {len(names)} names")
            except Exception as e:  # noqa: BLE001
                log(f"  {key.upper()} sponsor register: download failed ({e})"
                    + ("; using cached copy" if path.exists() else "; skipping"))
        if path.exists():
            result[key] = json.loads(path.read_text())["names"]
        else:
            result[key] = []
    return Registers(result["uk"], result["nl"])
