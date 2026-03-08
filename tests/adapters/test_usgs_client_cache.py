from hiking_router.adapters.usgs_client import USGSClient


def test_usgs_client_reads_cached_dem_without_network(tmp_path):
    client = USGSClient(cache_dir=tmp_path)
    tile_id = "z10-290-391"
    path = tmp_path / "raw" / "usgs" / f"{tile_id}.tif"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"fake-dem")

    dem_path, status = client.fetch_dem(tile_id=tile_id, bbox=(-80, 37, -79, 38))

    assert status == "hit"
    assert dem_path.exists()
