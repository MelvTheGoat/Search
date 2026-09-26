from hunt.checker import check_file
from hunt.config import load_yaml

CV_NUMBERS = {0.96, 0.842, 50.0, 27.0, 5.1, 2026.0}
RULES = load_yaml("writing.yaml")

GOOD_BODY = " ".join(["Plain words here."] * 55)


def write(tmp_path, body, sign="Oluwatobi Melvyn Mayungbo\nmayungboluwatobi@gmail.com"):
    p = tmp_path / "letter.md"
    p.write_text(f"---\njob_id: 3\nlink: https://x.com/jobs/12345\n---\n\n## Cover letter\n\n{body}\n\n{sign}\n\n## Why this company\n\nShort.\n")
    return p


def kinds(problems):
    return [p.kind for p in problems]


def test_clean_letter_passes(tmp_path):
    p = write(tmp_path, GOOD_BODY + " My RAG system hit 0.96 recall@5 and 0.842 MRR.")
    assert check_file(p, CV_NUMBERS, RULES) == []


def test_em_and_en_dashes_are_flagged_with_line(tmp_path):
    p = write(tmp_path, GOOD_BODY + "\nI built it — fast.\nFrom 2021 – 2025.")
    probs = [x for x in check_file(p, CV_NUMBERS | {2021.0, 2025.0}, RULES) if x.kind == "dash"]
    assert len(probs) == 2
    assert probs[0].line == 9 and probs[1].line == 10


def test_spaced_hyphen_is_flagged_but_word_hyphen_is_fine(tmp_path):
    p = write(tmp_path, GOOD_BODY + "\nAn end-to-end system - built alone.")
    probs = [x for x in check_file(p, CV_NUMBERS, RULES) if x.kind == "dash"]
    assert len(probs) == 1


def test_banned_phrases(tmp_path):
    p = write(tmp_path, GOOD_BODY + "\nI am excited to apply. I am passionate about AI and leverage data.")
    msgs = " ".join(x.message for x in check_file(p, CV_NUMBERS, RULES) if x.kind == "banned")
    for phrase in ("excited to apply", "passionate", "leverage"):
        assert phrase in msgs


def test_numbers_not_in_cv_are_flagged(tmp_path):
    p = write(tmp_path, GOOD_BODY + "\nI cut cost by 27% and served 10 million users.")
    probs = [x for x in check_file(p, CV_NUMBERS, RULES) if x.kind == "number"]
    assert len(probs) == 1 and "10" in probs[0].message


def test_numbers_in_urls_and_front_matter_are_ignored(tmp_path):
    p = write(tmp_path, GOOD_BODY + "\nSee https://github.com/x/repo-999 for code.")
    assert "number" not in kinds(check_file(p, CV_NUMBERS, RULES))


def test_length_and_sign_off(tmp_path):
    p = write(tmp_path, "Too short.", sign="Thanks")
    k = kinds(check_file(p, CV_NUMBERS, RULES))
    assert "length" in k and "sign-off" in k
