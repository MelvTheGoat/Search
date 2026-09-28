"""HTTP client with a clear User-Agent, polite rate limits and retries."""
import random
import threading
import time
from urllib.parse import urlparse

import requests

USER_AGENT = (
    "personal-job-hunt/1.0 (one person's job search, not a scraper; "
    "contact: mlvyn.t@gmail.com)"
)

RETRY_CODES = {429, 500, 502, 503, 504}
LIMITED_AFTER = 2  # requests that still got 429 after every retry


class HttpError(Exception):
    pass


def site_of(host):
    """The site a host belongs to, so "acme.jobs.personio.de" and
    "beta.jobs.personio.de" share one rate limit: "personio.de"."""
    parts = host.lower().split(":")[0].split(".")
    if len(parts) >= 3 and parts[-2] in {"co", "com", "gov", "org", "ac"}:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


class Http:
    def __init__(self, min_interval=1.0, per_host=None, retries=4, backoff=2.0, timeout=30):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json, text/html;q=0.9"})
        self.min_interval = min_interval
        self.per_host = per_host or {}
        self.retries = retries
        self.backoff = backoff
        self.timeout = timeout
        self._last = {}
        self._lock = threading.Lock()
        # Sites that kept answering "too many requests"; skipped for the rest
        # of the run so one busy site cannot stall every board after it.
        self._limited = {}

    def _wait(self, host):
        # The lock keeps the pace per site even when threads share a client.
        host = site_of(host)
        with self._lock:
            gap = self.per_host.get(host, self.min_interval)
            wait = gap - (time.time() - self._last.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            self._last[host] = time.time()

    def get(self, url, params=None, as_json=True, missing_ok=False, headers=None, auth=None, allow_redirects=True):
        """GET a URL. Returns None on 404 when missing_ok is set, and on a
        redirect when allow_redirects is False (some boards redirect when a
        company is missing)."""
        return self.request("GET", url, params=params, as_json=as_json, missing_ok=missing_ok,
                            headers=headers, auth=auth, allow_redirects=allow_redirects)

    def post(self, url, json_body=None, as_json=True, headers=None):
        return self.request("POST", url, json_body=json_body, as_json=as_json, headers=headers)

    def request(self, method, url, params=None, json_body=None, as_json=True, missing_ok=False,
                headers=None, auth=None, allow_redirects=True):
        host = urlparse(url).netloc
        if self._limited.get(site_of(host), 0) >= LIMITED_AFTER:
            raise HttpError(f"{url}: skipped, {site_of(host)} is rate-limiting this run")
        error = None
        for attempt in range(self.retries + 1):
            self._wait(host)
            try:
                r = self.session.request(method, url, params=params, json=json_body, headers=headers,
                                         auth=auth, timeout=self.timeout, allow_redirects=allow_redirects)
            except requests.RequestException as e:
                error = HttpError(f"{url}: {e}")
            else:
                if missing_ok and (r.status_code == 404 or (not allow_redirects and 300 <= r.status_code < 400)):
                    return None
                if r.status_code in RETRY_CODES:
                    error = HttpError(f"{url}: HTTP {r.status_code}")
                    retry_after = r.headers.get("Retry-After", "")
                    if r.status_code == 429 and attempt == self.retries:
                        with self._lock:
                            self._limited[site_of(host)] = self._limited.get(site_of(host), 0) + 1
                    if retry_after.isdigit() and attempt < self.retries:
                        time.sleep(min(int(retry_after), 120))
                        continue
                elif r.status_code >= 400:
                    raise HttpError(f"{url}: HTTP {r.status_code}")
                else:
                    if not as_json:
                        return r.text
                    try:
                        return r.json()
                    except ValueError:
                        raise HttpError(f"{url}: response is not JSON")
            if attempt < self.retries:
                time.sleep(self.backoff * (2 ** attempt) + random.random())
        raise error
