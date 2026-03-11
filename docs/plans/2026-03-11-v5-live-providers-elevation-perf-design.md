# V5 Live Providers, Elevation Realism, and Performance Design

## Scope
Add real live ingestion for ridge and summit inputs, improve elevation profile realism from route geometry sampling, and tune performance for warm-cache CLI queries while preserving deterministic tests and the existing JSON envelope.

## Decisions
- Summit provider priority: `Overpass -> GNIS`.
- Ridge live ingestion: Overpass-only in this phase.
- Keep offline-safe fallback behavior when `strict_live=false`.
- Also surface live-degradation explicitly in `meta.reason` for `force_live=true` degraded refreshes.

## Current Constraints
- Cache-first adapters and strict-live semantics already exist for OSM/USGS/ridge/summit.
- Route output contract (`query`, `meta`, `routes`) is consumed by tests and must remain stable.
- Test suite defaults to deterministic no-network behavior.

## Architecture

### Provider Layer
- Extend `providers/overpass.py` with:
  - `build_ridge_query(bbox)`
  - `build_summit_query(bbox)`
  - `fetch_overpass_ridges(...)`
  - `fetch_overpass_summits(...)`
- Add `providers/gnis.py` with:
  - GNIS fetch wrapper
  - normalization to `FeatureCollection<Point>`

### Adapter Layer
- Upgrade `adapters/ridge_client.py` to use real Overpass ridge fetch on live path.
- Add `adapters/summit_aggregator.py`:
  - tries Overpass summit provider first
  - falls back to GNIS when Overpass fails or yields unusable payload
  - merges and de-duplicates summit points
  - persists merged payload to `cache/raw/summit/<tile>.geojson`

### Use-Case Layer
- `use_cases/generate_loop.py` keeps using ridge/summit FeatureCollections.
- Track live-degradation flags per source on forced live refresh.
- If any live source degrades and a cached/fallback artifact is used, set a precise `meta.reason` message without failing the request (unless `strict_live=true` and no usable artifact exists).

### Elevation Realism
- Add route polyline extraction from selected loops.
- Replace artifact-level placeholder profile usage with sampled DEM elevations along route geometry points.
- Keep byte-fallback behavior only as last resort; prefer true raster sampling whenever a valid DEM is present.

### Performance
- Add warm-cache benchmark tests for representative query sizes.
- Add lightweight timing instrumentation at ingestion, graph build, route scoring, and terrain metric stages.
- Optimize hot paths (memoization of coordinate conversions, reduced repeated scenic score calls, avoid duplicate loop transforms).

## Data Flow
1. Query enters `generate_top_loops`.
2. OSM graph fetch: cache-first, then live.
3. Ridge fetch: cache-first, then Overpass live.
4. Summit fetch: cache-first, then Overpass live, then GNIS live fallback.
5. USGS DEM fetch: cache-first, then TNM live.
6. Route generation and ranking.
7. Elevation profile sampled along route geometry.
8. Terrain metrics computed (`ridge_fraction`, `summit_proximity_min_m`, `scenic_score`).
9. Response emitted with cache statuses and optional degradation reason.

## Error Handling
- `strict_live=true`:
  - no cache + no usable live result from required source => insufficient coverage response path.
- `strict_live=false`:
  - preserve fallback artifact creation and successful response behavior.
- `force_live=true` degradation:
  - response still succeeds when usable fallback/cached data exists.
  - `meta.reason` includes degraded source details.

## Testing Strategy
- Provider tests:
  - Overpass ridge/summit query builders and parsers.
  - GNIS fetch parsing and normalization.
- Adapter tests:
  - Summit provider ordering and fallback.
  - Deduping behavior and cache persistence.
  - Ridge live path real fetch wiring.
- Use-case tests:
  - Degradation reason behavior for force-live partial failures.
  - Terrain metrics remain populated with mixed provider outcomes.
- Elevation tests:
  - Route-geometry DEM sampling yields deterministic profile for fixed fixture raster.
- Performance tests:
  - Warm-cache target checks for latency budget.

## Risks and Mitigations
- External API variability:
  - mitigate with strict normalization, bounded retries, and deterministic fixture tests.
- Overpass query size/rate limits:
  - keep bbox small per tile and allow fallback to cached artifacts.
- Profile sampling performance cost:
  - cache route coordinate transforms and sample at controlled spacing.

## Success Criteria
- Summit coverage improves with GNIS fallback while preserving stable response shape.
- Ridge live ingestion is no longer placeholder-only.
- Elevation metrics reflect route geometry sampling from DEM where available.
- Warm-cache performance shows measurable improvement and has regression tests.
