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

### Current shape (placeholder)

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
        "scenic_score": null
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
- `routes[].terrain.summit_proximity_min_m` (`float | null`): Placeholder for summit-distance metric (planned in milestone B).
- `routes[].terrain.scenic_score` (`float | null`): Placeholder for weighted scenic score (planned in milestone C).

### Response guarantees

- Returns `0..3` ranked routes in `routes`.
- Output order is descending rank (best first).
- Top-level shape is stable and JSON-serializable.

### Terrain metric behavior

- `ridge_fraction` is populated in v4 milestone A.
- If ridge data is unavailable and `strict_live=false`, ridge cache falls back to an empty feature collection and `ridge_fraction` resolves to `0.0`.
- If ridge data is unavailable and `strict_live=true` with no cache artifact, request fails with source-unavailable behavior.

## Cache behavior

- First query in an area usually reports source cache `miss`.
- Repeated query in same area reports source cache `hit` or `partial`.
- Raw cache paths:
  - `cache/raw/osm/<tile>.geojson`
  - `cache/raw/ridge/<tile>.geojson`
  - `cache/raw/usgs/<tile>.tif`
- Derived cache paths:
  - `cache/derived/graph/<query-key>.json`
- With `force_live` semantics in use-case orchestration, live-source failure with existing cache results in `partial` status and `meta.reason`.

## Status and limitations

- OSM/USGS adapters currently implement cache-first local behavior with placeholder miss artifacts.
- Live fallback semantics are implemented: when forced live fetch degrades, cached artifacts are served and reason is surfaced.
- Search/scoring are still baseline implementations (full terrain-aware ranking is next).
- `ridge_fraction` is now computed; summit/scenic remain `null` until later milestones.

## Next optimization steps

1. Implement real OSM/USGS/ridge ingestion and tile persistence.
2. Build derived-feature preprocessing (gain/mi, ridge overlap, summit proximity, scenic factors).
3. Add bounded loop search heuristics and diversity filtering.
4. Introduce warm-cache benchmarking targets and profile hotspots.
