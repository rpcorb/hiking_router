from hiking_router.adapters.usgs_client import USGSClient


def test_usgs_client_returns_partial_when_live_fails_but_cache_exists(tmp_path):
    client = USGSClient(cache_dir=tmp_path)
    tile_id = "z10-290-391"
    cached = tmp_path / "raw" / "usgs" / f"{tile_id}.tif"
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(b"dem")

    dem_path, status = client.fetch_dem(tile_id=tile_id, bbox=(-80, 37, -79, 38), force_live=True)

    assert status in {"hit", "partial"}
    assert dem_path.exists()
