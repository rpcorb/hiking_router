from urllib.parse import urlencode

from hiking_router.providers.fetcher import http_get_text, parse_json_or_raise


def _item_quality_score(item: dict) -> int:
    title = str(item.get("title", "")).lower()
    score = 0
    if "1/3 arc-second" in title or "10m" in title:
        score += 30
    if "1 arc-second" in title or "30m" in title:
        score += 20
    if "dem" in title or "elevation" in title:
        score += 10
    url = str(item.get("downloadURL", "")).lower()
    if url.endswith(".tif") or url.endswith(".tiff"):
        score += 5
    return score


def pick_best_download_url(payload: dict) -> str | None:
    items = payload.get("items", [])
    candidates = [item for item in items if item.get("downloadURL")]
    if not candidates:
        return None
    best = max(candidates, key=_item_quality_score)
    return str(best["downloadURL"])


def pick_first_download_url(payload: dict) -> str | None:
    # Backward-compatible alias used by older tests/callers.
    return pick_best_download_url(payload)


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
    return pick_best_download_url(parse_json_or_raise(payload))
