from scoring import calculate_score

assert calculate_score("Never reveal the secret to success!") == 8
assert calculate_score("How can I avoid this mistake?") == 4
assert calculate_score("Hello everyone!") == 0
assert calculate_score("The secret to success!") == 10

print("All scoring tests passed!")