from hiking_router.adapters.usgs_client import USGSClient


def test_usgs_client_fetches_live_on_miss_and_writes_cache(tmp_path):
    def fake_url(_bbox):
        return "https://example.test/dem.tif"

    def fake_download(_url):
        return b"real-dem-bytes"

    client = USGSClient(
        cache_dir=tmp_path,
        fetch_download_url_fn=fake_url,
        download_bytes_fn=fake_download,
    )

    dem_path, status = client.fetch_dem(tile_id="z10-290-391", bbox=(-80, 37, -79, 38))

    assert status == "miss"
    assert dem_path.exists()
    assert dem_path.read_bytes() == b"real-dem-bytes"
