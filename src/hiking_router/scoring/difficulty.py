def is_strenuous(gain_per_mile_ft: float, threshold_ft_per_mile: float = 500) -> bool:
    return gain_per_mile_ft >= threshold_ft_per_mile
