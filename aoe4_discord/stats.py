def calculate_percentage_change(x: int, y: int) -> float:
    if x == 0:
        if y == 0:
            return 0
        else:
            return float('inf') if y > 0 else float('-inf')
    percentage_change = ((y - x) / abs(x)) * 100
    return percentage_change
