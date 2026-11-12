def calculate_score(sentence):
    words = sentence.lower().split()
    clean_words = []

    for word in words:
        clean_word = word.strip("!?.,")
        clean_words.append(clean_word)
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

    return score
