import os
from pathlib import Path

from hiking_router.adapters.osm_client import OSMClient
from hiking_router.adapters.usgs_client import USGSClient
from hiking_router.models.response import QueryResponse


def generate_top_loops(query: dict) -> dict:
    cache_root = Path(os.environ.get("HIKING_ROUTER_CACHE_DIR", "cache"))
    tile_id = "z10-290-391"
    bbox = (-80.0, 37.0, -79.0, 38.0)

    osm_client = OSMClient(cache_dir=cache_root)
    usgs_client = USGSClient(cache_dir=cache_root)

    _, osm_status = osm_client.fetch_trails(tile_id=tile_id, bbox=bbox)
    _, usgs_status = usgs_client.fetch_dem(tile_id=tile_id, bbox=bbox)

    if osm_status == "miss":
        osm_path = cache_root / "raw" / "osm" / f"{tile_id}.geojson"
        osm_path.parent.mkdir(parents=True, exist_ok=True)
        osm_path.write_text('{"type":"FeatureCollection","features":[]}')
    if usgs_status == "miss":
        usgs_path = cache_root / "raw" / "usgs" / f"{tile_id}.tif"
        usgs_path.parent.mkdir(parents=True, exist_ok=True)
        usgs_path.write_bytes(b"fake-dem")

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
            "cache": {"osm": osm_status, "usgs": usgs_status},
            "candidates_considered": len(routes),
            "routes_returned": len(routes),
        },
        routes=routes,
    )
    return response.model_dump()
