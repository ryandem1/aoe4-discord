import statistics


def calculate_percentage_change(x: int, y: int) -> float:
    if x == 0:
        if y == 0:
            return 0
        else:
            return float('inf') if y > 0 else float('-inf')
    percentage_change = ((y - x) / abs(x)) * 100
    return percentage_change


def micro_average(*lsts: list) -> float:
    # Assuming all lists have the same length
    length = len(lsts[0])
    result = []

    for i in range(length):
        total = sum(lst[i] for lst in lsts)
        result.append(total)

    micro_average_mean = statistics.mean(result)
    return micro_average_mean
