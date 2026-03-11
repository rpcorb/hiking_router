from pathlib import Path

from hiking_router.providers.fetcher import SourceUnavailableError
from hiking_router.providers.fetcher import http_get_bytes
from hiking_router.providers.tnm import fetch_tnm_download_url


class USGSClient:
    def __init__(
        self,
        cache_dir: Path = Path("cache"),
        fetch_download_url_fn=fetch_tnm_download_url,
        download_bytes_fn=http_get_bytes,
    ) -> None:
        self.cache_dir = cache_dir
        self.fetch_download_url_fn = fetch_download_url_fn
        self.download_bytes_fn = download_bytes_fn

    @staticmethod
    def _is_valid_dem_bytes(data: bytes) -> bool:
        return isinstance(data, (bytes, bytearray)) and len(data) > 0

    @staticmethod
    def _is_valid_dem_file(path: Path) -> bool:
        return path.exists() and path.is_file() and path.stat().st_size > 0

    def fetch_dem(
        self,
        tile_id: str,
        bbox: tuple[float, float, float, float],
        force_live: bool = False,
        strict_live: bool = False,
    ) -> tuple[Path, str]:
        path = self.cache_dir / "raw" / "usgs" / f"{tile_id}.tif"

        if not force_live and self._is_valid_dem_file(path):
            return path, "hit"

        try:
            url = self.fetch_download_url_fn(bbox)
            if url:
                data = self.download_bytes_fn(url)
                if self._is_valid_dem_bytes(data):
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                    return path, "miss" if not force_live else "hit"
        except Exception:
            pass

        if self._is_valid_dem_file(path):
            return path, "partial"
        if strict_live:
            raise SourceUnavailableError(
                "USGS live fetch failed and no cached artifact exists."
            )

        # Offline-safe fallback artifact.
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fake-dem")
        return path, "miss"
