
from subtitle_engine import generate_srt

segments = [
    {"start": 0, "end": 4.8, "text": "سلام عليكم محباً بكم في ديو طارق"},
    {"start": 4.8, "end": 9.96, "text": "جيد ليوما ديوكم في ديو تاي تست"},
    {"start": 9.96, "end": 14.28, "text": "بشكل ديو تجريباً تعالي لطالي"}
]

generate_srt(segments, "exports/test_subtitles.srt")

print("Subtitles generated successfully!")
