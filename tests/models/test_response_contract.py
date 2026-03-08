from hiking_router.models.response import QueryResponse


def test_response_contract_requires_query_meta_routes():
    payload = QueryResponse(
        query={"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"},
        meta={"engine_version": "v2-osm-usgs", "cache": {"osm": "hit", "usgs": "miss"}, "candidates_considered": 3, "routes_returned": 1},
        routes=[],
    )
    assert payload.meta.engine_version == "v2-osm-usgs"
