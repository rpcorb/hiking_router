from hiking_router.use_cases.generate_loop import generate_top_loops


def test_generate_top_loops_returns_v2_envelope_with_cache_meta():
    payload = generate_top_loops({"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})
    assert payload["meta"]["engine_version"] == "v2-osm-usgs"
    assert "cache" in payload["meta"]
    assert isinstance(payload["routes"], list)
