import os
from pathlib import Path

import networkx as nx
from hiking_router.adapters.osm_client import OSMClient
from hiking_router.adapters.ridge_client import RidgeClient
from hiking_router.adapters.summit_aggregator import SummitAggregatorClient
from hiking_router.adapters.usgs_client import USGSClient
from hiking_router.config.providers import ProviderConfig
from hiking_router.config.scoring import ScenicConfig
from hiking_router.features.dem_sampling import (
    profile_from_dem_route_geometry,
    profile_from_dem_artifact,
    route_elevation_metrics,
)
from hiking_router.features.ridge_overlap import route_ridge_fraction
from hiking_router.features.summit_proximity import route_summit_proximity_min_m
from hiking_router.graph.osm_normalize import extract_segment_edges
from hiking_router.models.response import QueryResponse
from hiking_router.providers.fetcher import SourceUnavailableError, http_get_bytes
from hiking_router.providers.gnis import fetch_gnis_summits
from hiking_router.providers.overpass import fetch_overpass_geojson
from hiking_router.providers.overpass import fetch_overpass_ridges
from hiking_router.providers.overpass import fetch_overpass_summits
from hiking_router.providers.tnm import fetch_tnm_download_url
from hiking_router.scoring.composite import composite_score
from hiking_router.scoring.composite import difficulty_fit_score
from hiking_router.scoring.composite import distance_fit_score
from hiking_router.scoring.composite import sustained_grade_penalty
from hiking_router.scoring.scenic import scenic_score
from hiking_router.search.diversity import select_diverse_loops
from hiking_router.search.loop_search import filter_loops_by_distance_band, find_loops


def _loop_length_miles(loop: list[str], edge_lengths_m: dict[frozenset[str], float]) -> float:
    total_m = 0.0
    for idx, node in enumerate(loop):
        nxt = loop[(idx + 1) % len(loop)]
        total_m += edge_lengths_m.get(frozenset((node, nxt)), 0.0)
    return total_m / 1609.34


def _loop_route_points(
    loop: list[str],
    edge_details: dict[frozenset[str], dict],
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for idx, node in enumerate(loop):
        nxt = loop[(idx + 1) % len(loop)]
        detail = edge_details.get(frozenset((node, nxt)))
        if not detail:
            continue
        from_coord = tuple(detail.get("from_coord"))
        to_coord = tuple(detail.get("to_coord"))
        if not points:
            points.append(from_coord)
        points.append(to_coord)
    return points


def generate_top_loops(query: dict) -> dict:
    cache_root = Path(os.environ.get("HIKING_ROUTER_CACHE_DIR", "cache"))
    cfg = ProviderConfig.from_env(dict(os.environ))
    scenic_cfg = ScenicConfig.from_env(dict(os.environ))
    tile_id = "z10-290-391"
    bbox = (-80.0, 37.0, -79.0, 38.0)

    force_live = bool(query.get("force_live", False))
    strict_live = bool(query.get("strict_live", False))
    miles_min = float(query.get("miles_min", 0))
    miles_max = float(query.get("miles_max", miles_min))

    osm_client = OSMClient(
        cache_dir=cache_root,
        fetch_trails_fn=lambda b: fetch_overpass_geojson(
            b,
            base_url=cfg.osm_base_url,
            timeout=cfg.timeout_seconds,
            retries=cfg.retry_count,
        ),
    )
    ridge_client = RidgeClient(
        cache_dir=cache_root,
        fetch_ridges_fn=lambda b: fetch_overpass_ridges(
            b,
            base_url=cfg.osm_base_url,
            timeout=cfg.timeout_seconds,
            retries=cfg.retry_count,
        ),
    )
    summit_client = SummitAggregatorClient(
        cache_dir=cache_root,
        provider_fns=[
            lambda b: fetch_overpass_summits(
                b,
                base_url=cfg.osm_base_url,
                timeout=cfg.timeout_seconds,
                retries=cfg.retry_count,
            ),
            lambda b: fetch_gnis_summits(
                b,
                timeout=cfg.timeout_seconds,
                retries=cfg.retry_count,
            ),
        ],
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
        ridge_payload, ridge_status = ridge_client.fetch_ridges(
            tile_id=tile_id,
            bbox=bbox,
            force_live=force_live,
            strict_live=strict_live,
        )
        summit_payload, summit_status = summit_client.fetch_summits(
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

    edges = extract_segment_edges(osm_payload)
    candidates_considered = max(1, len(edges))

    graph = nx.Graph()
    edge_lengths_m: dict[frozenset[str], float] = {}
    edge_details: dict[frozenset[str], dict] = {}
    for edge in edges:
        u = edge["from_node"]
        v = edge["to_node"]
        length_m = float(edge["length_m"])
        graph.add_edge(u, v, length_m=length_m)
        key = frozenset((u, v))
        edge_lengths_m[key] = length_m
        edge_details[key] = {
            "length_m": length_m,
            "from_coord": tuple(edge["from_coord"]),
            "to_coord": tuple(edge["to_coord"]),
        }

    loops: list[list[str]] = []
    lengths: dict[tuple[str, ...], float] = {}
    if graph.number_of_nodes() > 0:
        start = next(iter(graph.nodes))
        loops = find_loops(graph, start=start, max_loops=50)
        for loop in loops:
            lengths[tuple(loop)] = _loop_length_miles(loop, edge_lengths_m)

    selected_loops = filter_loops_by_distance_band(
        loops, lengths, miles_min=miles_min, miles_max=miles_max
    )
    selected_loops = select_diverse_loops(
        candidates=selected_loops,
        max_loops=10,
        max_similarity=0.75,
    )

    default_profile = profile_from_dem_artifact(dem_path)
    routes: list[dict] = []
    for loop in selected_loops:
        loop_miles = lengths.get(tuple(loop), miles_min)
        route_points = _loop_route_points(loop, edge_details=edge_details)
        profile = profile_from_dem_route_geometry(dem_path, route_points)
        metrics = route_elevation_metrics(samples=profile, distance_miles=loop_miles)
        ridge_frac = route_ridge_fraction(
            route_nodes=loop,
            edge_details=edge_details,
            ridge_feature_collection=ridge_payload,
        )
        summit_proximity = route_summit_proximity_min_m(
            route_nodes=loop,
            edge_details=edge_details,
            summit_feature_collection=summit_payload,
        )
        distance_fit = distance_fit_score(
            loop_miles=loop_miles,
            miles_min=miles_min,
            miles_max=miles_max,
        )
        difficulty_fit = difficulty_fit_score(
            gain_per_mile_ft=metrics["gain_per_mile_ft"],
            difficulty=query.get("difficulty", "unknown"),
        )
        grade_penalty = sustained_grade_penalty(
            gain_per_mile_ft=metrics["gain_per_mile_ft"],
            difficulty=query.get("difficulty", "unknown"),
        )
        score = composite_score(
            distance_fit=distance_fit,
            difficulty_fit=difficulty_fit,
            terrain_fit=max(
                0.3,
                scenic_score(
                    ridge_fraction=ridge_frac,
                    summit_proximity_min_m=summit_proximity,
                    elevation_gain_per_mile_ft=metrics["gain_per_mile_ft"],
                    cfg=scenic_cfg,
                ),
            ),
            penalties=grade_penalty,
        )
        scenic_value = scenic_score(
            ridge_fraction=ridge_frac,
            summit_proximity_min_m=summit_proximity,
            elevation_gain_per_mile_ft=metrics["gain_per_mile_ft"],
            cfg=scenic_cfg,
        )
        routes.append(
            {
                "id": "loop-candidate",
                "name": f"Loop near {query.get('near', 'unknown')} ({len(loop)} nodes)",
                "distance_miles": loop_miles,
                "elevation_gain_ft": metrics["gain_ft"],
                "elevation_gain_per_mile_ft": metrics["gain_per_mile_ft"],
                "difficulty": query.get("difficulty", "unknown"),
                "score": score,
                "terrain": {
                    "ridge_fraction": ridge_frac,
                    "summit_proximity_min_m": summit_proximity,
                    "scenic_score": scenic_value,
                },
            }
        )
    routes.sort(key=lambda route: route["score"], reverse=True)
    routes = routes[:3]
    for idx, route in enumerate(routes, start=1):
        route["id"] = f"loop-{idx}"

    if not routes:
        metrics = route_elevation_metrics(samples=default_profile, distance_miles=miles_min)
        routes = [
            {
                "id": "prototype-roanoke-loop",
                "name": f"Loop near {query.get('near', 'unknown')} ({len(edges)} segments)",
                "distance_miles": miles_min,
                "elevation_gain_ft": metrics["gain_ft"],
                "elevation_gain_per_mile_ft": metrics["gain_per_mile_ft"],
                "difficulty": query.get("difficulty", "unknown"),
                "score": 0.5,
                "terrain": {
                    "ridge_fraction": 0.0,
                    "summit_proximity_min_m": None,
                    "scenic_score": scenic_score(
                        ridge_fraction=0.0,
                        summit_proximity_min_m=None,
                        elevation_gain_per_mile_ft=metrics["gain_per_mile_ft"],
                        cfg=scenic_cfg,
                    ),
                },
            }
        ]

    reason = None
    degraded_sources: list[str] = []
    if osm_status == "partial":
        degraded_sources.append("osm")
    if ridge_status == "partial":
        degraded_sources.append("ridge")
    if summit_status == "partial":
        degraded_sources.append("summit")
    if usgs_status == "partial":
        degraded_sources.append("usgs")
    if degraded_sources:
        source_list = ", ".join(degraded_sources)
        reason = f"Live fetch degraded for: {source_list}; serving cached/fallback artifacts."

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
