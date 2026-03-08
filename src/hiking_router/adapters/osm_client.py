import json
from pathlib import Path

from hiking_router.providers.fetcher import SourceUnavailableError
from hiking_router.providers.overpass import fetch_overpass_geojson


class OSMClient:
    def __init__(
        self,
        cache_dir: Path = Path("cache"),
        fetch_trails_fn=fetch_overpass_geojson,
    ) -> None:
        self.cache_dir = cache_dir
        self.fetch_trails_fn = fetch_trails_fn

    def fetch_trails(
        self,
        tile_id: str,
        bbox: tuple[float, float, float, float],
        force_live: bool = False,
        strict_live: bool = False,
    ) -> tuple[dict, str]:
        path = self.cache_dir / "raw" / "osm" / f"{tile_id}.geojson"

        # Normal cache-first path.
        if not force_live and path.exists():
            return json.loads(path.read_text()), "hit"

        # Live fetch path used on miss or forced refresh.
        try:
            data = self.fetch_trails_fn(bbox)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data))
            return data, "miss" if not force_live else "hit"
        except Exception:
            if path.exists():
                return json.loads(path.read_text()), "partial"
            if strict_live:
                raise SourceUnavailableError(
                    "OSM live fetch failed and no cached artifact exists."
                )

            # Offline-safe fallback to avoid hard failure in local/dev mode.
            fallback = {"type": "FeatureCollection", "features": []}
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(fallback))
            return fallback, "miss"
