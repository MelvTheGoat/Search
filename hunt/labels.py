"""Location labels and sponsorship signals.

Labels, best first:
  remote_open      remote and open to Nigeria, Africa, EMEA or worldwide
  nigeria          onsite or hybrid in Nigeria
  sponsor_yes      abroad, and the post offers sponsorship or relocation
  sponsor_likely   abroad, and the company is a known visa sponsor
  sponsor_unknown  abroad, and the post says nothing about sponsorship
  restricted       no sponsorship, needs existing right to work, remote for
                   one country only, or needs citizenship or clearance
"""
import re
from dataclasses import dataclass, field

from .config import load_yaml
from .countries import OPEN_REGIONS, OTHER_REGIONS, find_countries, has_city, has_region
from .text import sentences

HOME = "Nigeria"


@dataclass
class LabelResult:
    label: str
    country: str = ""
    restriction: str = ""        # exact sentence that restricts the job
    sponsorship: str = "unknown"  # yes / likely / no / not needed / unknown
    evidence: list = field(default_factory=list)


class Labeller:
    def __init__(self, phrases=None, registers=None):
        phrases = phrases or load_yaml("sponsorship.yaml")
        self.patterns = {
            kind: [re.compile(p, re.I) for p in phrases.get(kind, [])]
            for kind in ("no_sponsorship", "right_to_work", "citizenship", "clearance", "location_only", "positive")
        }
        self.registers = registers  # object with .lookup(names) -> list of evidence strings

    # --- text scanning -------------------------------------------------
    def scan(self, text):
        """Return {kind: [sentence, ...]} for every phrase found."""
        found = {k: [] for k in self.patterns}
        for sent in sentences(text):
            neg_hit = False
            for kind in ("no_sponsorship", "right_to_work", "citizenship", "clearance", "location_only"):
                if any(p.search(sent) for p in self.patterns[kind]):
                    if kind == "clearance" and re.search(r"clearance (is )?not required|no clearance", sent, re.I):
                        continue
                    found[kind].append(sent)
                    neg_hit = True
            # A sentence that says "we cannot sponsor" is never a positive signal.
            if not neg_hit and any(p.search(sent) for p in self.patterns["positive"]):
                found["positive"].append(sent)
        return found

    # --- main entry ----------------------------------------------------
    def label(self, job):
        loc = job.location or ""
        hints = " ; ".join(job.extra.get("location_hints", []))
        where = f"{loc} ; {hints}" if hints else loc
        countries = find_countries(where)
        if job.country and job.country not in countries:
            countries.insert(0, job.country)
        is_remote = bool(job.remote) or bool(re.search(r"\bremote\b|\banywhere\b|work from home|\bwfh\b", where, re.I))
        in_nigeria = HOME in countries
        abroad = [c for c in countries if c != HOME]
        country = HOME if in_nigeria else (abroad[0] if abroad else ("Remote" if is_remote else ""))

        found = self.scan(f"{job.title}\n{job.description}")
        hard = found["right_to_work"] + found["citizenship"] + found["clearance"] + found["location_only"]
        no_sponsor = found["no_sponsorship"]
        positive = found["positive"]
        evidence = [f"post: \"{s}\"" for s in positive[:2]]

        # 1. Onsite or hybrid in Nigeria. No visa needed.
        if in_nigeria and not is_remote:
            return LabelResult("nigeria", HOME, sponsorship="not needed", evidence=["job is in Nigeria"])

        # 2. Remote jobs.
        if is_remote:
            open_scope = in_nigeria or has_region(where, OPEN_REGIONS)
            other_region = has_region(where, OTHER_REGIONS)
            if hard:
                return self._restricted(country, hard[0])
            if open_scope:
                return LabelResult("remote_open", country, sponsorship="not needed",
                                   evidence=[f"remote, location: \"{where.strip(' ;')}\""])
            onsite_option = has_city(loc) or re.search(r"hybrid|on-?site|office", loc, re.I)
            if len(abroad) == 1 and not other_region and not onsite_option:
                return self._restricted(country, f"Location: {loc or hints}", note="remote for one country only")
            if not abroad and not other_region and not onsite_option:
                # Plain "Remote" with no country named.
                if no_sponsor:
                    return self._restricted(country, no_sponsor[0])
                return LabelResult("remote_open", country, sponsorship="not needed",
                                   evidence=["remote, no country limit named in the post"])
            # Remote for a group of countries that does not include Nigeria,
            # or remote with an office option abroad: treat it like a job abroad.

        # 3. Jobs abroad.
        if hard or no_sponsor:
            return self._restricted(country, (hard + no_sponsor)[0])
        if positive:
            return LabelResult("sponsor_yes", country, sponsorship="yes", evidence=evidence)
        register_hits = self._known_sponsor(job)
        if register_hits:
            return LabelResult("sponsor_likely", country, sponsorship="likely", evidence=register_hits)
        return LabelResult("sponsor_unknown", country, sponsorship="unknown",
                           evidence=["post does not mention sponsorship"])

    def _restricted(self, country, sentence, note=""):
        ev = [f"restricts: \"{sentence}\""] + ([note] if note else [])
        return LabelResult("restricted", country, restriction=sentence, sponsorship="no", evidence=ev)

    def _known_sponsor(self, job):
        hits = []
        known = job.extra.get("known_sponsor")
        if known:
            hits.append("companies.yaml: " + (known if isinstance(known, str) else "known visa sponsor"))
        if self.registers is not None:
            names = [job.company, *job.extra.get("aliases", [])]
            hits += self.registers.lookup(names)
        return hits
