
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


def test_question_adds_bonus_to_keyword_score():
    text = "What is the secret to success?"

    score = calculate_score(text)

    assert score == 8

@pytest.mark.parametrize(
    "text, expected",
    [
        ("The secret to success", 6),
        ("Le secret de la réussite", 6),
        ("سر النجاح", 6),
    ]
)
def test_multilingual_keyword_scoring(text, expected):
    assert calculate_score(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("سر النجاح", 6),
        ("السر وراء النجاح", 6),
        ("سر نجاح", 6),
        ("ما هو سر النجاح؟", 8),
    ]
)
def test_arabic_keyword_variations(text, expected):
    assert calculate_score(text) == expected



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


@pytest.mark.parametrize(
    "text, expected",
    [
        ("This is a mistake", 3),
        ("This is an error", 3),
        ("C'est une erreur", 3),
        ("C'est une faute", 3),
        ("هذا خطأ", 3),
    ]
)
def test_mistake_synonyms(text, expected):
    assert calculate_score(text) == expected



@pytest.mark.parametrize(
    "text, expected",
    [
        ("This mistake was an error", 3),
        ("Cette erreur est une faute", 3),
        ("Mistake and error?", 5),
        ("Une erreur et un secret", 7),
        ("This mistake was a secret error", 7),
    ]
)
def test_synonyms_not_double_counted(text, expected):
    assert calculate_score(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("The secret to success", 6),
        ("What is the secret to success?", 8),
        ("secret mistake never success how", 10),
        ("secret mistake never success how?", 10),
    ]
)
def test_score_maximum(text, expected):
    assert calculate_score(text) == expected

def test_long_text_does_not_gain_points_from_repetition():
    short_text = "This is a secret"

    long_text = (
        "This is a secret. "
        + "This is a secret. " * 20
    )

    assert calculate_score(short_text) == calculate_score(long_text)
