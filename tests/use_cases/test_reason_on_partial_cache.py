from hiking_router.use_cases.generate_loop import generate_top_loops


def test_meta_reason_present_when_partial_cache_used(tmp_path, monkeypatch):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))
    _ = generate_top_loops({"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})

    payload = generate_top_loops({
        "near": "Roanoke, VA",
        "miles_min": 12,
        "miles_max": 15,
        "difficulty": "strenuous",
        "force_live": True,
    })

    assert payload["meta"]["cache"]["osm"] == "partial"
    assert payload["meta"]["cache"]["usgs"] == "partial"
    assert payload["meta"]["reason"] is not None
