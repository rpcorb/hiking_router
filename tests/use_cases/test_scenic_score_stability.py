from hiking_router.use_cases.generate_loop import generate_top_loops


def test_scenic_score_is_deterministic_for_fixed_fixture_data(tmp_path, monkeypatch):
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
    ridge_path.write_text(
        '{"type":"FeatureCollection","features":['
        '{"type":"Feature","geometry":{"type":"LineString","coordinates":[[-80.0,37.0],[-80.0,37.001]]},"properties":{}}]}'
    )

    summit_path = tmp_path / "raw" / "summit" / "z10-290-391.geojson"
    summit_path.parent.mkdir(parents=True, exist_ok=True)
    summit_path.write_text(
        '{"type":"FeatureCollection","features":['
        '{"type":"Feature","geometry":{"type":"Point","coordinates":[-80.0,37.001]},"properties":{"name":"Peak"}}]}'
    )

    usgs_path = tmp_path / "raw" / "usgs" / "z10-290-391.tif"
    usgs_path.parent.mkdir(parents=True, exist_ok=True)
    usgs_path.write_bytes(b"dem")

    query = {
        "near": "Roanoke, VA",
        "miles_min": 0.1,
        "miles_max": 1.0,
        "difficulty": "moderate",
    }
    first = generate_top_loops(query)
    second = generate_top_loops(query)

    first_score = first["routes"][0]["terrain"]["scenic_score"]
    second_score = second["routes"][0]["terrain"]["scenic_score"]
    assert first_score is not None
    assert second_score is not None
    assert first_score == second_score

