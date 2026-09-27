from hunt.http import site_of


def test_subdomains_share_one_site():
    assert site_of("acme.jobs.personio.de") == site_of("beta.jobs.personio.de") == "personio.de"
    assert site_of("api.eu.lever.co") == "lever.co"
    assert site_of("www.reed.co.uk") == "reed.co.uk"
