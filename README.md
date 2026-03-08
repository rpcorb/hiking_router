# hiking_router

Terrain-aware hiking route generator (CLI-first).

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install pytest typer pydantic networkx
```

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

Current CLI returns up to top-3 placeholder ranked routes via the orchestration entrypoint.

## Cache behavior (planned)

- First query in an area: fetch missing tiles and preprocess features.
- Warm-cache query in same area: reuse tile and query-view caches for faster response.
- Tile cache and query radius cache are both part of the design and represented by stable cache-key primitives.

## Status and limitations

- Data adapters are currently interface stubs.
- Search/scoring modules are baseline placeholders for iterative buildout.
- E2E and performance tests are harness-level checks, not full real-data validation yet.

## Next optimization steps

1. Implement real OSM/USGS/ridge ingestion and tile persistence.
2. Build derived-feature preprocessing (gain/mi, ridge overlap, summit proximity, scenic factors).
3. Add bounded loop search heuristics and diversity filtering.
4. Introduce warm-cache benchmarking targets and profile hotspots.
