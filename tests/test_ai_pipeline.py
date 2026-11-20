
from unittest.mock import patch, MagicMock

from clip_engine import build_ai_clips

import pytest


def test_build_ai_clips_connects_scoring():
    groups = [
        [
            {
                "text": "Most people give up too early.",
                "start": 0,
                "end": 10
            },
            {
                "text": "Success requires consistency and patience.",
                "start": 10,
                "end": 20
            }
        ]
    ]

    fake_client = MagicMock()

    with patch("llm_client.evaluate_candidates") as mock_evaluate:
        mock_evaluate.return_value = [
            {
                "text": "Most people give up too early. "
                        "Success requires consistency and patience.",
                "start": 0,
                "end": 20,
                "score": 18
            }
        ]

        result = build_ai_clips(
            groups,
            client=fake_client,
            top_n=3
        )

        assert len(result) == 1
        assert result[0]["score"] == 18

        mock_evaluate.assert_called_once()

        args, kwargs = mock_evaluate.call_args

        assert args[0] is fake_client
        assert len(args[1]) == 1
        assert args[1][0]["start"] == 0
        assert args[1][0]["end"] == 20
        assert kwargs["top_n"] is None


def test_build_ai_clips_respects_max_candidates():
    groups = []

    # Create 10 valid clips of 20 seconds each
    for i in range(10):
        start = i * 25

        groups.append([
            {
                "text": f"Interesting video segment number {i}",
                "start": start,
                "end": start + 20
            }
        ])

    fake_client = MagicMock()

    with patch("llm_client.evaluate_candidates") as mock_evaluate:
        mock_evaluate.return_value = []

        build_ai_clips(
            groups,
            client=fake_client,
            top_n=2,
            max_candidates=3
        )

        mock_evaluate.assert_called_once()

        args, kwargs = mock_evaluate.call_args
        candidates = args[1]

        # Only 3 out of 10 candidates reach the AI
        assert len(candidates) == 3
        assert kwargs["top_n"] is None


@pytest.mark.parametrize("invalid_limit", [0, -1, -10])
def test_build_ai_clips_rejects_invalid_limit(invalid_limit):
    fake_client = MagicMock()

    with patch("llm_client.evaluate_candidates") as mock_evaluate:
        with pytest.raises(
            ValueError,
            match="max_candidates must be at least 1"
        ):
            build_ai_clips(
                groups=[],
                client=fake_client,
                max_candidates=invalid_limit
            )

        # Invalid requests must never reach the AI
        mock_evaluate.assert_not_called()

def test_ai_pipeline_keeps_overlapping_candidates():
    groups = [
        [
            {"text": "First interesting moment",
             "start": 0, "end": 20}
        ],
        [
            {"text": "Second interesting moment",
             "start": 10, "end": 30}
        ]
    ]

    fake_client = MagicMock()

    with patch("llm_client.evaluate_candidates") as mock_evaluate:
        mock_evaluate.return_value = []

        build_ai_clips(
            groups,
            client=fake_client,
            max_candidates=10
        )

        mock_evaluate.assert_called_once()

        args, kwargs = mock_evaluate.call_args
        candidates = args[1]

        assert len(candidates) == 2

        assert {clip["start"] for clip in candidates} == {
            0, 10
        }



from clip_engine import select_final_clips


def test_select_final_clips_removes_overlaps():
    clips = [
        {
            "text": "Best clip",
            "start": 0,
            "end": 20,
            "duration": 20,
            "score": 19
        },
        {
            "text": "Overlapping clip",
            "start": 10,
            "end": 30,
            "duration": 20,
            "score": 12
        },
        {
            "text": "Independent clip",
            "start": 40,
            "end": 60,
            "duration": 20,
            "score": 17
        }
    ]

    result = select_final_clips(clips, top_n=2)

    assert len(result) == 2
    assert [clip["score"] for clip in result] == [19, 17]
    assert [clip["text"] for clip in result] == [
        "Best clip",
        "Independent clip"
    ]

def test_ai_pipeline_selects_best_non_overlapping_clips():
    groups = [
        [{"text": "First moment", "start": 0, "end": 20}],
        [{"text": "Second moment", "start": 10, "end": 30}],
        [{"text": "Third moment", "start": 40, "end": 60}]
    ]

    fake_client = MagicMock()

    evaluated_clips = [
        {
            "text": "First moment",
            "start": 0,
            "end": 20,
            "duration": 20,
            "score": 19
        },
        {
            "text": "Second moment",
            "start": 10,
            "end": 30,
            "duration": 20,
            "score": 18
        },
        {
            "text": "Third moment",
            "start": 40,
            "end": 60,
            "duration": 20,
            "score": 17
        }
    ]

    with patch("llm_client.evaluate_candidates") as mock_evaluate:
        mock_evaluate.return_value = evaluated_clips

        result = build_ai_clips(
            groups,
            client=fake_client,
            top_n=2
        )

        assert [clip["score"] for clip in result] == [19, 17]
        assert [clip["text"] for clip in result] == [
            "First moment",
            "Third moment"
        ]

        assert mock_evaluate.call_args.kwargs["top_n"] is None

from semantic_scoring import rank_clips


def test_rank_clips_without_limit():
    clips = [
        {"text": "Clip A", "score": 12},
        {"text": "Clip B", "score": 19},
        {"text": "Clip C", "score": 15}
    ]

    result = rank_clips(clips, top_n=None)

    assert len(result) == 3
    assert [clip["score"] for clip in result] == [
        19, 15, 12
    ]
