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
    node_coords: dict[int, tuple[float, float]] = {}
    for el in elements:
        if el.get("type") == "node" and "lat" in el and "lon" in el:
            node_coords[int(el["id"])] = (float(el["lat"]), float(el["lon"]))

    edges: list[dict] = []
    for el in elements:
        if el.get("type") != "way":
            continue
        nodes = el.get("nodes", [])
        for idx in range(len(nodes) - 1):
            n1 = int(nodes[idx])
            n2 = int(nodes[idx + 1])
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
                }
            )
    return edges
