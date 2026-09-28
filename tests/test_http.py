from hunt.http import site_of


def test_subdomains_share_one_site():
    assert site_of("acme.jobs.personio.de") == site_of("beta.jobs.personio.de") == "personio.de"
    assert site_of("api.eu.lever.co") == "lever.co"
    assert site_of("www.reed.co.uk") == "reed.co.uk"


def test_a_rate_limiting_site_is_skipped_for_the_rest_of_the_run():
    from hunt.http import Http, HttpError

    class Resp:
        status_code, headers = 429, {}

    http = Http(min_interval=0, retries=1, backoff=0)
    calls = []
    http.session.request = lambda *a, **k: calls.append(a[1]) or Resp()
    for n in range(3):
        try:
            http.get(f"https://apply.workable.com/api/{n}")
        except HttpError:
            pass
    assert len(calls) == 4  # two boards tried twice each, the third skipped
    http.session.request = lambda *a, **k: calls.append(a[1]) or Resp()
    try:
        http.get("https://boards-api.greenhouse.io/x")
    except HttpError:
        pass
    assert len(calls) == 6  # other sites are still tried
