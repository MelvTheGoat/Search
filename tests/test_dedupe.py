from hunt.dedupe import dedupe
from hunt.models import Job


def job(**kw):
    base = dict(source="greenhouse", company="Acme", title="ML Engineer", location="London, UK",
                apply_url="https://boards.greenhouse.io/acme/jobs/1", description="short")
    base.update(kw)
    return Job(**base)


def test_same_url_is_a_duplicate():
    a = job()
    b = job(title="Machine Learning Engineer", apply_url="https://boards.greenhouse.io/acme/jobs/1?gh_src=abc&utm_source=x")
    assert len(dedupe([a, b])) == 1


def test_same_company_title_location_is_a_duplicate():
    a = job(source="remoteok", apply_url="https://remoteok.com/1")
    b = job(source="greenhouse", apply_url="https://boards.greenhouse.io/acme/jobs/9", company="ACME", title="ml engineer")
    assert len(dedupe([a, b])) == 1


def test_longer_description_wins():
    a = job(source="adzuna", apply_url="https://adzuna/1", description="snippet")
    b = job(source="greenhouse", description="a much longer full description of the job")
    out = dedupe([a, b])
    assert len(out) == 1 and out[0].source == "greenhouse"


def test_different_jobs_are_kept():
    a = job()
    b = job(title="Data Scientist", apply_url="https://boards.greenhouse.io/acme/jobs/2")
    c = job(location="Lagos, Nigeria", apply_url="https://boards.greenhouse.io/acme/jobs/3")
    assert len(dedupe([a, b, c])) == 3
