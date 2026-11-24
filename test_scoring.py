import pytest

from scoring import calculate_score

assert calculate_score("Never reveal the secret to success!") == 8
assert calculate_score("How can I avoid this mistake?") == 4
assert calculate_score("Hello everyone!") == 0
assert calculate_score("The secret to success!") == 10

print("All scoring tests passed!")





@pytest.mark.parametrize(
    "text, expected",
    [
        ("Le secret du succès", 6),
        ("Le secret du succes", 6),
        ("Le secret de la réussite", 6),
        ("سر النجاح", 6),
        ("السر وراء النجاح", 6),
    ]
)
def test_normalized_keywords_are_not_double_counted(text, expected):
    assert calculate_score(text) == expected



def test_long_text_does_not_gain_points_from_repetition():
    short_text = "This is a secret"

    long_text = (
        "This is a secret. "
        + "This is a secret. " * 20
    )

    assert calculate_score(short_text) == calculate_score(long_text)

def test_long_text_does_not_gain_points_from_repetition():
    short_text = "This is a secret"

    long_text = (
        "This is a secret. "
        + "This is a secret. " * 20
    )

    assert calculate_score(short_text) == calculate_score(long_text)
