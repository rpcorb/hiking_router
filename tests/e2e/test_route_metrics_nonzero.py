from hiking_router.use_cases.generate_loop import generate_top_loops


def test_route_elevation_metrics_are_nonzero_when_dem_exists(tmp_path, monkeypatch):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))

    payload = generate_top_loops(
        {"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"}
    )
    route = payload["routes"][0]

    assert route["elevation_gain_ft"] > 0
    assert route["elevation_gain_per_mile_ft"] > 0
