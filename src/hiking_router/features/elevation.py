M_PER_MILE = 1609.34


def gain_per_mile(gain_m: float, length_m: float) -> float:
    if length_m <= 0:
        return 0.0
    return gain_m / (length_m / M_PER_MILE)
