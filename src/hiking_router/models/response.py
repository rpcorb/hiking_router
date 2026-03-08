from pydantic import BaseModel


class CacheMeta(BaseModel):
    osm: str
    usgs: str


class Meta(BaseModel):
    engine_version: str
    cache: CacheMeta
    candidates_considered: int
    routes_returned: int
    reason: str | None = None


class QueryResponse(BaseModel):
    query: dict
    meta: Meta
    routes: list[dict]
