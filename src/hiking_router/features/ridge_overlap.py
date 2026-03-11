def _coord_key(coord: tuple[float, float]) -> tuple[float, float]:
    return (round(coord[0], 6), round(coord[1], 6))


def _ridge_segments(ridge_feature_collection: dict) -> set[frozenset[tuple[float, float]]]:
    segments: set[frozenset[tuple[float, float]]] = set()
    for feature in ridge_feature_collection.get("features", []):
        geom = feature.get("geometry", {})
        if geom.get("type") != "LineString":
            continue
        coords = geom.get("coordinates", [])
        for i in range(len(coords) - 1):
            c1 = coords[i]
            c2 = coords[i + 1]
            # GeoJSON coordinate order is [lon, lat]; normalize to (lat, lon)
            a = _coord_key((float(c1[1]), float(c1[0])))
            b = _coord_key((float(c2[1]), float(c2[0])))
            segments.add(frozenset((a, b)))
    return segments


def route_ridge_fraction(
    route_nodes: list[str],
    edge_details: dict[frozenset[str], dict],
    ridge_feature_collection: dict,
) -> float:
    if len(route_nodes) < 2:
        return 0.0

    ridge_segments = _ridge_segments(ridge_feature_collection)
    total_len = 0.0
    ridge_len = 0.0

    for idx, node in enumerate(route_nodes):
        nxt = route_nodes[(idx + 1) % len(route_nodes)]
        detail = edge_details.get(frozenset((node, nxt)))
        if not detail:
            continue
        seg_len = float(detail.get("length_m", 0.0))
        total_len += seg_len

        a = _coord_key(tuple(detail.get("from_coord")))
        b = _coord_key(tuple(detail.get("to_coord")))
        if frozenset((a, b)) in ridge_segments:
            ridge_len += seg_len

    if total_len <= 0:
        return 0.0
    return max(0.0, min(1.0, ridge_len / total_len))
