
def calculate_semantic_score(hook, clarity, emotion, value):
    scores = [hook, clarity, emotion, value]

    for score in scores:
        if not isinstance(score, int) or isinstance(score, bool):
            raise TypeError("Scores must be integers")

        if not 0 <= score <= 5:
            raise ValueError("Scores must be between 0 and 5")

    return sum(scores)



def rank_clips(clips, top_n=5):
    return sorted(
        clips,
        key=lambda clip: (
            -clip["score"],
            clip.get("duration", float("inf"))
        )
    )[:top_n]

