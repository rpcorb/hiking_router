from hiking_router.use_cases.generate_loop import generate_top_loops
from hiking_router.adapters.osm_client import OSMClient
from hiking_router.adapters.usgs_client import USGSClient
from hiking_router.config.providers import ProviderConfig


def test_meta_reason_present_when_partial_cache_used(tmp_path, monkeypatch):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(ProviderConfig, "from_env", classmethod(lambda cls, env: cls(
        osm_base_url="https://invalid.local/overpass",
        usgs_base_url="https://invalid.local/tnm",
    )))
    monkeypatch.setattr(
        OSMClient,
        "fetch_trails",
        lambda self, tile_id, bbox, force_live=False, strict_live=False: (
            {"type": "FeatureCollection", "features": []},
            "partial" if force_live else "hit",
        ),
    )
    monkeypatch.setattr(
        USGSClient,
        "fetch_dem",
        lambda self, tile_id, bbox, force_live=False, strict_live=False: (
            tmp_path / "raw" / "usgs" / f"{tile_id}.tif",
            "partial" if force_live else "hit",
        ),
    )
    _ = generate_top_loops({"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})

    payload = generate_top_loops({
        "near": "Roanoke, VA",
        "miles_min": 12,
        "miles_max": 15,
        "difficulty": "strenuous",
        "force_live": True,
    })

    assert payload["meta"]["cache"]["osm"] == "partial"
    assert payload["meta"]["cache"]["usgs"] == "partial"
    assert payload["meta"]["reason"] is not None
