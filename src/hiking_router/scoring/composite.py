def composite_score(
    distance_fit: float,
    difficulty_fit: float,
    terrain_fit: float,
    penalties: float,
) -> float:
    raw = 0.35 * distance_fit + 0.30 * difficulty_fit + 0.35 * terrain_fit - penalties
    return max(0.0, min(1.0, raw))
