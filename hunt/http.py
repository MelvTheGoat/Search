"""HTTP client with a clear User-Agent, polite rate limits and retries."""
import random
import time
from urllib.parse import urlparse

import requests

USER_AGENT = (
    "personal-job-hunt/1.0 (one person's job search, not a scraper; "
    "contact: mayungboluwatobi@gmail.com)"
)

RETRY_CODES = {429, 500, 502, 503, 504}


class HttpError(Exception):
    pass


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

    def _wait(self, host):
        gap = self.per_host.get(host, self.min_interval)
        wait = gap - (time.time() - self._last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        self._last[host] = time.time()

    def get(self, url, params=None, as_json=True, missing_ok=False, headers=None, auth=None):
        """GET a URL. Returns None on 404 when missing_ok is set."""
        return self.request("GET", url, params=params, as_json=as_json, missing_ok=missing_ok,
                            headers=headers, auth=auth)

    def post(self, url, json_body=None, as_json=True, headers=None):
        return self.request("POST", url, json_body=json_body, as_json=as_json, headers=headers)

    def request(self, method, url, params=None, json_body=None, as_json=True, missing_ok=False,
                headers=None, auth=None):
        host = urlparse(url).netloc
        error = None
        for attempt in range(self.retries + 1):
            self._wait(host)
            try:
                r = self.session.request(method, url, params=params, json=json_body, headers=headers,
                                         auth=auth, timeout=self.timeout)
            except requests.RequestException as e:
                error = HttpError(f"{url}: {e}")
            else:
                if r.status_code == 404 and missing_ok:
                    return None
                if r.status_code in RETRY_CODES:
                    error = HttpError(f"{url}: HTTP {r.status_code}")
                    retry_after = r.headers.get("Retry-After", "")
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
