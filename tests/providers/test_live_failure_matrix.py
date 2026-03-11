from hiking_router.use_cases.generate_loop import generate_top_loops


def _write_cycle(path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '{"elements":['
        '{"type":"node","id":1,"lat":37.0,"lon":-80.0},'
        '{"type":"node","id":2,"lat":37.001,"lon":-80.0},'
        '{"type":"node","id":3,"lat":37.001,"lon":-80.001},'
        '{"type":"node","id":4,"lat":37.0,"lon":-80.001},'
        '{"type":"way","id":10,"nodes":[1,2,3,4,1],"tags":{"highway":"path"}}]}'
    )


def test_strict_live_without_cache_returns_insufficient_data(tmp_path, monkeypatch):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))
    monkeypatch.setenv("HIKING_ROUTER_DISABLE_NETWORK", "1")

    payload = generate_top_loops(
        {
            "near": "Roanoke, VA",
            "miles_min": 1.0,
            "miles_max": 2.0,
            "difficulty": "moderate",
            "force_live": True,
            "strict_live": True,
        }
    )

    assert payload["routes"] == []
    assert payload["meta"]["reason"] is not None


def test_force_live_with_cache_reports_partial_when_network_unavailable(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))
    monkeypatch.setenv("HIKING_ROUTER_DISABLE_NETWORK", "1")

    osm_path = tmp_path / "raw" / "osm" / "z10-290-391.geojson"
    _write_cycle(osm_path)
    usgs_path = tmp_path / "raw" / "usgs" / "z10-290-391.tif"
    usgs_path.parent.mkdir(parents=True, exist_ok=True)
    usgs_path.write_bytes(b"dem")

    payload = generate_top_loops(
        {
            "near": "Roanoke, VA",
            "miles_min": 0.1,
            "miles_max": 1.0,
            "difficulty": "moderate",
            "force_live": True,
            "strict_live": False,
        }
    )

    assert payload["routes"]
    assert payload["meta"]["cache"]["osm"] == "partial"
    assert payload["meta"]["cache"]["usgs"] == "partial"
    assert payload["meta"]["reason"] is not None

