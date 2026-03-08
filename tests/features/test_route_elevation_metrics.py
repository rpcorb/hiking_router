from hiking_router.features.dem_sampling import route_elevation_metrics


def test_route_elevation_metrics_returns_gain_and_gain_per_mile():
    metrics = route_elevation_metrics(samples=[100, 120, 110, 140], distance_miles=2.0)
    assert metrics["gain_ft"] > 0
    assert metrics["gain_per_mile_ft"] > 0
