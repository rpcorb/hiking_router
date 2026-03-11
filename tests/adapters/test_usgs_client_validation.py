import pytest

from hiking_router.adapters.usgs_client import USGSClient
from hiking_router.providers.fetcher import SourceUnavailableError


def test_usgs_client_does_not_treat_zero_byte_cache_as_hit(tmp_path):
    tile_id = "z10-290-391"
    path = tmp_path / "raw" / "usgs" / f"{tile_id}.tif"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")

    client = USGSClient(cache_dir=tmp_path)
    _, status = client.fetch_dem(tile_id=tile_id, bbox=(-80, 37, -79, 38))

    assert status == "miss"
    assert path.read_bytes() != b""


def test_usgs_client_raises_on_empty_live_download_in_strict_mode(tmp_path):
    def fake_url(_bbox):
        return "https://example.test/dem.tif"

    def empty_download(_url):
        return b""

    client = USGSClient(
        cache_dir=tmp_path,
        fetch_download_url_fn=fake_url,
        download_bytes_fn=empty_download,
    )

    with pytest.raises(SourceUnavailableError):
        client.fetch_dem(
            tile_id="z10-290-391",
            bbox=(-80, 37, -79, 38),
            force_live=True,
            strict_live=True,
        )

