import os
from pathlib import Path

from hiking_router.adapters.osm_client import OSMClient
from hiking_router.adapters.usgs_client import USGSClient
from hiking_router.config.providers import ProviderConfig
from hiking_router.features.dem_sampling import (
    profile_from_dem_artifact,
    route_elevation_metrics,
)
from hiking_router.graph.osm_normalize import extract_segment_edges
from hiking_router.models.response import QueryResponse
from hiking_router.providers.fetcher import SourceUnavailableError
from hiking_router.providers.fetcher import http_get_bytes
from hiking_router.providers.overpass import fetch_overpass_geojson
from hiking_router.providers.tnm import fetch_tnm_download_url


def generate_top_loops(query: dict) -> dict:
    cache_root = Path(os.environ.get("HIKING_ROUTER_CACHE_DIR", "cache"))
    cfg = ProviderConfig.from_env(dict(os.environ))
    tile_id = "z10-290-391"
    bbox = (-80.0, 37.0, -79.0, 38.0)

    force_live = bool(query.get("force_live", False))
    strict_live = bool(query.get("strict_live", False))
    osm_client = OSMClient(
        cache_dir=cache_root,
        fetch_trails_fn=lambda b: fetch_overpass_geojson(
            b,
            base_url=cfg.osm_base_url,
            timeout=cfg.timeout_seconds,
            retries=cfg.retry_count,
        ),
    )
    usgs_client = USGSClient(
        cache_dir=cache_root,
        fetch_download_url_fn=lambda b: fetch_tnm_download_url(
            b,
            base_url=cfg.usgs_base_url,
            timeout=cfg.timeout_seconds,
            retries=cfg.retry_count,
        ),
        download_bytes_fn=lambda url: http_get_bytes(
            url, timeout=cfg.timeout_seconds, retries=cfg.retry_count
        ),
    )

    try:
        osm_payload, osm_status = osm_client.fetch_trails(
            tile_id=tile_id,
            bbox=bbox,
            force_live=force_live,
            strict_live=strict_live,
        )
        dem_path, usgs_status = usgs_client.fetch_dem(
            tile_id=tile_id,
            bbox=bbox,
            force_live=force_live,
            strict_live=strict_live,
        )
    except SourceUnavailableError:
        response = QueryResponse(
            query=query,
            meta={
                "engine_version": "v2-osm-usgs",
                "cache": {"osm": "miss", "usgs": "miss"},
                "candidates_considered": 0,
                "routes_returned": 0,
                "reason": "Insufficient live source coverage and no cached data available.",
            },
            routes=[],
        )
        return response.model_dump()

    distance_miles = float(query.get("miles_min", 0))
    profile = profile_from_dem_artifact(dem_path)
    metrics = route_elevation_metrics(samples=profile, distance_miles=distance_miles)
    edges = extract_segment_edges(osm_payload)
    candidates_considered = max(1, len(edges))
    route_name = f"Loop near {query.get('near', 'unknown')} ({len(edges)} segments)"

    routes = [
        {
            "id": "prototype-roanoke-loop",
            "name": route_name,
            "distance_miles": distance_miles,
            "elevation_gain_ft": metrics["gain_ft"],
            "elevation_gain_per_mile_ft": metrics["gain_per_mile_ft"],
            "difficulty": query.get("difficulty", "unknown"),
            "score": 0.5,
            "terrain": {
                "ridge_fraction": None,
                "summit_proximity_min_m": None,
                "scenic_score": None,
            },
        }
    ]
    reason = None
    if osm_status == "partial" or usgs_status == "partial":
        reason = "Live fetch failed; serving cached source artifacts."

    response = QueryResponse(
        query=query,
        meta={
            "engine_version": "v2-osm-usgs",
            "cache": {"osm": osm_status, "usgs": usgs_status},
            "candidates_considered": candidates_considered,
            "routes_returned": len(routes),
            "reason": reason,
        },
        routes=routes,
    )
    return response.model_dump()
