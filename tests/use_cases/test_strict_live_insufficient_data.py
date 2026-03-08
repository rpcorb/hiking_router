from hiking_router.use_cases.generate_loop import generate_top_loops


def test_strict_live_returns_empty_routes_when_live_and_cache_unavailable(tmp_path, monkeypatch):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))
    monkeypatch.setenv("HIKING_ROUTER_OSM_BASE_URL", "https://invalid.local/overpass")
    monkeypatch.setenv("HIKING_ROUTER_USGS_BASE_URL", "https://invalid.local/tnm")

    payload = generate_top_loops(
        {
            "near": "Roanoke, VA",
            "miles_min": 12,
            "miles_max": 15,
            "difficulty": "strenuous",
            "strict_live": True,
            "force_live": True,
        }
    )

    assert payload["routes"] == []
    assert payload["meta"]["reason"] is not None
    assert "insufficient" in payload["meta"]["reason"].lower()
