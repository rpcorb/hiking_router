from pydantic import BaseModel


class ProviderConfig(BaseModel):
    osm_provider: str = "overpass"
    usgs_provider: str = "tnm"
    osm_base_url: str = "https://overpass-api.de/api/interpreter"
    usgs_base_url: str = "https://tnmaccess.nationalmap.gov/api/v1/products"
    timeout_seconds: int = 20
    retry_count: int = 3

    @classmethod
    def from_env(cls, env: dict[str, str]) -> "ProviderConfig":
        return cls(
            osm_provider=env.get("HIKING_ROUTER_OSM_PROVIDER", "overpass"),
            usgs_provider=env.get("HIKING_ROUTER_USGS_PROVIDER", "tnm"),
            osm_base_url=env.get("HIKING_ROUTER_OSM_BASE_URL", cls.model_fields["osm_base_url"].default),
            usgs_base_url=env.get("HIKING_ROUTER_USGS_BASE_URL", cls.model_fields["usgs_base_url"].default),
            timeout_seconds=int(env.get("HIKING_ROUTER_TIMEOUT_SECONDS", "20")),
            retry_count=int(env.get("HIKING_ROUTER_RETRY_COUNT", "3")),
        )
