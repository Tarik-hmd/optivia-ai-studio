

from clip_engine import sliding_windows, build_clips

segments = [
    {"start": 0, "end": 10, "text": "Segment 1"},
    {"start": 10, "end": 20, "text": "Segment 2"},
    {"start": 20, "end": 30, "text": "Segment 3"},
    {"start": 30, "end": 40, "text": "Segment 4"},
    {"start": 40, "end": 50, "text": "Segment 5"}
]



windows = sliding_windows(
    segments,
    window_size=3
)

clips = build_clips(
    windows,
    min_duration=15,
    max_duration=60,
    top_n=5
)

print("Total windows:", len(windows))
print("Selected clips:", len(clips))

for index, clip in enumerate(clips, start=1):
    print(f"\nClip {index}")
    print("Text:", clip["text"])
    print("Start:", clip["start"])
    print("End:", clip["end"])
    print("Duration:", clip["duration"])
    print("Score:", clip["score"])

