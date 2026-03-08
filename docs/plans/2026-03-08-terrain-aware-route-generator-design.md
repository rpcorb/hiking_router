# Terrain-Aware Hiking Route Generator Design

Date: 2026-03-08
Status: Approved
Scope: v1 CLI-only system for U.S.-wide terrain-aware loop generation with hybrid on-demand + cached data.

## 1. Goals and Non-Goals

### Goals
- Generate hiking loops algorithmically from raw terrain/network data rather than scraped trail suggestions.
- Support user queries like: "Generate a 12-15 mile strenuous loop near Roanoke."
- Use OpenStreetMap trail network, USGS elevation data, and watershed/ridge data.
- Return top 3 ranked loop routes with key metrics.
- Achieve moderate query latency target (10-60s typical), optimized for warm-cache queries.

### Non-Goals (v1)
- GUI/web frontend.
- Real-time nationwide precompute before first use.
- Turn-by-turn navigation or offline mobile packaging.

## 2. High-Level Architecture

Primary interface is a CLI, with four internal modules:

1. `hike ingest`
- Fetches raw OSM, USGS DEM, and watershed/ridge overlays for requested area tiles.

2. `hike preprocess`
- Builds normalized graph fragments from raw data.
- Attaches terrain features to edges and nodes.

3. `hike query`
- Builds query-local subgraph from cached tiles around search center.
- Generates, scores, and ranks loop candidates.

4. `hike cache`
- Stores raw tiles, derived graph/features, and query-level cached views/results.

## 3. Data Strategy: Hybrid On-Demand + Cache

v1 uses a hybrid approach:
- First query in an area: download missing data, preprocess, and cache.
- Later queries in same area: reuse cached data for improved latency.

Cache structure:
- Raw layer cache: source payloads keyed by tile + source/version metadata.
- Derived layer cache: cleaned graph fragments + terrain feature artifacts.
- Query view cache: stitched radius subgraphs and optional top-k result cache.

Cache keying strategy:
- Tile-based storage for reuse and deduplication.
- Radius/query-specific views for fast repeated local searches.

## 4. Graph Model

### Node
- `id`
- `lat`, `lon`
- `elevation_m`
- `is_junction`
- optional POI tags

### Edge
- `from`, `to`
- `length_m`
- `elev_gain_m`, `elev_loss_m`
- `avg_grade`, `max_grade`
- `ridge_fraction`
- `summit_proximity_min_m`
- `surface/type`
- `scenic_score`

Mapping:
- Trail junctions become graph nodes.
- Trail segments become graph edges.

## 5. Metrics and Scoring

Composite route score is a weighted normalized objective (0-1) over:
- Distance fitness to requested range.
- Difficulty fitness using gain-per-mile and sustained grade.
- Terrain desirability from ridge-line share, summit proximity, and scenic signal.
- Loop quality penalties (backtracking, road share, graph artifacts).

Strenuous handling:
- Apply hard minimum gain-per-mile threshold.
- Rank remaining candidates by composite score with higher difficulty preference subject to safety constraints.

Derived metrics reported per route:
- Total distance
- Elevation gain/loss
- Elevation gain per mile
- Ridge-line segment share
- Summit proximity summary
- Scenic score breakdown

## 6. Query and Loop Search Flow

Example request:
- `generate-loop --near "Roanoke, VA" --miles 12-15 --difficulty strenuous`

Execution flow:
1. Resolve anchor point and determine nearby tiles.
2. Fetch/preprocess any missing tiles and stitch cached fragments.
3. Filter to hike-eligible edges (trail/path classes, road-share cap).
4. Generate candidate loops with bounded search:
- Seed from candidate trailheads/junctions.
- Expand with distance/elevation constraints and early pruning.
- Close loop on start/near-start with topology checks.
5. Compute full metrics and composite scores for candidates.
6. Rank and return top 3 with diversity control (overlap threshold to avoid near-duplicates).

Performance controls:
- Two-stage search (cheap heuristic shortlist, then expensive scoring).
- Beam-width and path-expansion bounds.
- Precomputed tile-local stats for faster pruning.

## 7. Error Handling and Degradation

- Missing coverage: explicit insufficiency message with remediation suggestions.
- Source failures: fall back to existing cached data when possible.
- Graph path failures: detect disconnected components early.
- Invalid inputs: clear CLI validation errors and examples.

## 8. Testing and Verification Plan

- Unit tests: feature extraction and metric computations.
- Property tests: graph invariants after tile stitching.
- Golden tests: representative query fixtures, including Roanoke strenuous loop case.
- Performance regression tests: warm-cache p95 <= 60s target budget.

## 9. Technology Choice

Language: Python.

Rationale:
- Strongest geospatial ecosystem for OSM network processing, raster DEM analysis, vector operations, and scientific scoring workflows.
- Fastest path to robust v1 exploration while preserving future optimization options.

## 10. Open Decisions Deferred to Implementation Planning

- Exact CLI argument schema and defaults.
- Concrete geospatial libraries and storage format selection.
- Detailed scenic score formula components and weighting calibration workflow.
- Caching eviction policy and disk budget defaults.
