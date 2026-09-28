"""Which jobs are within reach.

A job is out of reach when any of these hold. Such jobs stay in the
database, so they do not come back as new, but they are left out of the
page, the tracker and the letter queue.

- restricted: the post rules you out (no sponsorship, right to work,
  citizens only, remote for one country, clearance)
- abroad with no sign of sponsorship: the post says nothing, and the
  company is not on the UK or NL sponsor register or known for US H-1B
  filings
- a senior level, or a post that asks for MAX_YEARS or more years
- for current students only
- needs a Master's degree or a PhD
"""
import re

from .scoring import required_years
from .text import sentences

MAX_YEARS = 5
OK_LABELS = {"remote_open", "nigeria", "africa", "sponsor_yes", "sponsor_likely"}
SENIOR = {"senior", "lead", "staff", "principal", "manager"}

_STUDENT = re.compile(
    r"currently (enrolled|pursuing)|current(ly)? (a )?(full-time )?(university )?student|enrolled (full-time )?in a"
    r"|returning to (school|university)|graduating (in|between|by|before)|expected graduation|penultimate year"
    r"|must be (a )?(current )?student|pursuing a (bachelor|master|phd|degree)", re.I)
_HIGH_DEGREE = re.compile(r"\b(ph\.?\s?d|doctorate|master'?s|master degree|m\.?sc?\b|m\.s\.|advanced degree|graduate degree)", re.I)
_LOW_DEGREE = re.compile(r"\b(bachelor|b\.?sc?\b|b\.s\.|b\.a\.|undergraduate|or equivalent)", re.I)
_SOFT = re.compile(r"prefer|plus\b|bonus|nice to have|ideally|advantage|desirable|not required|welcome", re.I)
_NEED = re.compile(r"require|must|minimum|you have|you hold|hold a|degree in|in (computer|machine|statistics|math|a related|a quantitative)", re.I)


def needs_high_degree(text):
    """The sentence that asks for a Master's or PhD as a must, if any."""
    for s in sentences(text or ""):
        if _HIGH_DEGREE.search(s) and _NEED.search(s) and not _LOW_DEGREE.search(s) and not _SOFT.search(s):
            return s
    return None


def out_of_reach(job):
    """A short reason when the job is out of reach, else None. `job` is a
    database row (dict)."""
    label = job.get("location_label")
    if label == "restricted":
        return "restricted: " + (job.get("restriction") or "the post rules you out")[:120]
    if label not in OK_LABELS:
        return "abroad, and no sign the company sponsors visas"
    if (job.get("level") or "") in SENIOR:
        return f"{job['level']} role"
    text = job.get("description") or ""
    years = required_years(text)
    if years and years >= MAX_YEARS:
        return f"asks for {years}+ years"
    if _STUDENT.search(text):
        return "for current students only"
    s = needs_high_degree(text)
    if s:
        return "needs a Master's or PhD: " + s[:100]
    return None


def within_reach(job):
    return out_of_reach(job) is None
