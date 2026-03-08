# Terrain-Aware Hiking Route Generator Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI that generates top-3 terrain-aware hiking loops (12-15 mile strenuous example) using OSM, USGS DEM, and watershed/ridge data with hybrid tile/radius caching.

**Architecture:** Use a package with separable modules for ingest, preprocess, graph model, search, scoring, and cache. First-query in an area fetches and derives tile artifacts; subsequent queries stitch cached tiles into query-local subgraphs and run bounded loop search with ranking. Keep scorer/search components pluggable so speed/quality can be tuned without redesign.

**Tech Stack:** Python 3.12, pytest, typer, networkx, pydantic, geopandas, shapely, rasterio, numpy, pyproj

---

### Task 1: Project Skeleton and Tooling

**Files:**
- Create: `pyproject.toml`
- Create: `src/hiking_router/__init__.py`
- Create: `src/hiking_router/cli.py`
- Create: `tests/test_cli_smoke.py`

**Step 1: Write the failing test**

```python
# tests/test_cli_smoke.py
from typer.testing import CliRunner
from hiking_router.cli import app


def test_cli_shows_help():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "generate-loop" in result.stdout
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_smoke.py::test_cli_shows_help -v`
Expected: FAIL with import/module errors.

**Step 3: Write minimal implementation**

```python
# src/hiking_router/cli.py
import typer

app = typer.Typer()


@app.command("generate-loop")
def generate_loop() -> None:
    print("Not implemented")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli_smoke.py::test_cli_shows_help -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add pyproject.toml src/hiking_router/__init__.py src/hiking_router/cli.py tests/test_cli_smoke.py
git commit -m "chore: bootstrap CLI package and smoke test"
```

### Task 2: Typed Query Contract and CLI Args

**Files:**
- Create: `src/hiking_router/models/query.py`
- Modify: `src/hiking_router/cli.py`
- Create: `tests/models/test_query_validation.py`

**Step 1: Write the failing test**

```python
# tests/models/test_query_validation.py
import pytest
from hiking_router.models.query import LoopQuery


def test_query_rejects_invalid_distance_range():
    with pytest.raises(ValueError):
        LoopQuery(near="Roanoke, VA", miles_min=15, miles_max=12, difficulty="strenuous")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/models/test_query_validation.py::test_query_rejects_invalid_distance_range -v`
Expected: FAIL because `LoopQuery` does not exist.

**Step 3: Write minimal implementation**

```python
# src/hiking_router/models/query.py
from pydantic import BaseModel, field_validator


class LoopQuery(BaseModel):
    near: str
    miles_min: float
    miles_max: float
    difficulty: str

    @field_validator("miles_max")
    @classmethod
    def validate_range(cls, v: float, info):
        miles_min = info.data.get("miles_min")
        if miles_min is not None and v < miles_min:
            raise ValueError("miles_max must be >= miles_min")
        return v
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/models/test_query_validation.py::test_query_rejects_invalid_distance_range -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/models/query.py src/hiking_router/cli.py tests/models/test_query_validation.py
git commit -m "feat: add typed loop query model and validation"
```

### Task 3: Cache Keying and Metadata Index

**Files:**
- Create: `src/hiking_router/cache/store.py`
- Create: `tests/cache/test_store_keys.py`

**Step 1: Write the failing test**

```python
# tests/cache/test_store_keys.py
from hiking_router.cache.store import TileKey, QueryViewKey


def test_tile_and_query_keys_are_stable():
    tile = TileKey(dataset="osm", z=10, x=290, y=391)
    view = QueryViewKey(lat=37.271, lon=-79.941, radius_km=30.0)
    assert tile.to_id() == "osm:z10:290:391"
    assert view.to_id().startswith("qv:")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/cache/test_store_keys.py::test_tile_and_query_keys_are_stable -v`
Expected: FAIL because cache store types are missing.

**Step 3: Write minimal implementation**

```python
# src/hiking_router/cache/store.py
from dataclasses import dataclass


@dataclass(frozen=True)
class TileKey:
    dataset: str
    z: int
    x: int
    y: int

    def to_id(self) -> str:
        return f"{self.dataset}:z{self.z}:{self.x}:{self.y}"


@dataclass(frozen=True)
class QueryViewKey:
    lat: float
    lon: float
    radius_km: float

    def to_id(self) -> str:
        return f"qv:{self.lat:.4f}:{self.lon:.4f}:{self.radius_km:.1f}"
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/cache/test_store_keys.py::test_tile_and_query_keys_are_stable -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/cache/store.py tests/cache/test_store_keys.py
git commit -m "feat: add tile and query cache key primitives"
```

### Task 4: Graph Schema and Invariants

**Files:**
- Create: `src/hiking_router/graph/schema.py`
- Create: `tests/graph/test_schema_invariants.py`

**Step 1: Write the failing test**

```python
# tests/graph/test_schema_invariants.py
import pytest
from hiking_router.graph.schema import TrailEdge


def test_edge_rejects_negative_length():
    with pytest.raises(ValueError):
        TrailEdge(edge_id="e1", from_node="a", to_node="b", length_m=-1)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/graph/test_schema_invariants.py::test_edge_rejects_negative_length -v`
Expected: FAIL because schema is missing.

**Step 3: Write minimal implementation**

```python
# src/hiking_router/graph/schema.py
from pydantic import BaseModel, Field


class TrailEdge(BaseModel):
    edge_id: str
    from_node: str
    to_node: str
    length_m: float = Field(ge=0)
    elev_gain_m: float = 0
    elev_loss_m: float = 0
    avg_grade: float = 0
    max_grade: float = 0
    ridge_fraction: float = 0
    summit_proximity_min_m: float = 0
    scenic_score: float = 0
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/graph/test_schema_invariants.py::test_edge_rejects_negative_length -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/graph/schema.py tests/graph/test_schema_invariants.py
git commit -m "feat: add graph edge schema with core invariants"
```

### Task 5: Elevation Gain Per Mile Feature Extraction

**Files:**
- Create: `src/hiking_router/features/elevation.py`
- Create: `tests/features/test_elevation_metrics.py`

**Step 1: Write the failing test**

```python
# tests/features/test_elevation_metrics.py
from hiking_router.features.elevation import gain_per_mile


def test_gain_per_mile():
    assert round(gain_per_mile(gain_m=600, length_m=1609.34), 2) == 600.00
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/features/test_elevation_metrics.py::test_gain_per_mile -v`
Expected: FAIL because function is missing.

**Step 3: Write minimal implementation**

```python
# src/hiking_router/features/elevation.py
M_PER_MILE = 1609.34


def gain_per_mile(gain_m: float, length_m: float) -> float:
    if length_m <= 0:
        return 0.0
    return gain_m / (length_m / M_PER_MILE)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/features/test_elevation_metrics.py::test_gain_per_mile -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/features/elevation.py tests/features/test_elevation_metrics.py
git commit -m "feat: add elevation gain-per-mile metric"
```

### Task 6: Ridge and Summit Feature Utilities

**Files:**
- Create: `src/hiking_router/features/terrain.py`
- Create: `tests/features/test_terrain_features.py`

**Step 1: Write the failing test**

```python
# tests/features/test_terrain_features.py
from hiking_router.features.terrain import ridge_fraction


def test_ridge_fraction():
    assert ridge_fraction(total_m=1000, ridge_m=250) == 0.25
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/features/test_terrain_features.py::test_ridge_fraction -v`
Expected: FAIL because terrain helpers are missing.

**Step 3: Write minimal implementation**

```python
# src/hiking_router/features/terrain.py
def ridge_fraction(total_m: float, ridge_m: float) -> float:
    if total_m <= 0:
        return 0.0
    value = ridge_m / total_m
    return max(0.0, min(1.0, value))
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/features/test_terrain_features.py::test_ridge_fraction -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/features/terrain.py tests/features/test_terrain_features.py
git commit -m "feat: add ridge-line feature metric helper"
```

### Task 7: Candidate Loop Search Skeleton

**Files:**
- Create: `src/hiking_router/search/loop_search.py`
- Create: `tests/search/test_loop_search_basics.py`

**Step 1: Write the failing test**

```python
# tests/search/test_loop_search_basics.py
import networkx as nx
from hiking_router.search.loop_search import find_loops


def test_find_loops_returns_simple_cycle():
    g = nx.Graph()
    g.add_edges_from([(1, 2), (2, 3), (3, 1)])
    loops = find_loops(g, start=1, max_loops=3)
    assert len(loops) >= 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/search/test_loop_search_basics.py::test_find_loops_returns_simple_cycle -v`
Expected: FAIL because search function is missing.

**Step 3: Write minimal implementation**

```python
# src/hiking_router/search/loop_search.py
import networkx as nx


def find_loops(graph: nx.Graph, start: int, max_loops: int = 3) -> list[list[int]]:
    loops: list[list[int]] = []
    for cycle in nx.cycle_basis(graph, root=start):
        loops.append(cycle)
        if len(loops) >= max_loops:
            break
    return loops
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/search/test_loop_search_basics.py::test_find_loops_returns_simple_cycle -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/search/loop_search.py tests/search/test_loop_search_basics.py
git commit -m "feat: add baseline loop candidate search"
```

### Task 8: Composite Route Scoring

**Files:**
- Create: `src/hiking_router/scoring/composite.py`
- Create: `tests/scoring/test_composite_score.py`

**Step 1: Write the failing test**

```python
# tests/scoring/test_composite_score.py
from hiking_router.scoring.composite import composite_score


def test_composite_score_increases_with_better_terrain_fit():
    weak = composite_score(distance_fit=0.8, difficulty_fit=0.5, terrain_fit=0.2, penalties=0.1)
    strong = composite_score(distance_fit=0.8, difficulty_fit=0.5, terrain_fit=0.9, penalties=0.1)
    assert strong > weak
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/scoring/test_composite_score.py::test_composite_score_increases_with_better_terrain_fit -v`
Expected: FAIL because scorer is missing.

**Step 3: Write minimal implementation**

```python
# src/hiking_router/scoring/composite.py
def composite_score(
    distance_fit: float,
    difficulty_fit: float,
    terrain_fit: float,
    penalties: float,
) -> float:
    raw = 0.35 * distance_fit + 0.30 * difficulty_fit + 0.35 * terrain_fit - penalties
    return max(0.0, min(1.0, raw))
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/scoring/test_composite_score.py::test_composite_score_increases_with_better_terrain_fit -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/scoring/composite.py tests/scoring/test_composite_score.py
git commit -m "feat: add composite route scoring function"
```

### Task 9: Query Orchestration Use Case

**Files:**
- Create: `src/hiking_router/use_cases/generate_loop.py`
- Create: `tests/use_cases/test_generate_loop_top3.py`

**Step 1: Write the failing test**

```python
# tests/use_cases/test_generate_loop_top3.py
from hiking_router.use_cases.generate_loop import generate_top_loops


def test_generate_top_loops_returns_three_or_fewer_ranked_results():
    results = generate_top_loops(query={"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})
    assert len(results) <= 3
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/use_cases/test_generate_loop_top3.py::test_generate_top_loops_returns_three_or_fewer_ranked_results -v`
Expected: FAIL because orchestration is missing.

**Step 3: Write minimal implementation**

```python
# src/hiking_router/use_cases/generate_loop.py
def generate_top_loops(query: dict) -> list[dict]:
    # Placeholder orchestration. Real integration will call ingest/cache/search/scoring.
    return []
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/use_cases/test_generate_loop_top3.py::test_generate_top_loops_returns_three_or_fewer_ranked_results -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/use_cases/generate_loop.py tests/use_cases/test_generate_loop_top3.py
git commit -m "feat: add loop generation orchestration entrypoint"
```

### Task 10: CLI Wiring to Use Case and Top-3 Output

**Files:**
- Modify: `src/hiking_router/cli.py`
- Create: `tests/test_cli_generate_loop.py`

**Step 1: Write the failing test**

```python
# tests/test_cli_generate_loop.py
from typer.testing import CliRunner
from hiking_router.cli import app


def test_generate_loop_command_accepts_core_flags():
    result = CliRunner().invoke(
        app,
        [
            "generate-loop",
            "--near", "Roanoke, VA",
            "--miles-min", "12",
            "--miles-max", "15",
            "--difficulty", "strenuous",
        ],
    )
    assert result.exit_code == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_generate_loop.py::test_generate_loop_command_accepts_core_flags -v`
Expected: FAIL because arguments are not wired.

**Step 3: Write minimal implementation**

```python
# src/hiking_router/cli.py (core command shape)
@app.command("generate-loop")
def generate_loop(
    near: str = typer.Option(...),
    miles_min: float = typer.Option(..., "--miles-min"),
    miles_max: float = typer.Option(..., "--miles-max"),
    difficulty: str = typer.Option(...),
) -> None:
    query = LoopQuery(near=near, miles_min=miles_min, miles_max=miles_max, difficulty=difficulty)
    routes = generate_top_loops(query.model_dump())
    print(routes)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli_generate_loop.py::test_generate_loop_command_accepts_core_flags -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/cli.py tests/test_cli_generate_loop.py
git commit -m "feat: wire generate-loop CLI command to use case"
```

### Task 11: Data Source Adapters (Stubbed Interfaces)

**Files:**
- Create: `src/hiking_router/adapters/osm_client.py`
- Create: `src/hiking_router/adapters/usgs_client.py`
- Create: `src/hiking_router/adapters/ridge_client.py`
- Create: `tests/adapters/test_adapter_contracts.py`

**Step 1: Write the failing test**

```python
# tests/adapters/test_adapter_contracts.py
from hiking_router.adapters.osm_client import OSMClient


def test_osm_client_has_fetch_trails_contract():
    client = OSMClient()
    assert hasattr(client, "fetch_trails")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/adapters/test_adapter_contracts.py::test_osm_client_has_fetch_trails_contract -v`
Expected: FAIL because adapters are missing.

**Step 3: Write minimal implementation**

```python
# src/hiking_router/adapters/osm_client.py
class OSMClient:
    def fetch_trails(self, bbox: tuple[float, float, float, float]) -> dict:
        return {"type": "FeatureCollection", "features": []}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/adapters/test_adapter_contracts.py::test_osm_client_has_fetch_trails_contract -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/adapters/osm_client.py src/hiking_router/adapters/usgs_client.py src/hiking_router/adapters/ridge_client.py tests/adapters/test_adapter_contracts.py
git commit -m "feat: add geodata adapter interfaces"
```

### Task 12: End-to-End Query Fixture and Performance Budget Harness

**Files:**
- Create: `tests/e2e/test_roanoke_query_fixture.py`
- Create: `tests/perf/test_query_budget.py`
- Create: `docs/plans/fixtures/roanoke-query.md`

**Step 1: Write the failing test**

```python
# tests/e2e/test_roanoke_query_fixture.py
from hiking_router.use_cases.generate_loop import generate_top_loops


def test_roanoke_strenuous_query_returns_ranked_results_shape():
    results = generate_top_loops({"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})
    assert isinstance(results, list)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/e2e/test_roanoke_query_fixture.py::test_roanoke_strenuous_query_returns_ranked_results_shape -v`
Expected: FAIL while fixture behavior is undefined.

**Step 3: Write minimal implementation**

```python
# tests/perf/test_query_budget.py
import time


def test_warm_cache_query_budget_placeholder():
    start = time.time()
    elapsed = time.time() - start
    assert elapsed < 60
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/e2e/test_roanoke_query_fixture.py tests/perf/test_query_budget.py -v`
Expected: PASS with placeholder harness.

**Step 5: Commit**

```bash
git add tests/e2e/test_roanoke_query_fixture.py tests/perf/test_query_budget.py docs/plans/fixtures/roanoke-query.md
git commit -m "test: add e2e fixture and performance budget harness"
```

### Task 13: Verification and Completion Gate (@verification-before-completion)

**Files:**
- Modify: `README.md`
- Create: `docs/architecture.md`

**Step 1: Write the failing test**

```python
# Add one failing assertion in tests/test_cli_smoke.py temporarily if README command differs.
```

**Step 2: Run full test suite to verify current status**

Run: `pytest -v`
Expected: PASS.

**Step 3: Run CLI manual checks**

Run: `python -m hiking_router.cli generate-loop --near "Roanoke, VA" --miles-min 12 --miles-max 15 --difficulty strenuous`
Expected: exits successfully and prints top-3 result payload shape.

**Step 4: Update docs**

Document:
- CLI usage examples
- Cache behavior (first run vs warm cache)
- Known limitations and next optimization steps for sub-10s mode

**Step 5: Commit**

```bash
git add README.md docs/architecture.md
git commit -m "docs: add usage and architecture notes"
```

## Implementation Notes

- Apply @test-driven-development discipline on every task: fail -> pass -> refactor.
- Keep modules small and pure where possible.
- Avoid premature optimization; implement metrics/search correctness first, then tune hot paths.
- Keep cache interfaces stable to support future pluggable backends.
