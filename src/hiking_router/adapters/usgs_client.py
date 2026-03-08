class USGSClient:
    def fetch_dem(self, bbox: tuple[float, float, float, float]) -> dict:
        _ = bbox
        return {"raster": None, "meta": {}}
