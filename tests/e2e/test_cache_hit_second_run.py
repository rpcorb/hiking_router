from hiking_router.use_cases.generate_loop import generate_top_loops


def test_second_run_reports_cache_hits(tmp_path, monkeypatch):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))

    _ = generate_top_loops({"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})
    second = generate_top_loops({"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})

    assert second["meta"]["cache"]["osm"] in {"hit", "partial"}
