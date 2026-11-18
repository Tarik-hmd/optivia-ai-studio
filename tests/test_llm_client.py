
import pytest
from pydantic import ValidationError

from llm_client import ClipEvaluation


def test_invalid_llm_score():
    with pytest.raises(ValidationError):
        ClipEvaluation(
            hook=9,
            clarity=4,
            emotion=5,
            value=3,
            reason="Interesting story"
        )


def test_valid_llm_response():
    evaluation = ClipEvaluation(
        hook=5,
        clarity=4,
        emotion=5,
        value=3,
        reason="Strong emotional storytelling"
    )

    assert evaluation.hook == 5
    assert evaluation.clarity == 4
    assert evaluation.emotion == 5
    assert evaluation.value == 3
    assert evaluation.reason == "Strong emotional storytelling"


from unittest.mock import patch

from llm_client import create_llm_client


def test_create_llm_client():
    with patch("llm_client.OpenAI") as mock_openai:
        client = create_llm_client("fake-api-key")

        mock_openai.assert_called_once_with(
            api_key="fake-api-key"
        )

        assert client == mock_openai.return_value


from unittest.mock import MagicMock

from llm_client import evaluate_clip


def test_evaluate_clip():
    fake_client = MagicMock()

    fake_evaluation = ClipEvaluation(
        hook=5,
        clarity=4,
        emotion=5,
        value=3,
        reason="Strong emotional story"
    )

    fake_client.responses.parse.return_value.output_parsed = fake_evaluation

    result = evaluate_clip(
        fake_client,
        "I lost everything and rebuilt my company."
    )

    assert result.hook == 5
    assert result.clarity == 4
    assert result.emotion == 5
    assert result.value == 3

    fake_client.responses.parse.assert_called_once()


from llm_client import score_clip


def test_score_clip():
    fake_client = MagicMock()

    fake_evaluation = ClipEvaluation(
        hook=5,
        clarity=4,
        emotion=5,
        value=3,
        reason="Strong emotional storytelling"
    )

    fake_client.responses.parse.return_value.output_parsed = fake_evaluation

    result = score_clip(
        fake_client,
        "I lost everything and rebuilt my company."
    )

    assert result["score"] == 17
    assert result["evaluation"]["hook"] == 5
    assert result["evaluation"]["reason"] == "Strong emotional storytelling"

    fake_client.responses.parse.assert_called_once()


from unittest.mock import patch
from llm_client import evaluate_candidates


def test_evaluate_candidates():
    candidates = [
        {"start": 0, "end": 20, "text": "Clip A"},
        {"start": 25, "end": 45, "text": "Clip B"},
        {"start": 50, "end": 75, "text": "Clip C"}
    ]

    fake_scores = [
        {"score": 12, "evaluation": {"reason": "Average"}},
        {"score": 19, "evaluation": {"reason": "Excellent"}},
        {"score": 15, "evaluation": {"reason": "Good"}}
    ]

    with patch("llm_client.score_clip", side_effect=fake_scores) as mock_score:
        result = evaluate_candidates(
            client=None,
            candidates=candidates,
            top_n=2
        )

    assert len(result) == 2
    assert result[0]["text"] == "Clip B"
    assert result[0]["score"] == 19
    assert result[0]["start"] == 25

    assert result[1]["text"] == "Clip C"
    assert result[1]["score"] == 15

    assert mock_score.call_count == 3
