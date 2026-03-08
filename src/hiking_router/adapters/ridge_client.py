class RidgeClient:
    def fetch_ridges(self, bbox: tuple[float, float, float, float]) -> dict:
        _ = bbox
        return {"type": "FeatureCollection", "features": []}
