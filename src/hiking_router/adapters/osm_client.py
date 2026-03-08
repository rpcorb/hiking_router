import json
from pathlib import Path


class OSMClient:
    def __init__(self, cache_dir: Path = Path("cache")) -> None:
        self.cache_dir = cache_dir

    def fetch_trails(
        self, tile_id: str, bbox: tuple[float, float, float, float]
    ) -> tuple[dict, str]:
        _ = bbox
        path = self.cache_dir / "raw" / "osm" / f"{tile_id}.geojson"
        if path.exists():
            return json.loads(path.read_text()), "hit"
        return {"type": "FeatureCollection", "features": []}, "miss"
