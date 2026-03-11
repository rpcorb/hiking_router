import json
from pathlib import Path

from hiking_router.providers.fetcher import SourceUnavailableError


def _feature_key(feature: dict) -> tuple[float, float, str]:
    geom = feature.get("geometry", {})
    coords = geom.get("coordinates", [0.0, 0.0])
    lon = round(float(coords[0]), 6)
    lat = round(float(coords[1]), 6)
    name = str((feature.get("properties") or {}).get("name") or "").strip().lower()
    return (lat, lon, name)


def _merge_dedupe_collections(collections: list[dict]) -> dict:
    merged: dict[tuple[float, float, str], dict] = {}
    for collection in collections:
        for feature in collection.get("features", []):
            geom = feature.get("geometry", {})
            if geom.get("type") != "Point":
                continue
            coords = geom.get("coordinates", [])
            if not isinstance(coords, list) or len(coords) < 2:
                continue
            key = _feature_key(feature)
            if key not in merged:
                merged[key] = feature
    return {"type": "FeatureCollection", "features": list(merged.values())}


class SummitAggregatorClient:
    def __init__(
        self,
        cache_dir: Path = Path("cache"),
        provider_fns: list | None = None,
    ) -> None:
        self.cache_dir = cache_dir
        self.provider_fns = provider_fns or [
            lambda _bbox: {"type": "FeatureCollection", "features": []}
        ]

    def fetch_summits(
        self,
        tile_id: str,
        bbox: tuple[float, float, float, float],
        force_live: bool = False,
        strict_live: bool = False,
    ) -> tuple[dict, str]:
        path = self.cache_dir / "raw" / "summit" / f"{tile_id}.geojson"

        if not force_live and path.exists():
            return json.loads(path.read_text()), "hit"

        collections: list[dict] = []
        provider_failed = False
        for idx, provider_fn in enumerate(self.provider_fns):
            try:
                payload = provider_fn(bbox)
            except Exception:
                provider_failed = True
                continue
            features = payload.get("features", [])
            collections.append(payload)
            if features and not force_live and idx == 0:
                break

        try:
            if provider_failed and not collections and path.exists():
                return json.loads(path.read_text()), "partial"
            merged = _merge_dedupe_collections(collections)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(merged))
            if provider_failed and path.exists():
                return merged, "partial" if force_live else "miss"
            return merged, "miss" if not force_live else "hit"
        except Exception:
            if path.exists():
                return json.loads(path.read_text()), "partial"
            if strict_live:
                raise SourceUnavailableError(
                    "Summit live fetch failed and no cached artifact exists."
                )
            fallback = {"type": "FeatureCollection", "features": []}
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(fallback))
            return fallback, "miss"
