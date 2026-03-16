from hiking_router.use_cases.generate_loop import generate_top_loops


def test_generate_top_loops_falls_back_to_legacy_search_when_beam_returns_none(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))

    osm_path = tmp_path / "raw" / "osm" / "z10-290-391.geojson"
    osm_path.parent.mkdir(parents=True, exist_ok=True)
    osm_path.write_text(
        '{"elements":['
        '{"type":"node","id":1,"lat":37.0,"lon":-80.0},'
        '{"type":"node","id":2,"lat":37.001,"lon":-80.0},'
        '{"type":"node","id":3,"lat":37.001,"lon":-80.001},'
        '{"type":"node","id":4,"lat":37.0,"lon":-80.001},'
        '{"type":"way","id":10,"nodes":[1,2,3,4,1],"tags":{"highway":"path"}}]}'
    )
    ridge_path = tmp_path / "raw" / "ridge" / "z10-290-391.geojson"
    ridge_path.parent.mkdir(parents=True, exist_ok=True)
    ridge_path.write_text('{"type":"FeatureCollection","features":[]}')
    summit_path = tmp_path / "raw" / "summit" / "z10-290-391.geojson"
    summit_path.parent.mkdir(parents=True, exist_ok=True)
    summit_path.write_text('{"type":"FeatureCollection","features":[]}')
    usgs_path = tmp_path / "raw" / "usgs" / "z10-290-391.tif"
    usgs_path.parent.mkdir(parents=True, exist_ok=True)
    usgs_path.write_bytes(b"dem")

    monkeypatch.setattr(
        "hiking_router.use_cases.generate_loop.synthesize_loops_with_beam",
        lambda **kwargs: [],
    )

    payload = generate_top_loops(
        {"near": "Roanoke, VA", "miles_min": 0.1, "miles_max": 1.0, "difficulty": "moderate"}
    )

    assert payload["routes"]
    assert payload["routes"][0]["id"].startswith("loop-")
