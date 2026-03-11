from urllib.parse import urlencode

from hiking_router.providers.fetcher import http_get_text
from hiking_router.providers.fetcher import parse_json_or_raise


def _to_float(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_gnis_summits(payload: dict) -> dict:
    items = payload.get("items", [])
    if not isinstance(items, list):
        items = []

    features: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        lat = _to_float(item.get("latitude"))
        lon = _to_float(item.get("longitude"))
        if lat is None or lon is None:
            lat = _to_float(item.get("prim_lat_dec"))
            lon = _to_float(item.get("prim_long_dec"))
        if lat is None or lon is None:
            continue

        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "source": "gnis",
                    "name": item.get("name"),
                    "gnis_id": item.get("featureId") or item.get("feature_id"),
                },
            }
        )

    return {"type": "FeatureCollection", "features": features}


def fetch_gnis_summits(
    bbox: tuple[float, float, float, float],
    base_url: str = "https://carto.nationalmap.gov/arcgis/rest/services/geonames/MapServer/0/query",
    timeout: int = 20,
    retries: int = 2,
    fetch_text_fn=http_get_text,
) -> dict:
    min_lon, min_lat, max_lon, max_lat = bbox
    params = {
        "f": "json",
        "where": "1=1",
        "outFields": "featureId,name,prim_lat_dec,prim_long_dec,latitude,longitude",
        "geometry": f"{min_lon},{min_lat},{max_lon},{max_lat}",
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "returnGeometry": "false",
    }
    url = f"{base_url}?{urlencode(params)}"
    payload = fetch_text_fn(url, timeout=timeout, retries=retries)
    return _normalize_gnis_summits(parse_json_or_raise(payload))
