# V2 OSM + USGS Real-Data Routing Design

Date: 2026-03-08
Status: Approved
Scope: Real OSM trail graph + USGS elevation gain routing with cache-first on-demand fetching and JSON output contract.

## 1. Milestone Scope

### In scope
- Replace placeholder routing with real OSM trail graph search.
- Integrate USGS DEM sampling to compute real elevation metrics.
- Enforce strenuous filtering via real elevation gain per mile.
- Switch CLI output to stable JSON contract.
- Implement cache-first + on-demand fetch behavior for OSM and USGS.

### Out of scope for this milestone
- Ridge/watershed/summit/scenic computed metrics (kept as null placeholders).
- Background refresh pipelines.
- Full nationwide precompute.

## 2. Response Contract (JSON)

Top-level shape:

```json
{
  "query": {
    "near": "Roanoke, VA",
    "miles_min": 12,
    "miles_max": 15,
    "difficulty": "strenuous"
  },
  "meta": {
    "engine_version": "v2-osm-usgs",
    "cache": {
      "osm": "hit|miss|partial",
      "usgs": "hit|miss|partial"
    },
    "candidates_considered": 0,
    "routes_returned": 0
  },
  "routes": []
}
```

Per-route fields:
- `id`
- `name`
- `distance_miles`
- `elevation_gain_ft`
- `elevation_gain_per_mile_ft`
- `difficulty`
- `score`
- `geometry` (optional; emitted when `--include-geometry`)
- `terrain.ridge_fraction` = `null` (v3)
- `terrain.summit_proximity_min_m` = `null` (v3)
- `terrain.scenic_score` = `null` (v3)

## 3. Data Flow

1. Geocode `near` query center (with cache).
2. Compute search area bbox/radius from target distance band.
3. Load OSM trail data from tile cache and fetch missing tiles.
4. Load USGS DEM tiles from cache and fetch missing tiles.
5. Build graph edges and sample DEM along segments to derive elevation gain/loss.
6. Run bounded loop search in distance band.
7. Apply strenuous threshold and rank routes.
8. Return top 3 routes with cache stats and candidate counts.

## 4. Cache Model

Directory structure:
- `cache/raw/osm/<tile>.geojson`
- `cache/raw/usgs/<tile>.tif`
- `cache/derived/graph/<query-view-key>.json`

Cache behavior:
- Reuse local artifacts when present and version-compatible.
- Fetch missing source tiles on demand.
- No async/background refresh in v2.

## 5. Error Handling

- OSM miss + fetch failure: return hard error with retry guidance.
- USGS partial coverage: continue only if route metrics remain reliable, else return insufficiency error.
- No qualifying strenuous loops: return empty routes plus explanatory `meta.reason`.

## 6. Testing and Acceptance

### Tests
- JSON contract tests for top-level and per-route required fields.
- Adapter tests with fixed OSM/USGS fixtures.
- Integration test for Roanoke query producing non-placeholder gain metrics.
- Cache tests: cold miss then warm hit.
- Warm-cache performance guardrail test.

### Acceptance criteria
- CLI emits valid JSON consistently.
- Elevation gain/gain-per-mile comes from real DEM sampling.
- Strenuous filtering impacts final route selection.
- Warm-cache query is materially faster than cold-cache query.
