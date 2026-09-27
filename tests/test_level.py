from hunt.scoring import detect_level


def test_title_words_win():
    assert detect_level("Machine Learning Intern", "10+ years of experience")[0] == "intern"
    assert detect_level("Senior Data Scientist")[0] == "senior"


def test_main_requirement_not_the_smallest_number():
    text = "3-5 years of relevant experience, including at least 2-3 years with analytics."
    assert detect_level("Data Scientist", text) == ("mid", True)


def test_bachelors_figure_is_used():
    text = "PhD with 1-3 years, MS with 2-6 years, or BS with 4-8 years of experience"
    assert detect_level("Data Scientist", text) == ("mid", True)


def test_new_grad_text_and_no_years():
    assert detect_level("Data Scientist", "Open to new grads.")[0] == "entry"
    assert detect_level("Data Scientist", "Build models.")[0] == "unspecified"
