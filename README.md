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

## Response contract

`generate-loop` currently prints a Python list of route objects (`list[dict]`) to stdout.

### Current shape (placeholder)

```python
[
  {
    "name": "Prototype loop near Roanoke, VA",
    "distance_miles": 12.0,
    "difficulty": "strenuous",
    "score": 0.5
  }
]
```

### Current attributes

- `name` (`str`): Human-readable route label.
- `distance_miles` (`float`): Placeholder distance value (currently seeded from `--miles-min`).
- `difficulty` (`str`): Difficulty requested by the user.
- `score` (`float`): Composite ranking score in `[0.0, 1.0]` (currently fixed placeholder).

### Response guarantees

- Returns `0..3` ranked routes (top-k behavior).
- Output order is descending rank (best first).
- Shape is intentionally minimal while data ingestion/search/scoring are still stubbed.

### Planned expansion

As real terrain processing is implemented, each route object will expand with route and terrain metrics such as:
- elevation gain/loss
- elevation gain per mile
- ridge-line fraction
- summit proximity
- scenic score breakdown

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
