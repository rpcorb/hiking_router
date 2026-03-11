import time

from hiking_router.use_cases.generate_loop import generate_top_loops


def test_warm_cache_query_budget_placeholder(tmp_path, monkeypatch):
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
    (tmp_path / "raw" / "ridge").mkdir(parents=True, exist_ok=True)
    (tmp_path / "raw" / "ridge" / "z10-290-391.geojson").write_text(
        '{"type":"FeatureCollection","features":[]}'
    )
    (tmp_path / "raw" / "summit").mkdir(parents=True, exist_ok=True)
    (tmp_path / "raw" / "summit" / "z10-290-391.geojson").write_text(
        '{"type":"FeatureCollection","features":[]}'
    )
    (tmp_path / "raw" / "usgs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "raw" / "usgs" / "z10-290-391.tif").write_bytes(b"dem")

    query = {"near": "Roanoke, VA", "miles_min": 0.1, "miles_max": 1.0, "difficulty": "moderate"}
    _ = generate_top_loops(query)

    start = time.perf_counter()
    _ = generate_top_loops(query)
    elapsed = time.perf_counter() - start
    assert elapsed < 0.30
