def calc_score(picks,actuals):
    points = 0
    for i, pick in enumerate(picks):
        if pick == actuals[i]:
            points += 10
        elif pick in actuals:
            points += 5
    return points
    