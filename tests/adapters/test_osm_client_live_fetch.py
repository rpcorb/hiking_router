from hiking_router.adapters.osm_client import OSMClient


def test_osm_client_fetches_live_on_miss_and_writes_cache(tmp_path):
    def fake_fetch(_bbox):
        return {"type": "FeatureCollection", "features": [{"id": 1}]}

    client = OSMClient(cache_dir=tmp_path, fetch_trails_fn=fake_fetch)

    data, status = client.fetch_trails(tile_id="z10-290-391", bbox=(-80, 37, -79, 38))

    assert status == "miss"
    assert data["features"][0]["id"] == 1
    assert (tmp_path / "raw" / "osm" / "z10-290-391.geojson").exists()
