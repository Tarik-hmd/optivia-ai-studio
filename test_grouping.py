from clip_engine import generate_clips


segments = [
    {"start": 0, "end": 4.8, "text": "Segment 1"},
    {"start": 4.8, "end": 9.96, "text": "Segment 2"},
    {"start": 9.96, "end": 14.28, "text": "Segment 3"}
]

groups = group_segments(segments, max_duration=60)

print("Number of groups:", len(groups))

for group in groups:
    print(group)
    