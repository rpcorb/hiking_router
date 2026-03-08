from hiking_router.adapters.osm_client import OSMClient


def test_osm_client_reads_cached_geojson_without_network(tmp_path):
    client = OSMClient(cache_dir=tmp_path)
    tile_id = "z10-290-391"
    path = tmp_path / "raw" / "osm" / f"{tile_id}.geojson"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"type":"FeatureCollection","features":[]}')

    data, status = client.fetch_trails(tile_id=tile_id, bbox=(-80, 37, -79, 38))

    assert status == "hit"
    assert data["type"] == "FeatureCollection"
