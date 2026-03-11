# hiking_router

Terrain-aware hiking route generator (CLI-first).

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install pytest typer pydantic networkx
```

Provider config is environment-driven (v3):
- `HIKING_ROUTER_OSM_PROVIDER` (default: `overpass`)
- `HIKING_ROUTER_USGS_PROVIDER` (default: `tnm`)
- `HIKING_ROUTER_OSM_BASE_URL`
- `HIKING_ROUTER_USGS_BASE_URL`
- `HIKING_ROUTER_TIMEOUT_SECONDS` (default: `20`)
- `HIKING_ROUTER_RETRY_COUNT` (default: `3`)

## Run tests

```bash
. .venv/bin/activate
PYTHONPATH=src python -m pytest -v
```

## CLI usage

```bash
. .venv/bin/activate
PYTHONPATH=src python -m hiking_router.cli --help
PYTHONPATH=src python -m hiking_router.cli generate-loop \
  --near "Roanoke, VA" \
  --miles-min 12 \
  --miles-max 15 \
  --difficulty strenuous
```

CLI returns a JSON envelope with `query`, `meta`, and `routes`.

## Response contract

`generate-loop` prints JSON (`dict`) to stdout.

### Current shape

```json
{
  "query": {
    "near": "Roanoke, VA",
    "miles_min": 12.0,
    "miles_max": 15.0,
    "difficulty": "strenuous"
  },
  "meta": {
    "engine_version": "v2-osm-usgs",
    "cache": {
      "osm": "hit",
      "usgs": "hit"
    },
    "candidates_considered": 1,
    "routes_returned": 1,
    "reason": null
  },
  "routes": [
    {
      "id": "prototype-roanoke-loop",
      "name": "Prototype loop near Roanoke, VA",
      "distance_miles": 12.0,
      "elevation_gain_ft": 0.0,
      "elevation_gain_per_mile_ft": 0.0,
      "difficulty": "strenuous",
      "score": 0.5,
      "terrain": {
        "ridge_fraction": 0.0,
        "summit_proximity_min_m": null,
        "scenic_score": 0.0
      }
    }
  ]
}
```

### Current attributes

- `query` (`dict`): Echo of normalized request parameters.
- `meta.engine_version` (`str`): Response schema/engine marker (`v2-osm-usgs`).
- `meta.cache` (`dict`): Source cache statuses for `osm` and `usgs` (`hit|miss|partial`).
- `meta.candidates_considered` (`int`): Number of candidate routes scored before truncation.
- `meta.routes_returned` (`int`): Number of routes returned in `routes`.
- `meta.reason` (`str | null`): Optional explanation when no qualifying routes are returned.
- `routes[].id` (`str`): Stable route identifier.
- `routes[].name` (`str`): Human-readable route label.
- `routes[].distance_miles` (`float`): Route distance in miles.
- `routes[].elevation_gain_ft` (`float`): Total ascent in feet.
- `routes[].elevation_gain_per_mile_ft` (`float`): Ascent intensity in feet per mile.
- `routes[].difficulty` (`str`): Difficulty class for the returned route.
- `routes[].score` (`float`): Composite ranking score in `[0.0, 1.0]`.
- `routes[].terrain.ridge_fraction` (`float`): Fraction of route distance overlapping ridge segments, normalized to `[0.0, 1.0]`.
- `routes[].terrain.summit_proximity_min_m` (`float | null`): Minimum summit distance from route geometry in meters (null when summit dataset has no points).
- `routes[].terrain.scenic_score` (`float`): Weighted normalized score in `[0.0, 1.0]` derived from ridge overlap, summit proximity, and elevation intensity.

### Response guarantees

- Returns `0..3` ranked routes in `routes`.
- Output order is descending rank (best first).
- Top-level shape is stable and JSON-serializable.

### Terrain metric behavior

- `ridge_fraction` is populated in v4 milestone A.
- `summit_proximity_min_m` is populated in v4 milestone B when summit points are present; otherwise `null`.
- `scenic_score` is populated in v4 milestone C and is deterministic for fixed input data.
- Ridge live ingestion uses Overpass ridge ways.
- Summit live ingestion uses provider priority `Overpass -> GNIS` with merge+dedupe.
- If ridge data is unavailable and `strict_live=false`, ridge cache falls back to an empty feature collection and `ridge_fraction` resolves to `0.0`.
- If ridge data is unavailable and `strict_live=true` with no cache artifact, request fails with source-unavailable behavior.
- With `force_live=true`, any degraded source refresh returns routes when possible and sets `meta.reason` listing degraded sources (`osm`, `ridge`, `summit`, `usgs`).
- Elevation metrics are sampled from DEM along per-route geometry when route coordinates are available.
- Scenic defaults can be overridden with:
  - `HIKING_ROUTER_SCENIC_WEIGHT_RIDGE`
  - `HIKING_ROUTER_SCENIC_WEIGHT_SUMMIT`
  - `HIKING_ROUTER_SCENIC_WEIGHT_ELEVATION`
  - `HIKING_ROUTER_SCENIC_SUMMIT_MAX_DISTANCE_M`
  - `HIKING_ROUTER_SCENIC_ELEVATION_SCALE_FT_PER_MILE`

## Cache behavior

- First query in an area usually reports source cache `miss`.
- Repeated query in same area reports source cache `hit` or `partial`.
- Raw cache paths:
  - `cache/raw/osm/<tile>.geojson`
  - `cache/raw/ridge/<tile>.geojson`
  - `cache/raw/summit/<tile>.geojson`
  - `cache/raw/usgs/<tile>.tif`
- Derived cache paths:
  - `cache/derived/graph/<query-key>.json`
- With `force_live` semantics in use-case orchestration, live-source failure with existing cache results in `partial` status and `meta.reason`.

## Status and limitations

- OSM/USGS/ridge/summit adapters implement cache-first behavior with live fetch refresh paths.
- Live fallback semantics are implemented: when forced live fetch degrades, cached artifacts are served and reason is surfaced.
- Search/scoring include distance fit, difficulty fit, terrain fit, diversity filtering, and sustained-grade penalty.
- `ridge_fraction` and `scenic_score` are computed; `summit_proximity_min_m` is computed when summit features exist.
- Warm-cache performance budgets are enforced via `tests/perf/test_query_budget.py` and `tests/perf/test_warm_cache_latency.py`.

## Next optimization steps

1. Expand ridge/summit coverage quality with region-aware query tuning.
2. Add richer DEM sampling controls (spacing, smoothing, outlier handling).
3. Add provider-level health/metrics reporting in CLI meta output.
4. Profile and optimize larger-area graph construction workloads.
