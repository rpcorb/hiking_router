from hiking_router.search.state import SearchState


def score_partial_state(
    state: SearchState,
    target_miles: float,
    estimated_return_miles: float,
    ridge_bonus: float,
    revisit_penalty: float,
) -> float:
    projected_total = state.distance_miles + estimated_return_miles
    target_error = abs(projected_total - target_miles)
    distance_score = max(0.0, 1.0 - (target_error / max(target_miles, 0.1)))
    return distance_score + ridge_bonus - revisit_penalty
