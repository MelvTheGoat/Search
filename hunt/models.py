"""The one job schema every source is turned into."""
from dataclasses import dataclass, field

from .text import norm, sha


@dataclass
class Job:
    source: str
    company: str
    title: str
    location: str
    apply_url: str
    description: str = ""
    remote: bool = False
    country: str = ""            # filled by the labeller if the source does not give it
    posted_at: str = ""
    department: str = ""
    # Extra hints from the source, like Himalayas location limits or
    # the companies.yaml entry (known sponsor, aliases).
    extra: dict = field(default_factory=dict)

    @property
    def key(self):
        """Stable id from company, title and location."""
        return sha(f"{norm(self.company)}|{norm(self.title)}|{norm(self.location)}")

    @property
    def url_key(self):
        return normalize_url(self.apply_url)


def normalize_url(url):
    """Drop tracking bits so the same posting gives the same URL."""
    if not url:
        return ""
    url = url.strip()
    base, _, query = url.partition("?")
    keep = []
    for part in query.split("&"):
        name = part.split("=")[0].lower()
        if part and not name.startswith("utm_") and name not in {"source", "ref", "gh_src", "lever-source", "src"}:
            keep.append(part)
    base = base.rstrip("/").lower().replace("http://", "https://")
    return base + ("?" + "&".join(sorted(keep)) if keep else "")
