from hiking_router.models.response import QueryResponse


def generate_top_loops(query: dict) -> dict:
    routes = [
        {
            "id": "prototype-roanoke-loop",
            "name": f"Prototype loop near {query.get('near', 'unknown')}",
            "distance_miles": float(query.get("miles_min", 0)),
            "elevation_gain_ft": 0.0,
            "elevation_gain_per_mile_ft": 0.0,
            "difficulty": query.get("difficulty", "unknown"),
            "score": 0.5,
            "terrain": {
                "ridge_fraction": None,
                "summit_proximity_min_m": None,
                "scenic_score": None,
            },
        }
    ]
    response = QueryResponse(
        query=query,
        meta={
            "engine_version": "v2-osm-usgs",
            "cache": {"osm": "miss", "usgs": "miss"},
            "candidates_considered": len(routes),
            "routes_returned": len(routes),
        },
        routes=routes,
    )
    return response.model_dump()
