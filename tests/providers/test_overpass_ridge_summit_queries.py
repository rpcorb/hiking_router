from hiking_router.providers.overpass import build_ridge_query
from hiking_router.providers.overpass import build_summit_query
from hiking_router.providers.overpass import fetch_overpass_ridges
from hiking_router.providers.overpass import fetch_overpass_summits


def test_build_ridge_query_contains_bbox_and_natural_ridge_tag():
    q = build_ridge_query((-80.0, 37.0, -79.0, 38.0))
    assert "37.0,-80.0,38.0,-79.0" in q
    assert 'way["natural"="ridge"]' in q


def test_build_summit_query_contains_bbox_and_natural_peak_tag():
    q = build_summit_query((-80.0, 37.0, -79.0, 38.0))
    assert "37.0,-80.0,38.0,-79.0" in q
    assert 'node["natural"="peak"]' in q


def test_fetch_overpass_ridges_normalizes_ways_to_linestring_features():
    def fake_fetch_text(_url, _form, timeout=20, retries=2):
        _ = timeout, retries
        return (
            '{"elements":['
            '{"type":"node","id":1,"lat":37.0,"lon":-80.0},'
            '{"type":"node","id":2,"lat":37.001,"lon":-80.001},'
            '{"type":"way","id":10,"nodes":[1,2],"tags":{"natural":"ridge"}}]}'
        )

    payload = fetch_overpass_ridges(
        bbox=(-80.0, 37.0, -79.0, 38.0),
        fetch_text_fn=fake_fetch_text,
    )

    assert payload["type"] == "FeatureCollection"
    assert len(payload["features"]) == 1
    feature = payload["features"][0]
    assert feature["geometry"]["type"] == "LineString"
    assert feature["geometry"]["coordinates"][0] == [-80.0, 37.0]


def test_fetch_overpass_summits_normalizes_peak_nodes_to_point_features():
    def fake_fetch_text(_url, _form, timeout=20, retries=2):
        _ = timeout, retries
        return (
            '{"elements":['
            '{"type":"node","id":101,"lat":37.5,"lon":-79.5,"tags":{"natural":"peak","name":"Foo Peak"}}]}'
        )

    payload = fetch_overpass_summits(
        bbox=(-80.0, 37.0, -79.0, 38.0),
        fetch_text_fn=fake_fetch_text,
    )

    assert payload["type"] == "FeatureCollection"
    assert len(payload["features"]) == 1
    feature = payload["features"][0]
    assert feature["geometry"]["type"] == "Point"
    assert feature["geometry"]["coordinates"] == [-79.5, 37.5]
    assert feature["properties"]["name"] == "Foo Peak"
