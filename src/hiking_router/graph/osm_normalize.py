import math


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def extract_segment_edges(payload: dict) -> list[dict]:
    elements = payload.get("elements", [])
    if not isinstance(elements, list):
        return []

    node_coords: dict[int, tuple[float, float]] = {}
    for el in elements:
        if not isinstance(el, dict):
            continue
        if el.get("type") != "node" or "lat" not in el or "lon" not in el:
            continue
        try:
            node_id = int(el["id"])
            node_coords[node_id] = (float(el["lat"]), float(el["lon"]))
        except (KeyError, TypeError, ValueError):
            continue

    edges: list[dict] = []
    for el in elements:
        if not isinstance(el, dict):
            continue
        if el.get("type") != "way":
            continue
        nodes = el.get("nodes", [])
        if not isinstance(nodes, list):
            continue
        for idx in range(len(nodes) - 1):
            try:
                n1 = int(nodes[idx])
                n2 = int(nodes[idx + 1])
            except (TypeError, ValueError):
                continue
            if n1 not in node_coords or n2 not in node_coords:
                continue
            lat1, lon1 = node_coords[n1]
            lat2, lon2 = node_coords[n2]
            edges.append(
                {
                    "edge_id": f"{el.get('id')}:{n1}:{n2}",
                    "from_node": str(n1),
                    "to_node": str(n2),
                    "length_m": _haversine_m(lat1, lon1, lat2, lon2),
                    "from_coord": (lat1, lon1),
                    "to_coord": (lat2, lon2),
                }
            )
    return edges
