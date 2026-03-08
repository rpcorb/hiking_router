from hiking_router.use_cases.generate_loop import generate_top_loops


def test_candidates_considered_reflects_osm_segments(tmp_path, monkeypatch):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))

    osm_path = tmp_path / "raw" / "osm" / "z10-290-391.geojson"
    osm_path.parent.mkdir(parents=True, exist_ok=True)
    osm_path.write_text(
        '{"elements":['
        '{"type":"node","id":1,"lat":37.0,"lon":-80.0},'
        '{"type":"node","id":2,"lat":37.001,"lon":-80.001},'
        '{"type":"node","id":3,"lat":37.002,"lon":-80.002},'
        '{"type":"way","id":10,"nodes":[1,2,3],"tags":{"highway":"path"}}]}'
    )

    usgs_path = tmp_path / "raw" / "usgs" / "z10-290-391.tif"
    usgs_path.parent.mkdir(parents=True, exist_ok=True)
    usgs_path.write_bytes(b"dem")

    payload = generate_top_loops(
        {"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"}
    )

    assert payload["meta"]["candidates_considered"] >= 2
