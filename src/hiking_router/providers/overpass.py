from hiking_router.providers.fetcher import http_post_form_text, parse_json_or_raise


def build_bbox_query(bbox: tuple[float, float, float, float]) -> str:
    min_lon, min_lat, max_lon, max_lat = bbox
    return (
        f"[out:json];(way[\"highway\"~\"path|footway|track\"]"
        f"({min_lat},{min_lon},{max_lat},{max_lon}););out body;>;out skel qt;"
    )


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
