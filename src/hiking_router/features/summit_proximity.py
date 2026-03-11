import math


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def _summit_points(summit_feature_collection: dict) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for feature in summit_feature_collection.get("features", []):
        geom = feature.get("geometry", {})
        if geom.get("type") != "Point":
            continue
        coord = geom.get("coordinates", [])
        if len(coord) < 2:
            continue
        lon, lat = float(coord[0]), float(coord[1])
        points.append((lat, lon))
    return points


def route_summit_proximity_min_m(
    route_nodes: list[str],
    edge_details: dict[frozenset[str], dict],
    summit_feature_collection: dict,
) -> float | None:
    if len(route_nodes) < 2:
        return None

    summit_points = _summit_points(summit_feature_collection)
    if not summit_points:
        return None

    route_points: list[tuple[float, float]] = []
    for idx, node in enumerate(route_nodes):
        nxt = route_nodes[(idx + 1) % len(route_nodes)]
        detail = edge_details.get(frozenset((node, nxt)))
        if not detail:
            continue
        route_points.append(tuple(detail.get("from_coord")))
        route_points.append(tuple(detail.get("to_coord")))

    if not route_points:
        return None

    min_distance = None
    for route_lat, route_lon in route_points:
        for summit_lat, summit_lon in summit_points:
            distance = _haversine_m(route_lat, route_lon, summit_lat, summit_lon)
            if min_distance is None or distance < min_distance:
                min_distance = distance
    return min_distance

