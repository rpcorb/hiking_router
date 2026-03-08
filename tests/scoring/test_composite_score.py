from hiking_router.scoring.composite import composite_score


def test_composite_score_increases_with_better_terrain_fit():
    weak = composite_score(distance_fit=0.8, difficulty_fit=0.5, terrain_fit=0.2, penalties=0.1)
    strong = composite_score(distance_fit=0.8, difficulty_fit=0.5, terrain_fit=0.9, penalties=0.1)
    assert strong > weak
