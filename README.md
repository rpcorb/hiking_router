# hiking_router

This is a CLI-first Python route-generation engine that builds and ranks hiking loops from OSM trail geometry plus DEM/summit/ridge terrain signals.

## How it works

1. CLI parses `generate-loop` args and validates query fields in Pydantic (`src/hiking_router/cli.py`, `src/hiking_router/models/query.py`).
2. Main orchestrator fetches OSM/ridge/summit/USGS data with cache-first adapters and fallback semantics (`src/hiking_router/use_cases/generate_loop.py`).
3. OSM payload is normalized into graph edges (`src/hiking_router/graph/osm_normalize.py`).
4. Loop candidates are found with `networkx.cycle_basis`, filtered by distance, then diversity-pruned (`src/hiking_router/search/loop_search.py`, `src/hiking_router/search/diversity.py`).
5. Per-loop terrain/elevation features are computed, then scored and ranked (`src/hiking_router/features/dem_sampling.py`, `src/hiking_router/features/ridge_overlap.py`, `src/hiking_router/features/summit_proximity.py`, `src/hiking_router/scoring/scenic.py`, `src/hiking_router/scoring/composite.py`).
6. Response envelope (`query/meta/routes`) is validated and printed as JSON (`src/hiking_router/models/response.py`).

## Architecture

- Transport/provider helpers (HTTP, Overpass, TNM, GNIS): `src/hiking_router/providers/`
- Cache-aware source adapters: `src/hiking_router/adapters/`
- Domain logic (graph/search/features/scoring): `src/hiking_router/`
- Contracts/config via env vars: `src/hiking_router/config/providers.py`, `src/hiking_router/config/scoring.py`

## Important current constraints

- `tile_id` and `bbox` are currently hardcoded in the use case, so `--near` is mostly label-level today rather than true geocoded area selection (`src/hiking_router/use_cases/generate_loop.py`).
- When live fetch fails and `strict_live` is false, adapters intentionally create fallback artifacts for offline-safe behavior.
- Test coverage is broad (unit + e2e + perf) across all layers in `tests/`, with additional notes in `docs/architecture.md`.
