
from scoring import calculate_score

import pytest


@pytest.mark.parametrize(
    "sentence, expected",
    [
        ("This is a secret", 4),
        ("Never make this mistake", 5),
        ("SUCCESS is important", 2),
        ("I enjoy playing tennis", 0),
    ]
)
def test_multiple_sentences(sentence, expected):
    result = calculate_score(sentence)
    assert result == expected


def test_success_keyword():
    result = calculate_score("Success comes with practice")
    assert result == 2


def test_question_bonus():
    sentence = "Why do people give up?"

    score = calculate_score(sentence)

    assert score == 2


def test_keywords_with_complex_punctuation():
    sentence = '"The secret:" to success;'

    score = calculate_score(sentence)

    assert score == 6

