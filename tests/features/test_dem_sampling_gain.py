from hiking_router.features.dem_sampling import elevation_gain_from_profile


def test_elevation_gain_from_profile_accumulates_only_positive_deltas():
    gain = elevation_gain_from_profile([100, 120, 110, 140])
    assert gain == 50
