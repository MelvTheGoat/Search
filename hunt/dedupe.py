"""Remove duplicate jobs by apply URL and by company + title + location."""


def dedupe(jobs):
    """Keep the first copy of each job. A job is a duplicate if its apply URL
    or its company/title/location hash was already seen. When two copies
    exist, the one with the longer description wins, so ATS copies beat short
    aggregator snippets."""
    by_key = {}
    url_to_key = {}
    order = []
    for job in jobs:
        key = job.key
        url = job.url_key
        found = key if key in by_key else url_to_key.get(url) if url else None
        if found is None:
            by_key[key] = job
            order.append(key)
            if url:
                url_to_key[url] = key
            continue
        kept = by_key[found]
        if len(job.description or "") > len(kept.description or ""):
            by_key[found] = job
        if url and url not in url_to_key:
            url_to_key[url] = found
    return [by_key[k] for k in order]
