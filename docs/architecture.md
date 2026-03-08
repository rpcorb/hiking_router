# Architecture

## Modules

- `hiking_router.cli`: user-facing Typer CLI command surface.
- `hiking_router.models.query`: typed query contract and validation.
- `hiking_router.models.response`: v2 JSON response envelope models.
- `hiking_router.cache.store`: tile/query view key primitives.
- `hiking_router.adapters.*`: OSM/USGS/ridge source adapter interfaces.
- `hiking_router.features.*`: terrain feature computations.
- `hiking_router.search.loop_search`: baseline cycle-based loop candidate finder.
- `hiking_router.scoring.composite`: weighted route scoring utility.
- `hiking_router.scoring.difficulty`: strenuous threshold utility.
- `hiking_router.use_cases.generate_loop`: orchestration entrypoint for top route generation.

## Data flow (v2 skeleton)

1. CLI parses and validates query.
2. Use case resolves cache directory and tile key.
3. OSM and USGS adapters perform cache-first reads and return cache status.
4. On cache miss, placeholder source artifacts are written for subsequent warm hits.
5. Use case builds v2 JSON envelope with cache metadata and route list.
6. CLI serializes envelope as JSON to stdout.

## Cache model

- Tile-level source and derived artifacts.
- Radius-level query views over stitched local subgraphs.
- Stable keying for deterministic reuse and future disk-backed index.

Current source cache paths:
- `cache/raw/osm/<tile>.geojson`
- `cache/raw/usgs/<tile>.tif`
