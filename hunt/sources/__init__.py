"""Job sources. Each one returns a list of Job objects."""
import json
import time

from ..config import DATA_DIR

CACHE_DIR = DATA_DIR / "cache"


def cached(name, hours, fetch, log=print):
    """Run fetch() at most once every `hours`, else reuse the saved result.
    Used for aggregators with strict rate limits."""
    from ..models import Job
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{name}.json"
    if path.exists() and time.time() - path.stat().st_mtime < hours * 3600:
        log(f"  {name}: using cache (fetched less than {hours}h ago)")
        return [Job(**d) for d in json.loads(path.read_text())]
    jobs = fetch()
    if not jobs:
        return jobs  # do not cache a failed or empty fetch
    path.write_text(json.dumps([j.__dict__ for j in jobs]))
    return jobs
