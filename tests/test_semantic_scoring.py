
import pytest

from semantic_scoring import calculate_semantic_score
from semantic_scoring import rank_clips

@pytest.mark.parametrize(
    "hook, clarity, emotion, value, expected",
    [
        (5, 4, 5, 3, 17),
        (0, 0, 0, 0, 0),
        (5, 5, 5, 5, 20),
        (2, 3, 1, 4, 10),
    ]
)
def test_valid_semantic_scores(
    hook, clarity, emotion, value, expected
):
    result = calculate_semantic_score(
        hook, clarity, emotion, value
    )

    assert result == expected


@pytest.mark.parametrize(
    "scores, expected_error",
    [
        ((6, 4, 3, 2), ValueError),
        ((-1, 4, 3, 2), ValueError),
        ((3.5, 4, 3, 2), TypeError),
        ((True, 4, 3, 2), TypeError),
        (("five", 4, 3, 2), TypeError),
    ]
)
def test_invalid_semantic_scores(scores, expected_error):
    with pytest.raises(expected_error):
        calculate_semantic_score(*scores)


def test_rank_clips():
    clips = [
        {"id": 1, "score": 12},
        {"id": 2, "score": 19},
        {"id": 3, "score": 15},
        {"id": 4, "score": 8}
    ]

    ranked = rank_clips(clips, top_n=2)

    assert len(ranked) == 2
    assert ranked[0]["id"] == 2
    assert ranked[1]["id"] == 3
