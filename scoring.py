import string


def calculate_score(sentence):
    words = sentence.lower().split()
    clean_words = [
        word.strip(string.punctuation)
        for word in words
]

    score = 0

    keywords = {
        "success": 2,
        "mistake": 3,
        "secret": 4,
        "never": 2,
        "how": 1
    }

    for keyword, points in keywords.items():
        if keyword in clean_words:
            score += points

        if sentence.strip().endswith("?"):
            score =+ 2

    return score
