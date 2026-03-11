from hiking_router.providers.fetcher import http_post_form_text, parse_json_or_raise


def build_bbox_query(bbox: tuple[float, float, float, float]) -> str:
    min_lon, min_lat, max_lon, max_lat = bbox
    return (
        f"[out:json];(way[\"highway\"~\"path|footway|track\"]"
        f"({min_lat},{min_lon},{max_lat},{max_lon}););out body;>;out skel qt;"
    )


def build_ridge_query(bbox: tuple[float, float, float, float]) -> str:
    min_lon, min_lat, max_lon, max_lat = bbox
    return (
        f"[out:json];(way[\"natural\"=\"ridge\"]"
        f"({min_lat},{min_lon},{max_lat},{max_lon}););out body;>;out skel qt;"
    )


def build_summit_query(bbox: tuple[float, float, float, float]) -> str:
    min_lon, min_lat, max_lon, max_lat = bbox
    return (
        f"[out:json];(node[\"natural\"=\"peak\"]"
        f"({min_lat},{min_lon},{max_lat},{max_lon}););out body;"
    )


def _node_map(elements: list[dict]) -> dict[int, tuple[float, float]]:
    node_coords: dict[int, tuple[float, float]] = {}
    for element in elements:
        if (
            isinstance(element, dict)
            and element.get("type") == "node"
            and "id" in element
            and "lat" in element
            and "lon" in element
        ):
            node_coords[int(element["id"])] = (
                float(element["lat"]),
                float(element["lon"]),
            )
    return node_coords


def _normalize_ridges(payload: dict) -> dict:
    elements = payload.get("elements", [])
    if not isinstance(elements, list):
        elements = []

    node_coords = _node_map(elements)
    features: list[dict] = []

    for element in elements:
        if not isinstance(element, dict) or element.get("type") != "way":
            continue
        tags = element.get("tags", {}) or {}
        if tags.get("natural") != "ridge":
            continue
        nodes = element.get("nodes", [])
        if not isinstance(nodes, list):
            continue
        coords: list[list[float]] = []
        for node_id in nodes:
            try:
                lat, lon = node_coords[int(node_id)]
                coords.append([lon, lat])
            except Exception:
                continue
        if len(coords) < 2:
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coords},
                "properties": {"source": "overpass", "osm_way_id": element.get("id")},
            }
        )

    return {"type": "FeatureCollection", "features": features}


def _normalize_summits(payload: dict) -> dict:
    elements = payload.get("elements", [])
    if not isinstance(elements, list):
        elements = []
    features: list[dict] = []

    for element in elements:
        if not isinstance(element, dict) or element.get("type") != "node":
            continue
        tags = element.get("tags", {}) or {}
        if tags.get("natural") != "peak":
            continue
        if "lat" not in element or "lon" not in element:
            continue
        lat = float(element["lat"])
        lon = float(element["lon"])
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "source": "overpass",
                    "osm_node_id": element.get("id"),
                    "name": tags.get("name"),
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}


def fetch_overpass_geojson(
    bbox: tuple[float, float, float, float],
    base_url: str = "https://overpass-api.de/api/interpreter",
    timeout: int = 20,
    retries: int = 2,
    fetch_text_fn=http_post_form_text,
) -> dict:
    query = build_bbox_query(bbox)
    payload = fetch_text_fn(
        base_url, {"data": query}, timeout=timeout, retries=retries
    )
    return parse_json_or_raise(payload)


def fetch_overpass_ridges(
    bbox: tuple[float, float, float, float],
    base_url: str = "https://overpass-api.de/api/interpreter",
    timeout: int = 20,
    retries: int = 2,
    fetch_text_fn=http_post_form_text,
) -> dict:
    query = build_ridge_query(bbox)
    payload = fetch_text_fn(base_url, {"data": query}, timeout=timeout, retries=retries)
    return _normalize_ridges(parse_json_or_raise(payload))


def fetch_overpass_summits(
    bbox: tuple[float, float, float, float],
    base_url: str = "https://overpass-api.de/api/interpreter",
    timeout: int = 20,
    retries: int = 2,
    fetch_text_fn=http_post_form_text,
) -> dict:
    query = build_summit_query(bbox)
    payload = fetch_text_fn(base_url, {"data": query}, timeout=timeout, retries=retries)
    return _normalize_summits(parse_json_or_raise(payload))
