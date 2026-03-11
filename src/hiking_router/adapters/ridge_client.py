import json
from pathlib import Path

from hiking_router.providers.fetcher import SourceUnavailableError


class RidgeClient:
    def __init__(
        self,
        cache_dir: Path = Path("cache"),
        fetch_ridges_fn=None,
    ) -> None:
        self.cache_dir = cache_dir
        self.fetch_ridges_fn = fetch_ridges_fn or (
            lambda _bbox: {"type": "FeatureCollection", "features": []}
        )

    def fetch_ridges(
        self,
        tile_id: str,
        bbox: tuple[float, float, float, float],
        force_live: bool = False,
        strict_live: bool = False,
    ) -> tuple[dict, str]:
        path = self.cache_dir / "raw" / "ridge" / f"{tile_id}.geojson"

        if not force_live and path.exists():
            return json.loads(path.read_text()), "hit"

        try:
            payload = self.fetch_ridges_fn(bbox)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload))
            return payload, "miss" if not force_live else "hit"
        except Exception:
            if path.exists():
                return json.loads(path.read_text()), "partial"
            if strict_live:
                raise SourceUnavailableError(
                    "Ridge live fetch failed and no cached artifact exists."
                )
            fallback = {"type": "FeatureCollection", "features": []}
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(fallback))
            return fallback, "miss"
