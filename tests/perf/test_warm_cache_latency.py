import time

from hiking_router.use_cases import generate_loop as generate_loop_module


def _seed_cache(cache_root):
    osm_path = cache_root / "raw" / "osm" / "z10-290-391.geojson"
    osm_path.parent.mkdir(parents=True, exist_ok=True)
    osm_path.write_text(
        '{"elements":['
        '{"type":"node","id":1,"lat":37.0,"lon":-80.0},'
        '{"type":"node","id":2,"lat":37.001,"lon":-80.0},'
        '{"type":"node","id":3,"lat":37.001,"lon":-80.001},'
        '{"type":"node","id":4,"lat":37.0,"lon":-80.001},'
        '{"type":"way","id":10,"nodes":[1,2,3,4,1],"tags":{"highway":"path"}}]}'
    )

    ridge_path = cache_root / "raw" / "ridge" / "z10-290-391.geojson"
    ridge_path.parent.mkdir(parents=True, exist_ok=True)
    ridge_path.write_text('{"type":"FeatureCollection","features":[]}')

    summit_path = cache_root / "raw" / "summit" / "z10-290-391.geojson"
    summit_path.parent.mkdir(parents=True, exist_ok=True)
    summit_path.write_text('{"type":"FeatureCollection","features":[]}')

    usgs_path = cache_root / "raw" / "usgs" / "z10-290-391.tif"
    usgs_path.parent.mkdir(parents=True, exist_ok=True)
    usgs_path.write_bytes(b"dem")


def test_warm_cache_query_latency_under_budget(tmp_path, monkeypatch):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))
    _seed_cache(tmp_path)

    query = {
        "near": "Roanoke, VA",
        "miles_min": 0.1,
        "miles_max": 1.0,
        "difficulty": "moderate",
    }
    _ = generate_loop_module.generate_top_loops(query)

    start = time.perf_counter()
    _ = generate_loop_module.generate_top_loops(query)
    elapsed = time.perf_counter() - start

    assert elapsed < 0.25


def test_scenic_score_called_once_per_route(tmp_path, monkeypatch):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))
    _seed_cache(tmp_path)

    call_count = {"count": 0}
    original = generate_loop_module.scenic_score

    def counting_scenic(*args, **kwargs):
        call_count["count"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(generate_loop_module, "scenic_score", counting_scenic)

    payload = generate_loop_module.generate_top_loops(
        {
            "near": "Roanoke, VA",
            "miles_min": 0.1,
            "miles_max": 1.0,
            "difficulty": "moderate",
        }
    )

    assert call_count["count"] == len(payload["routes"])


def test_warm_cache_query_with_beam_search_stays_under_budget(tmp_path, monkeypatch):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))
    _seed_cache(tmp_path)

    query = {
        "near": "Roanoke, VA",
        "miles_min": 0.1,
        "miles_max": 1.0,
        "difficulty": "moderate",
    }
    _ = generate_loop_module.generate_top_loops(query)

    start = time.perf_counter()
    payload = generate_loop_module.generate_top_loops(query)
    elapsed = time.perf_counter() - start

    assert payload["routes"]
    assert elapsed < 0.35
