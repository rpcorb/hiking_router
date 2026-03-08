# Architecture

## Modules

- `hiking_router.cli`: user-facing Typer CLI command surface.
- `hiking_router.models.query`: typed query contract and validation.
- `hiking_router.cache.store`: tile/query view key primitives.
- `hiking_router.adapters.*`: OSM/USGS/ridge source adapter interfaces.
- `hiking_router.features.*`: terrain feature computations.
- `hiking_router.search.loop_search`: baseline cycle-based loop candidate finder.
- `hiking_router.scoring.composite`: weighted route scoring utility.
- `hiking_router.use_cases.generate_loop`: orchestration entrypoint for top route generation.

## Data flow (v1 skeleton)

1. CLI parses and validates query.
2. Query is passed to use-case orchestration.
3. Orchestration will hydrate cache-backed geodata adapters (stubbed today).
4. Search produces loop candidates.
5. Scoring ranks candidates; top-3 are returned.

## Planned cache model

- Tile-level source and derived artifacts.
- Radius-level query views over stitched local subgraphs.
- Stable keying for deterministic reuse and future disk-backed index.
