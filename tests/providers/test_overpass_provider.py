from hiking_router.providers.overpass import build_bbox_query


def test_build_bbox_query_contains_bbox_bounds():
    q = build_bbox_query((-80.0, 37.0, -79.0, 38.0))
    assert "37.0,-80.0,38.0,-79.0" in q
