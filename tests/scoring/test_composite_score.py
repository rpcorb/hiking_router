from hiking_router.scoring.composite import (
    composite_score,
    distance_fit_score,
    difficulty_fit_score,
    sustained_grade_penalty,
)


def test_composite_score_increases_with_better_terrain_fit():
    weak = composite_score(distance_fit=0.8, difficulty_fit=0.5, terrain_fit=0.2, penalties=0.1)
    strong = composite_score(distance_fit=0.8, difficulty_fit=0.5, terrain_fit=0.9, penalties=0.1)
    assert strong > weak


def test_distance_fit_score_prefers_center_of_requested_band():
    perfect = distance_fit_score(loop_miles=13.5, miles_min=12.0, miles_max=15.0)
    edge = distance_fit_score(loop_miles=12.0, miles_min=12.0, miles_max=15.0)
    outside = distance_fit_score(loop_miles=18.0, miles_min=12.0, miles_max=15.0)
    assert perfect > edge
    assert edge > outside


def test_difficulty_fit_and_grade_penalty_for_moderate_queries():
    target = difficulty_fit_score(gain_per_mile_ft=300.0, difficulty="moderate")
    too_steep = difficulty_fit_score(gain_per_mile_ft=900.0, difficulty="moderate")
    penalty = sustained_grade_penalty(gain_per_mile_ft=900.0, difficulty="moderate")
    assert target > too_steep
    assert penalty > 0.0
