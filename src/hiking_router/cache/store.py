from dataclasses import dataclass


@dataclass(frozen=True)
class TileKey:
    dataset: str
    z: int
    x: int
    y: int

    def to_id(self) -> str:
        return f"{self.dataset}:z{self.z}:{self.x}:{self.y}"


@dataclass(frozen=True)
class QueryViewKey:
    lat: float
    lon: float
    radius_km: float

    def to_id(self) -> str:
        return f"qv:{self.lat:.4f}:{self.lon:.4f}:{self.radius_km:.1f}"
