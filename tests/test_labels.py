import pytest

from hunt.labels import Labeller
from hunt.models import Job
from hunt.registers import Registers


@pytest.fixture
def labeller():
    regs = Registers(uk_names=["Monzo Bank Limited"], nl_names=["Adyen N.V."])
    return Labeller(registers=regs)


def job(location, description="We build ML systems.", remote=False, company="Acme", **extra):
    return Job(source="greenhouse", company=company, title="ML Engineer", location=location,
               apply_url="https://x/1", description=description, remote=remote, extra=extra)


def test_remote_worldwide_is_open(labeller):
    assert labeller.label(job("Remote - Worldwide")).label == "remote_open"


def test_remote_emea_and_africa_are_open(labeller):
    assert labeller.label(job("Remote (EMEA)")).label == "remote_open"
    assert labeller.label(job("Remote, Africa")).label == "remote_open"


def test_remote_nigeria_is_open(labeller):
    assert labeller.label(job("Remote - Nigeria")).label == "remote_open"


def test_onsite_nigeria(labeller):
    r = labeller.label(job("Lagos, Nigeria"))
    assert r.label == "nigeria" and r.country == "Nigeria"


def test_nigeria_ignores_no_sponsorship_line(labeller):
    r = labeller.label(job("Lagos", "We are unable to sponsor visas for this role."))
    assert r.label == "nigeria"


def test_remote_one_country_is_restricted(labeller):
    r = labeller.label(job("Remote - US"))
    assert r.label == "restricted"
    assert "Remote - US" in r.restriction


def test_no_sponsorship_abroad_is_restricted_with_quote(labeller):
    text = "Great team. We are unable to sponsor visas for this position. Apply now."
    r = labeller.label(job("London, UK", text, company="Monzo"))
    assert r.label == "restricted"
    assert r.restriction == "We are unable to sponsor visas for this position."


def test_right_to_work_restricts_remote_jobs_too(labeller):
    text = "You must have the right to work in the UK."
    assert labeller.label(job("Remote - Worldwide", text)).label == "restricted"


def test_citizenship_and_clearance(labeller):
    assert labeller.label(job("Washington, DC", "Must be a US citizen.")).label == "restricted"
    assert labeller.label(job("Austin, TX", "Active security clearance required.")).label == "restricted"


def test_positive_sponsorship(labeller):
    r = labeller.label(job("Amsterdam, Netherlands", "We offer visa sponsorship and relocation support."))
    assert r.label == "sponsor_yes"
    assert "visa sponsorship" in r.evidence[0]


def test_known_sponsor_from_register(labeller):
    r = labeller.label(job("London, UK", company="Monzo"))
    assert r.label == "sponsor_likely"
    assert "Monzo Bank Limited" in r.evidence[0]


def test_known_sponsor_from_companies_yaml(labeller):
    r = labeller.label(job("Berlin, Germany", company="Other", known_sponsor=True))
    assert r.label == "sponsor_likely"


def test_unknown_sponsorship(labeller):
    r = labeller.label(job("Toronto, ON"))
    assert r.label == "sponsor_unknown" and r.country == "Canada"


def test_negative_sentence_is_not_counted_as_positive(labeller):
    r = labeller.label(job("Paris, France", "Visa sponsorship is not available for this role."))
    assert r.label == "restricted"


def test_multi_location_with_lagos_is_nigeria(labeller):
    assert labeller.label(job("London, UK; Lagos, Nigeria")).label == "nigeria"


def test_plain_remote_without_limits_is_open(labeller):
    assert labeller.label(job("Remote", remote=True)).label == "remote_open"


def test_plain_remote_with_no_sponsorship_is_restricted(labeller):
    r = labeller.label(job("Remote", "We cannot sponsor work visas.", remote=True))
    assert r.label == "restricted"


def test_remote_europe_is_treated_as_abroad(labeller):
    assert labeller.label(job("Remote - Europe")).label == "sponsor_unknown"
