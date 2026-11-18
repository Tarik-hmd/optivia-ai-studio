
from clip_engine import time_based_windows, build_clips

segments = [
    {"start": 0, "end": 8, "text": "Hello everyone"},
    {"start": 8, "end": 18, "text": "The secret of success"},
    {"start": 18, "end": 30, "text": "Never stop learning"},
    {"start": 30, "end": 42, "text": "The biggest mistake"},
    {"start": 42, "end": 55, "text": "How to improve"},
    {"start": 55, "end": 70, "text": "Build better systems"}
]

windows = time_based_windows(
    segments,
    min_duration=15,
    max_duration=60
)

clips = build_clips(
    windows,
    min_duration=15,
    max_duration=60,
    top_n=5
)

print("Total candidates:", len(windows))
print("Selected clips:", len(clips))

for index, clip in enumerate(clips, start=1):
    print(f"\nClip {index}")
    print("Start:", clip["start"])
    print("End:", clip["end"])
    print("Duration:", clip["duration"])
    print("Score:", clip["score"])
    print("Text:", clip["text"])
