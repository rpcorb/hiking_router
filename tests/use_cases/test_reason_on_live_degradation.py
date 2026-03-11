from hiking_router.adapters.osm_client import OSMClient
from hiking_router.adapters.ridge_client import RidgeClient
from hiking_router.adapters.summit_aggregator import SummitAggregatorClient
from hiking_router.adapters.usgs_client import USGSClient
from hiking_router.use_cases.generate_loop import generate_top_loops


def test_meta_reason_includes_ridge_and_summit_when_live_refresh_degrades(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))

    monkeypatch.setattr(
        OSMClient,
        "fetch_trails",
        lambda self, tile_id, bbox, force_live=False, strict_live=False: (
            {
                "elements": [
                    {"type": "node", "id": 1, "lat": 37.0, "lon": -80.0},
                    {"type": "node", "id": 2, "lat": 37.001, "lon": -80.0},
                    {"type": "node", "id": 3, "lat": 37.001, "lon": -80.001},
                    {"type": "way", "id": 10, "nodes": [1, 2, 3, 1]},
                ]
            },
            "hit",
        ),
    )
    monkeypatch.setattr(
        RidgeClient,
        "fetch_ridges",
        lambda self, tile_id, bbox, force_live=False, strict_live=False: (
            {"type": "FeatureCollection", "features": []},
            "partial" if force_live else "hit",
        ),
    )
    monkeypatch.setattr(
        SummitAggregatorClient,
        "fetch_summits",
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
            "hit",
        ),
    )
    (tmp_path / "raw" / "usgs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "raw" / "usgs" / "z10-290-391.tif").write_bytes(b"dem")

    payload = generate_top_loops(
        {
            "near": "Roanoke, VA",
            "miles_min": 0.2,
            "miles_max": 1.0,
            "difficulty": "moderate",
            "force_live": True,
        }
    )

    assert payload["meta"]["reason"] is not None
    assert "ridge" in payload["meta"]["reason"].lower()
    assert "summit" in payload["meta"]["reason"].lower()
