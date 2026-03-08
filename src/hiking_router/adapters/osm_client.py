class OSMClient:
    def fetch_trails(self, bbox: tuple[float, float, float, float]) -> dict:
        _ = bbox
        return {"type": "FeatureCollection", "features": []}
