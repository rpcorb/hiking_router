def ridge_fraction(total_m: float, ridge_m: float) -> float:
    if total_m <= 0:
        return 0.0
    value = ridge_m / total_m
    return max(0.0, min(1.0, value))
