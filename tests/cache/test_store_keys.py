from hiking_router.cache.store import TileKey, QueryViewKey


def test_tile_and_query_keys_are_stable():
    tile = TileKey(dataset="osm", z=10, x=290, y=391)
    view = QueryViewKey(lat=37.271, lon=-79.941, radius_km=30.0)
    assert tile.to_id() == "osm:z10:290:391"
    assert view.to_id().startswith("qv:")
