from pathlib import Path


class USGSClient:
    def __init__(self, cache_dir: Path = Path("cache")) -> None:
        self.cache_dir = cache_dir

    def fetch_dem(
        self, tile_id: str, bbox: tuple[float, float, float, float]
    ) -> tuple[Path, str]:
        _ = bbox
        path = self.cache_dir / "raw" / "usgs" / f"{tile_id}.tif"
        if path.exists():
            return path, "hit"
        return path, "miss"
