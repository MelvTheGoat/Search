"""Checks letter files: no dashes, no banned phrases, no numbers that are not
in the CV, right length, and the right sign-off."""
import re
from dataclasses import dataclass
from pathlib import Path

from .config import CV_PATH, LETTERS_DIR, load_yaml

NUM = re.compile(r"\d+(?:[.,]\d+)*")
URL = re.compile(r"https?://\S+|www\.\S+|\S+@\S+")


@dataclass
class Problem:
    file: str
    line: int
    kind: str
    message: str

    def __str__(self):
        return f"{self.file}:{self.line}: [{self.kind}] {self.message}"


def _numbers(text):
    """Numbers as floats, so "0.40" and "0.4" or "2,000" and "2000" match."""
    out = set()
    for m in NUM.finditer(URL.sub(" ", text)):
        raw = m.group(0).replace(",", "")
        try:
            out.add(float(raw))
        except ValueError:
            pass
    return out


def split_front_matter(lines):
    """Return the index of the first body line (after a --- block)."""
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return i + 1
    return 0


def letter_section(lines, start):
    """Line numbers of the cover letter section (from '## Cover letter' to the next '## ')."""
    begin = None
    for i in range(start, len(lines)):
        if lines[i].lower().startswith("## cover letter"):
            begin = i + 1
        elif begin is not None and lines[i].startswith("## "):
            return begin, i
    return (begin, len(lines)) if begin is not None else (None, None)


def check_file(path, cv_numbers, rules):
    problems = []
    name = str(path)
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    body_start = split_front_matter(lines)
    dashes = rules["dash_chars"]
    banned = [(p, re.compile(r"(?<![a-z])" + re.escape(p.lower()) + r"(?![a-z])")) for p in rules["banned_phrases"]]

    for n, line in enumerate(lines, start=1):
        for ch in dashes:
            if ch in line:
                problems.append(Problem(name, n, "dash", f"dash character {ch!r} (U+{ord(ch):04X}); use a comma, full stop or 'and'"))
        if n <= body_start:
            continue
        text = line.strip()
        if re.search(r"\S\s+-{1,2}\s+\S", text) or "--" in text:
            problems.append(Problem(name, n, "dash", "hyphen used as a dash; use a comma, full stop or 'and'"))
        low = line.lower()
        for phrase, pat in banned:
            if pat.search(low):
                problems.append(Problem(name, n, "banned", f"banned phrase \"{phrase}\""))
        for num in sorted(_numbers(line)):
            if num not in cv_numbers:
                shown = int(num) if num == int(num) else num
                problems.append(Problem(name, n, "number", f"number {shown} is not in profile/cv.md"))

    start, end = letter_section(lines, body_start)
    if start is None:
        problems.append(Problem(name, body_start + 1, "format", "no '## Cover letter' section found"))
    else:
        body = [l for l in lines[start:end] if l.strip()]
        words = len(" ".join(body).split())
        lo, hi = rules.get("letter_words", [150, 250])
        if not lo <= words <= hi:
            problems.append(Problem(name, start, "length", f"cover letter is {words} words; keep it between {lo} and {hi}"))
        email = rules.get("sign_off_email")
        if email and not any(email in l for l in body[-4:]):
            problems.append(Problem(name, end, "sign-off", f"sign off with the name and {email}"))
    return problems


def check_all(paths=None, cv_path=CV_PATH, rules=None):
    rules = rules or load_yaml("writing.yaml")
    cv_numbers = _numbers(Path(cv_path).read_text(encoding="utf-8"))
    paths = paths if paths is not None else sorted(LETTERS_DIR.glob("*.md"))
    problems = []
    for p in paths:
        problems += check_file(p, cv_numbers, rules)
    return problems, len(paths)
