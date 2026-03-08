from urllib.parse import urlencode

from hiking_router.providers.fetcher import http_get_text, parse_json_or_raise


def pick_first_download_url(payload: dict) -> str | None:
    items = payload.get("items", [])
    if not items:
        return None
    return items[0].get("downloadURL")


def fetch_tnm_download_url(
    bbox: tuple[float, float, float, float],
    base_url: str = "https://tnmaccess.nationalmap.gov/api/v1/products",
    timeout: int = 20,
    retries: int = 2,
    fetch_text_fn=http_get_text,
) -> str | None:
    min_lon, min_lat, max_lon, max_lat = bbox
    params = urlencode(
        {
            "bbox": f"{min_lon},{min_lat},{max_lon},{max_lat}",
            "outputFormat": "JSON",
        }
    )
    payload = fetch_text_fn(f"{base_url}?{params}", timeout=timeout, retries=retries)
    return pick_first_download_url(parse_json_or_raise(payload))
