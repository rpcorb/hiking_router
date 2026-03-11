from hiking_router.use_cases.generate_loop import generate_top_loops


def _write_cycle_osm(path, lat: float, lon: float, delta: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '{"elements":['
        f'{{"type":"node","id":1,"lat":{lat},"lon":{lon}}},'
        f'{{"type":"node","id":2,"lat":{lat + delta},"lon":{lon}}},'
        f'{{"type":"node","id":3,"lat":{lat + delta},"lon":{lon + delta}}},'
        f'{{"type":"node","id":4,"lat":{lat},"lon":{lon + delta}}},'
        '{"type":"way","id":10,"nodes":[1,2,3,4,1],"tags":{"highway":"path"}}]}'
    )


def _seed_non_network_sources(cache_root) -> None:
    ridge_path = cache_root / "raw" / "ridge" / "z10-290-391.geojson"
    ridge_path.parent.mkdir(parents=True, exist_ok=True)
    ridge_path.write_text('{"type":"FeatureCollection","features":[]}')
    summit_path = cache_root / "raw" / "summit" / "z10-290-391.geojson"
    summit_path.parent.mkdir(parents=True, exist_ok=True)
    summit_path.write_text('{"type":"FeatureCollection","features":[]}')
    usgs_path = cache_root / "raw" / "usgs" / "z10-290-391.tif"
    usgs_path.parent.mkdir(parents=True, exist_ok=True)
    usgs_path.write_bytes(b"dem")


def test_multi_region_quality_distance_fit_on_two_fixtures(tmp_path, monkeypatch):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))

    osm_path = tmp_path / "raw" / "osm" / "z10-290-391.geojson"

    _write_cycle_osm(osm_path, lat=37.0, lon=-80.0, delta=0.004)
    _seed_non_network_sources(tmp_path)
    first = generate_top_loops(
        {"near": "Roanoke, VA", "miles_min": 0.8, "miles_max": 1.5, "difficulty": "moderate"}
    )
    assert first["routes"]
    assert 0.8 <= first["routes"][0]["distance_miles"] <= 1.5

    _write_cycle_osm(osm_path, lat=40.0, lon=-105.0, delta=0.010)
    second = generate_top_loops(
        {"near": "Boulder, CO", "miles_min": 2.0, "miles_max": 3.5, "difficulty": "moderate"}
    )
    assert second["routes"]
    assert 2.0 <= second["routes"][0]["distance_miles"] <= 3.5
    assert second["routes"][0]["score"] >= 0.0

