from hiking_router.cache.store import raw_osm_tile_path, raw_usgs_tile_path, derived_graph_path


def test_cache_paths_follow_layout():
    assert "cache/raw/osm" in str(raw_osm_tile_path("z10-290-391"))
    assert "cache/raw/usgs" in str(raw_usgs_tile_path("z10-290-391"))
    assert "cache/derived/graph" in str(derived_graph_path("qv:37.271:-79.941:30.0"))
