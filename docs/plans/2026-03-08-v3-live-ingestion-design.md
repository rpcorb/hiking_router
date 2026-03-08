# V3 Live Ingestion and Real Terrain Metrics Design

Date: 2026-03-08
Status: Approved
Scope: Add pluggable live OSM + USGS ingestion with cache-first fallback, while preserving v2 JSON response contract.

## 1. Scope

### In scope
- Implement pluggable provider configuration for:
  - OSM Overpass API
  - USGS TNM/3DEP endpoints
- On cache miss, fetch real source data live and persist to cache.
- On live-fetch failure, fall back to existing cache when available and surface degraded status.
- Keep JSON response shape stable (`query`, `meta`, `routes`).
- Replace placeholder source cache artifacts with real payloads.

### Out of scope
- Ridge/summit/scenic computed metrics (remain null placeholders).
- Background refresh workers.
- Service/queue decomposition.

## 2. Provider + Fetch Architecture

### Configuration
- Add provider config model loaded from env and/or config file:
  - `osm_provider`
  - `usgs_provider`
  - base URLs
  - timeouts
  - retry limits
  - rate limits

### Shared fetch utility
- Central HTTP wrapper with:
  - bounded retries
  - exponential backoff
  - per-provider rate-limiting
  - structured errors:
    - `FetchTimeout`
    - `FetchHTTPError`
    - `FetchParseError`

### OSM provider
- `OverpassProvider` fetches trail/path network by bbox.
- Normalize provider payload into GeoJSON FeatureCollection.
- Persist normalized payload in `cache/raw/osm/<tile>.geojson`.

### USGS provider
- `TNMProvider` queries DEM products by bbox.
- Select best matching tile set and download raster.
- Validate file readability and basic metadata before accepting.
- Persist in `cache/raw/usgs/<tile>.tif`.

## 3. Cache Behavior

Policy per source:
- **Hit:** return cached artifact + `hit`.
- **Miss + live success:** fetch, validate, cache, return + `miss`.
- **Miss/live failure + cache exists:** return cached artifact + `partial` and reason note.
- **Miss/live failure + no cache:** return explicit error for insufficient data.

## 4. Query Flow

1. Parse query and resolve search area.
2. OSM adapter acquires trails with cache-first/live-fallback logic.
3. USGS adapter acquires DEM with same logic.
4. Build trail graph and sample DEM along segments.
5. Compute route metrics (`elevation_gain_ft`, `elevation_gain_per_mile_ft`).
6. Apply strenuous filtering and ranking.
7. Return top routes in stable JSON envelope.

## 5. Response Semantics

- Keep existing response schema unchanged.
- `meta.cache.osm|usgs` remains `hit|miss|partial`.
- `meta.reason` includes fallback/degradation notes when applicable.
- `routes` may be empty while still returning valid envelope.

## 6. Validation and Testing

### Validation
- OSM payload checks: FeatureCollection shape + supported geometry/tags.
- DEM checks: file exists, readable, non-empty, basic metadata sanity.

### Tests
- Unit tests for config parsing/default provider selection.
- Adapter tests for:
  - miss -> live fetch -> cache write
  - live fail + cache exists -> partial
  - live fail + no cache -> explicit error
- Integration tests with recorded fixtures ensuring real non-zero elevation metrics.
- JSON contract tests to ensure shape stability.
- Warm-cache performance guardrail tests.

## 7. Acceptance Criteria

- Live ingestion works for Overpass + TNM providers.
- Cache-first fallback works with explicit `meta` signals.
- Elevation metrics derive from real DEM sampling.
- Response contract remains stable.
- Test suite passes.
