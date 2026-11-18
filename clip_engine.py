from scoring import calculate_score

def generate_clips(segments, min_words=3, max_words=100):
    clips = []

    for segment in segments:
        text = segment["text"]
        word_count = len(text.split())

        print("SEGMENT:", text)
        print("WORDS:", word_count, "LIMITS:", min_words, max_words)

        if min_words <= word_count <= max_words:
            score = calculate_score(text)

            clip = {
                "text": text,
                "start": segment["start"],
                "end": segment["end"],
                "duration": round(
                    segment["end"] - segment["start"], 2
                ),
                "word_count": word_count,
                "score": score
            }
            clips.append(clip)

        ranked_clips = sorted(
            clips,
            key=lambda clip: clip["score"],
            reverse=True
   )

    return ranked_clips


def group_segments(segments, max_duration=60):
    groups = []
    current_group = []

    for segment in segments:
        if not current_group:
            current_group.append(segment)
            continue

        start = current_group[0]["start"]
        duration = segment["end"] - start

        if duration <= max_duration:
            current_group.append(segment)
        else:
            groups.append(current_group)
            current_group = [segment]

    if current_group:
        groups.append(current_group)

    return groups




def build_clips(
    groups,
    min_duration=15,
    max_duration=60,
    top_n=5
):
    clips = []

    for group in groups:
        if not group:
            continue

        start = group[0]["start"]
        end = group[-1]["end"]
        duration = round(end - start, 2)

        # Ignore clips outside the allowed duration
        if not min_duration <= duration <= max_duration:
            continue

        # Combine all segment texts
        text = " ".join(
            segment["text"] for segment in group
        )

        # Create the clip
        clip = {
            "text": text,
            "start": start,
            "end": end,
            "duration": duration,
            "word_count": len(text.split()),
            "score": calculate_score(text)
        }

        clips.append(clip)

    # Rank clips from highest to lowest score
    ranked_clips = sorted(
        clips,
        key=lambda clip: clip["score"],
        reverse=True
    )
    unique_clips = remove_overlapping_clips(ranked_clips)

    if top_n is None:
        return unique_clips
    return unique_clips[:top_n]

def sliding_windows(segments, window_size=3):
    windows = []

    for i in range(len(segments) - window_size + 1):
        window = segments[i:i + window_size]
        windows.append(window)

    return windows

def time_based_windows(
    segments,
    min_duration=15,
    max_duration=60
):
    windows = []

    for start_index in range(len(segments)):
        window = []
        start_time = segments[start_index]["start"]

        for end_index in range(start_index, len(segments)):
            segment = segments[end_index]

            duration = segment["end"] - start_time

            if duration > max_duration:
                break

            window.append(segment)

            if duration >= min_duration:
                windows.append(window.copy())

    return windows

def calculate_overlap(clip_a, clip_b):
    overlap_start = max(clip_a["start"], clip_b["start"])
    overlap_end = min(clip_a["end"], clip_b["end"])

    overlap = max(0, overlap_end - overlap_start)

    return overlap

def remove_overlapping_clips(clips, max_overlap_ratio=0.3):
    selected_clips = []

    for clip in clips:
        is_duplicate = False

        for selected in selected_clips:
            overlap = calculate_overlap(clip, selected)

            shorter_duration = min(
                clip["duration"],
                selected["duration"]
            )

            if shorter_duration <= 0:
                continue

            overlap_ratio = overlap / shorter_duration

            if overlap_ratio > max_overlap_ratio:
                is_duplicate = True
                break

        if not is_duplicate:
            selected_clips.append(clip)

    return selected_clips

