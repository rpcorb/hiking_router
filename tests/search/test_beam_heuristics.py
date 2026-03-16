from hiking_router.search.heuristics import score_partial_state
from hiking_router.search.state import SearchState


def _state(
    distance_miles: float,
    elevation_gain_ft: float,
) -> SearchState:
    return SearchState(
        origin="a",
        current_node="b",
        path_nodes=("a", "b"),
        used_edges=frozenset({("a", "b")}),
        distance_miles=distance_miles,
        elevation_gain_ft=elevation_gain_ft,
    )


def test_score_partial_state_prefers_distance_closer_to_target_midpoint():
    closer = score_partial_state(
        _state(distance_miles=6.0, elevation_gain_ft=500.0),
        target_miles=10.0,
        estimated_return_miles=4.0,
        ridge_bonus=0.0,
        revisit_penalty=0.0,
    )
    farther = score_partial_state(
        _state(distance_miles=2.0, elevation_gain_ft=500.0),
        target_miles=10.0,
        estimated_return_miles=4.0,
        ridge_bonus=0.0,
        revisit_penalty=0.0,
    )

    assert closer > farther


def test_score_partial_state_rewards_ridge_bonus_and_penalizes_revisits():
    strong = score_partial_state(
        _state(distance_miles=5.0, elevation_gain_ft=400.0),
        target_miles=10.0,
        estimated_return_miles=4.0,
        ridge_bonus=0.8,
        revisit_penalty=0.0,
    )
    weak = score_partial_state(
        _state(distance_miles=5.0, elevation_gain_ft=400.0),
        target_miles=10.0,
        estimated_return_miles=4.0,
        ridge_bonus=0.1,
        revisit_penalty=0.4,
    )

    assert strong > weak
