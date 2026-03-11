from hiking_router.providers.gnis import fetch_gnis_summits


def test_fetch_gnis_summits_normalizes_items_to_point_features():
    def fake_fetch_text(_url, timeout=20, retries=2):
        _ = timeout, retries
        return (
            '{"items":['
            '{"featureId":"1","name":"Alpha Peak","latitude":37.5,"longitude":-79.5},'
            '{"featureId":"2","name":"Beta Peak","prim_lat_dec":"37.25","prim_long_dec":"-79.25"}]}'
        )

    payload = fetch_gnis_summits(
        bbox=(-80.0, 37.0, -79.0, 38.0),
        fetch_text_fn=fake_fetch_text,
    )

    assert payload["type"] == "FeatureCollection"
    assert len(payload["features"]) == 2
    assert payload["features"][0]["geometry"]["type"] == "Point"
    assert payload["features"][0]["properties"]["source"] == "gnis"


def test_fetch_gnis_summits_ignores_malformed_items():
    def fake_fetch_text(_url, timeout=20, retries=2):
        _ = timeout, retries
        return (
            '{"items":['
            '{"featureId":"1","name":"Good","latitude":37.5,"longitude":-79.5},'
            '{"featureId":"2","name":"BadMissingLat","longitude":-79.4},'
            '{"featureId":"3","name":"BadMissingLon","latitude":37.4}]}'
        )

    payload = fetch_gnis_summits(
        bbox=(-80.0, 37.0, -79.0, 38.0),
        fetch_text_fn=fake_fetch_text,
    )

    assert len(payload["features"]) == 1
    assert payload["features"][0]["properties"]["name"] == "Good"
