from hiking_router.use_cases.generate_loop import generate_top_loops


def test_generate_top_loops_returns_v2_envelope_with_cache_meta():
    payload = generate_top_loops({"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})
    assert payload["meta"]["engine_version"] == "v2-osm-usgs"
    assert "cache" in payload["meta"]
    assert isinstance(payload["routes"], list)


def test_generate_top_loops_populates_summit_proximity_when_summits_available(
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

    summit_path = tmp_path / "raw" / "summit" / "z10-290-391.geojson"
    summit_path.parent.mkdir(parents=True, exist_ok=True)
    summit_path.write_text(
        '{"type":"FeatureCollection","features":['
        '{"type":"Feature","geometry":{"type":"Point","coordinates":[-80.0,37.001]},"properties":{"name":"Peak"}}]}'
    )

    ridge_path = tmp_path / "raw" / "ridge" / "z10-290-391.geojson"
    ridge_path.parent.mkdir(parents=True, exist_ok=True)
    ridge_path.write_text('{"type":"FeatureCollection","features":[]}')

    usgs_path = tmp_path / "raw" / "usgs" / "z10-290-391.tif"
    usgs_path.parent.mkdir(parents=True, exist_ok=True)
    usgs_path.write_bytes(b"dem")

    payload = generate_top_loops(
        {
            "near": "Roanoke, VA",
            "miles_min": 0.1,
            "miles_max": 1.0,
            "difficulty": "moderate",
        }
    )

    assert payload["routes"][0]["terrain"]["summit_proximity_min_m"] is not None
