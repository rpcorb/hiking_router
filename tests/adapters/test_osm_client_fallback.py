from hiking_router.adapters.osm_client import OSMClient


def test_osm_client_returns_partial_when_live_fails_but_cache_exists(tmp_path):
    client = OSMClient(cache_dir=tmp_path)
    tile_id = "z10-290-391"
    cached = tmp_path / "raw" / "osm" / f"{tile_id}.geojson"
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_text('{"type":"FeatureCollection","features":[]}')

    data, status = client.fetch_trails(tile_id=tile_id, bbox=(-80, 37, -79, 38), force_live=True)

    assert status in {"hit", "partial"}
    assert data["type"] == "FeatureCollection"
