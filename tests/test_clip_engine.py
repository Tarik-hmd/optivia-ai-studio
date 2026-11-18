
from clip_engine import time_based_windows, remove_overlapping_clips
import pytest


def test_windows_max_duration():
    segments = [
        {"start": 0, "end": 10, "text": "First segment"},
        {"start": 10, "end": 20, "text": "Second segment"},
        {"start": 20, "end": 30, "text": "Third segment"},
        {"start": 30, "end": 40, "text": "Fourth segment"},
    ]

    windows = time_based_windows(
        segments,
        min_duration=10,
        max_duration=20
    )

    assert len(windows) > 0

    for window in windows:
        duration = window[-1]["end"] - window[0]["start"]
        assert duration <= 20


def test_windows_min_duration():
    segments = [
        {"start": 0, "end": 5, "text": "First"},
        {"start": 5, "end": 10, "text": "Second"},
        {"start": 10, "end": 15, "text": "Third"},
        {"start": 15, "end": 20, "text": "Fourth"},
    ]

    windows = time_based_windows(
        segments,
        min_duration=10,
        max_duration=20
    )

    assert len(windows) > 0

    for window in windows:
        duration = window[-1]["end"] - window[0]["start"]
        assert duration >= 10



def test_remove_overlapping_clips():
    clips = [
        {
            "start": 10,
            "end": 30,
            "duration": 20,
            "score": 8
        },
        {
            "start": 15,
            "end": 35,
            "duration": 20,
            "score": 5
        },
        {
            "start": 50,
            "end": 70,
            "duration": 20,
            "score": 7
        }
    ]

    result = remove_overlapping_clips(clips)

    assert len(result) == 2
    assert result[0]["score"] == 8
    assert result[1]["score"] == 7


def test_empty_segments():
    segments = []

    windows = time_based_windows(
        segments,
        min_duration=10,
        max_duration=60
    )

    assert windows == []

def test_none_segments():
    with pytest.raises(TypeError):
        time_based_windows(
            None,
            min_duration=10,
            max_duration=60
        )
