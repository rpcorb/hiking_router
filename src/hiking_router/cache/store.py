from dataclasses import dataclass
from pathlib import Path


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


def raw_osm_tile_path(tile_id: str) -> Path:
    return Path("cache/raw/osm") / f"{tile_id}.geojson"


def raw_usgs_tile_path(tile_id: str) -> Path:
    return Path("cache/raw/usgs") / f"{tile_id}.tif"


def derived_graph_path(query_key: str) -> Path:
    safe = query_key.replace(":", "_")
    return Path("cache/derived/graph") / f"{safe}.json"
