def distance_fit_score(loop_miles: float, miles_min: float, miles_max: float) -> float:
    if miles_max < miles_min:
        miles_max = miles_min
    center = (miles_min + miles_max) / 2.0
    half_band = max((miles_max - miles_min) / 2.0, 0.1)
    return max(0.0, 1.0 - (abs(loop_miles - center) / (half_band * 2.0)))


def _difficulty_target_gain_per_mile(difficulty: str) -> float:
    level = (difficulty or "").strip().lower()
    if level == "easy":
        return 150.0
    if level == "moderate":
        return 300.0
    if level == "strenuous":
        return 600.0
    return 350.0


def difficulty_fit_score(gain_per_mile_ft: float, difficulty: str) -> float:
    target = _difficulty_target_gain_per_mile(difficulty)
    if target <= 0:
        return 0.0
    error_ratio = abs(gain_per_mile_ft - target) / target
    return max(0.0, 1.0 - error_ratio)


def sustained_grade_penalty(gain_per_mile_ft: float, difficulty: str) -> float:
    target = _difficulty_target_gain_per_mile(difficulty)
    if target <= 0:
        return 0.0
    severe = target * 2.0
    if gain_per_mile_ft <= severe:
        return 0.0
    return min(0.25, (gain_per_mile_ft - severe) / severe * 0.25)


def composite_score(
    distance_fit: float,
    difficulty_fit: float,
    terrain_fit: float,
    penalties: float,
) -> float:
    raw = 0.35 * distance_fit + 0.30 * difficulty_fit + 0.35 * terrain_fit - penalties
    return max(0.0, min(1.0, raw))
