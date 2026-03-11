from hiking_router.adapters.summit_aggregator import SummitAggregatorClient


def test_summit_aggregator_prefers_primary_provider_when_features_exist(tmp_path):
    primary_calls = {"count": 0}
    fallback_calls = {"count": 0}

    def primary(_bbox):
        primary_calls["count"] += 1
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-79.5, 37.5]},
                    "properties": {"name": "Primary Peak", "source": "overpass"},
                }
            ],
        }

    def fallback(_bbox):
        fallback_calls["count"] += 1
        return {
            "type": "FeatureCollection",
            "features": [],
        }

    client = SummitAggregatorClient(
        cache_dir=tmp_path,
        provider_fns=[primary, fallback],
    )
    payload, status = client.fetch_summits(
        tile_id="z10-290-391",
        bbox=(-80.0, 37.0, -79.0, 38.0),
    )

    assert status == "miss"
    assert len(payload["features"]) == 1
    assert primary_calls["count"] == 1
    assert fallback_calls["count"] == 0


def test_summit_aggregator_falls_back_when_primary_raises(tmp_path):
    def primary(_bbox):
        raise RuntimeError("primary unavailable")

    def fallback(_bbox):
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-79.6, 37.6]},
                    "properties": {"name": "Fallback Peak", "source": "gnis"},
                }
            ],
        }

    client = SummitAggregatorClient(
        cache_dir=tmp_path,
        provider_fns=[primary, fallback],
    )
    payload, status = client.fetch_summits(
        tile_id="z10-290-391",
        bbox=(-80.0, 37.0, -79.0, 38.0),
    )

    assert status == "miss"
    assert len(payload["features"]) == 1
    assert payload["features"][0]["properties"]["name"] == "Fallback Peak"


def test_summit_aggregator_dedupes_points_from_multiple_providers(tmp_path):
    def primary(_bbox):
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-79.5, 37.5]},
                    "properties": {"name": "Shared Peak", "source": "overpass"},
                }
            ],
        }

    def fallback(_bbox):
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-79.5, 37.5]},
                    "properties": {"name": "Shared Peak", "source": "gnis"},
                }
            ],
        }

    client = SummitAggregatorClient(
        cache_dir=tmp_path,
        provider_fns=[primary, fallback],
    )
    payload, _ = client.fetch_summits(
        tile_id="z10-290-391",
        bbox=(-80.0, 37.0, -79.0, 38.0),
        force_live=True,
    )

    assert len(payload["features"]) == 1


def test_summit_aggregator_returns_partial_when_force_live_fails_with_cache(tmp_path):
    cache_path = tmp_path / "raw" / "summit" / "z10-290-391.geojson"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        '{"type":"FeatureCollection","features":'
        '[{"type":"Feature","geometry":{"type":"Point","coordinates":[-79.5,37.5]},"properties":{"name":"Cached"}}]}'
    )

    def primary(_bbox):
        raise RuntimeError("unavailable")

    client = SummitAggregatorClient(cache_dir=tmp_path, provider_fns=[primary])
    payload, status = client.fetch_summits(
        tile_id="z10-290-391",
        bbox=(-80.0, 37.0, -79.0, 38.0),
        force_live=True,
    )

    assert status == "partial"
    assert payload["features"][0]["properties"]["name"] == "Cached"
