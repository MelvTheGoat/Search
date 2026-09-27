"""Small text helpers."""
import hashlib
import html
import re
import unicodedata

_BLOCK_TAGS = re.compile(r"<\s*(br|p|/p|div|/div|/li|h\d|/h\d|/tr|/ul|/ol)\b[^>]*>", re.I)
_LI_TAG = re.compile(r"<\s*li\b[^>]*>", re.I)
_TAG = re.compile(r"<[^>]+>")


def html_to_text(raw):
    """Turn HTML (maybe entity-escaped) into plain text with line breaks."""
    if not raw:
        return ""
    # Greenhouse escapes its HTML once, so unescape first to get real tags.
    text = html.unescape(raw)
    text = _BLOCK_TAGS.sub("\n", text)
    text = _LI_TAG.sub("\n- ", text)
    text = _TAG.sub(" ", text)
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    out, blank = [], False
    for line in lines:
        if not line:
            if not blank and out:
                out.append("")
            blank = True
            continue
        out.append(line)
        blank = False
    return "\n".join(out).strip()


def fix_mojibake(s):
    """Repair UTF-8 text that was decoded as Latin-1, like "MecÃ¡nico"."""
    if s and ("Ã" in s or "â€" in s):
        try:
            return s.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return s
    return s


def norm(s):
    """Lowercase, strip accents and punctuation, squeeze spaces."""
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return s.strip()


def sha(s, n=16):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:n]


def slug(s, max_len=40):
    s = norm(s).replace(" ", "-")
    return s[:max_len].strip("-") or "x"


def sentences(text):
    """Split text into sentences and lines."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text or "")
    return [p.strip(" -•*\t") for p in parts if p and p.strip(" -•*\t")]
