# V2 OSM + USGS Routing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement real OSM + USGS based loop generation with strenuous filtering and stable JSON CLI response.

**Architecture:** Keep a layered pipeline: CLI -> query model -> use case orchestration -> adapters/cache -> graph/preprocess -> search/scoring -> JSON formatter. Use cache-first on-demand fetch for raw OSM/USGS and derived query-view graph artifacts. Keep ridge/summit/scenic fields explicit `null` placeholders for forward compatibility.

**Tech Stack:** Python 3.13, typer, pydantic, networkx, pytest, requests, shapely, rasterio, numpy

---

### Task 1: Add V2 Response Models and JSON Envelope

**Files:**
- Create: `src/hiking_router/models/response.py`
- Modify: `src/hiking_router/use_cases/generate_loop.py`
- Test: `tests/models/test_response_contract.py`

**Step 1: Write the failing test**

```python
from hiking_router.models.response import QueryResponse


def test_response_contract_requires_query_meta_routes():
    payload = QueryResponse(
        query={"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"},
        meta={"engine_version": "v2-osm-usgs", "cache": {"osm": "hit", "usgs": "miss"}, "candidates_considered": 3, "routes_returned": 1},
        routes=[],
    )
    assert payload.meta.engine_version == "v2-osm-usgs"
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/models/test_response_contract.py::test_response_contract_requires_query_meta_routes -v`
Expected: FAIL with module/class not found.

**Step 3: Write minimal implementation**

```python
from pydantic import BaseModel


class CacheMeta(BaseModel):
    osm: str
    usgs: str


class Meta(BaseModel):
    engine_version: str
    cache: CacheMeta
    candidates_considered: int
    routes_returned: int
    reason: str | None = None


class QueryResponse(BaseModel):
    query: dict
    meta: Meta
    routes: list[dict]
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/models/test_response_contract.py::test_response_contract_requires_query_meta_routes -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/models/response.py tests/models/test_response_contract.py
git commit -m "feat: add v2 JSON response contract models"
```

### Task 2: Switch CLI Output to JSON

**Files:**
- Modify: `src/hiking_router/cli.py`
- Test: `tests/test_cli_generate_loop_json.py`

**Step 1: Write the failing test**

```python
import json
from typer.testing import CliRunner
from hiking_router.cli import app


def test_generate_loop_emits_json_envelope():
    result = CliRunner().invoke(app, ["generate-loop", "--near", "Roanoke, VA", "--miles-min", "12", "--miles-max", "15", "--difficulty", "strenuous"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "query" in payload and "meta" in payload and "routes" in payload
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/test_cli_generate_loop_json.py::test_generate_loop_emits_json_envelope -v`
Expected: FAIL with JSON decode or shape mismatch.

**Step 3: Write minimal implementation**

```python
import json
...
response = generate_top_loops(query.model_dump())
print(json.dumps(response))
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/test_cli_generate_loop_json.py::test_generate_loop_emits_json_envelope -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/cli.py tests/test_cli_generate_loop_json.py
git commit -m "feat: emit stable JSON from generate-loop command"
```

### Task 3: Add Cache Status and File Paths

**Files:**
- Modify: `src/hiking_router/cache/store.py`
- Create: `tests/cache/test_cache_paths.py`

**Step 1: Write the failing test**

```python
from hiking_router.cache.store import raw_osm_tile_path, raw_usgs_tile_path, derived_graph_path


def test_cache_paths_follow_layout():
    assert "cache/raw/osm" in str(raw_osm_tile_path("z10-290-391"))
    assert "cache/raw/usgs" in str(raw_usgs_tile_path("z10-290-391"))
    assert "cache/derived/graph" in str(derived_graph_path("qv:37.271:-79.941:30.0"))
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/cache/test_cache_paths.py::test_cache_paths_follow_layout -v`
Expected: FAIL with missing functions.

**Step 3: Write minimal implementation**

```python
from pathlib import Path

def raw_osm_tile_path(tile_id: str) -> Path:
    return Path("cache/raw/osm") / f"{tile_id}.geojson"

def raw_usgs_tile_path(tile_id: str) -> Path:
    return Path("cache/raw/usgs") / f"{tile_id}.tif"

def derived_graph_path(query_key: str) -> Path:
    safe = query_key.replace(":", "_")
    return Path("cache/derived/graph") / f"{safe}.json"
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/cache/test_cache_paths.py::test_cache_paths_follow_layout -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/cache/store.py tests/cache/test_cache_paths.py
git commit -m "feat: add cache path layout helpers for raw and derived artifacts"
```

### Task 4: Implement OSM Adapter Real Fetch + Cache Read/Write

**Files:**
- Modify: `src/hiking_router/adapters/osm_client.py`
- Test: `tests/adapters/test_osm_client_cache.py`

**Step 1: Write the failing test**

```python
from hiking_router.adapters.osm_client import OSMClient


def test_osm_client_reads_cached_geojson_without_network(tmp_path):
    client = OSMClient(cache_dir=tmp_path)
    tile_id = "z10-290-391"
    path = tmp_path / "raw" / "osm" / f"{tile_id}.geojson"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"type":"FeatureCollection","features":[]}')
    data, status = client.fetch_trails(tile_id=tile_id, bbox=(-80, 37, -79, 38))
    assert status == "hit"
    assert data["type"] == "FeatureCollection"
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/adapters/test_osm_client_cache.py::test_osm_client_reads_cached_geojson_without_network -v`
Expected: FAIL with signature/behavior mismatch.

**Step 3: Write minimal implementation**

```python
class OSMClient:
    def __init__(self, cache_dir: Path = Path("cache")) -> None: ...
    def fetch_trails(self, tile_id: str, bbox: tuple[float, float, float, float]) -> tuple[dict, str]:
        # return (payload, "hit"|"miss")
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/adapters/test_osm_client_cache.py::test_osm_client_reads_cached_geojson_without_network -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/adapters/osm_client.py tests/adapters/test_osm_client_cache.py
git commit -m "feat: implement OSM cache-first fetch behavior"
```

### Task 5: Implement USGS Adapter Real Fetch + Cache Read/Write

**Files:**
- Modify: `src/hiking_router/adapters/usgs_client.py`
- Test: `tests/adapters/test_usgs_client_cache.py`

**Step 1: Write the failing test**

```python
from hiking_router.adapters.usgs_client import USGSClient


def test_usgs_client_reads_cached_dem_without_network(tmp_path):
    client = USGSClient(cache_dir=tmp_path)
    tile_id = "z10-290-391"
    path = tmp_path / "raw" / "usgs" / f"{tile_id}.tif"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"fake-dem")
    dem_path, status = client.fetch_dem(tile_id=tile_id, bbox=(-80, 37, -79, 38))
    assert status == "hit"
    assert dem_path.exists()
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/adapters/test_usgs_client_cache.py::test_usgs_client_reads_cached_dem_without_network -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
class USGSClient:
    def __init__(self, cache_dir: Path = Path("cache")) -> None: ...
    def fetch_dem(self, tile_id: str, bbox: tuple[float, float, float, float]) -> tuple[Path, str]:
        # return (local_dem_path, "hit"|"miss")
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/adapters/test_usgs_client_cache.py::test_usgs_client_reads_cached_dem_without_network -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/adapters/usgs_client.py tests/adapters/test_usgs_client_cache.py
git commit -m "feat: implement USGS DEM cache-first fetch behavior"
```

### Task 6: Compute Elevation Gain on Real Path Samples

**Files:**
- Create: `src/hiking_router/features/dem_sampling.py`
- Test: `tests/features/test_dem_sampling_gain.py`

**Step 1: Write the failing test**

```python
from hiking_router.features.dem_sampling import elevation_gain_from_profile


def test_elevation_gain_from_profile_accumulates_only_positive_deltas():
    gain = elevation_gain_from_profile([100, 120, 110, 140])
    assert gain == 50
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/features/test_dem_sampling_gain.py::test_elevation_gain_from_profile_accumulates_only_positive_deltas -v`
Expected: FAIL with missing module.

**Step 3: Write minimal implementation**

```python
def elevation_gain_from_profile(samples: list[float]) -> float:
    gain = 0.0
    for a, b in zip(samples, samples[1:]):
        if b > a:
            gain += b - a
    return gain
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/features/test_dem_sampling_gain.py::test_elevation_gain_from_profile_accumulates_only_positive_deltas -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/features/dem_sampling.py tests/features/test_dem_sampling_gain.py
git commit -m "feat: add DEM profile gain computation utility"
```

### Task 7: Build Distance-Bounded Loop Candidate Filter

**Files:**
- Modify: `src/hiking_router/search/loop_search.py`
- Test: `tests/search/test_loop_distance_band.py`

**Step 1: Write the failing test**

```python
import networkx as nx
from hiking_router.search.loop_search import filter_loops_by_distance_band


def test_filters_loops_outside_distance_band():
    loops = [[1, 2, 3], [1, 4, 5]]
    lengths = {(1, 2, 3): 13.0, (1, 4, 5): 9.0}
    out = filter_loops_by_distance_band(loops, lengths, miles_min=12, miles_max=15)
    assert out == [[1, 2, 3]]
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/search/test_loop_distance_band.py::test_filters_loops_outside_distance_band -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
def filter_loops_by_distance_band(loops: list[list[int]], lengths: dict[tuple[int, ...], float], miles_min: float, miles_max: float) -> list[list[int]]:
    kept = []
    for loop in loops:
        d = lengths.get(tuple(loop))
        if d is not None and miles_min <= d <= miles_max:
            kept.append(loop)
    return kept
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/search/test_loop_distance_band.py::test_filters_loops_outside_distance_band -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/search/loop_search.py tests/search/test_loop_distance_band.py
git commit -m "feat: add distance-band loop filtering"
```

### Task 8: Add Strenuous Filter Using Gain Per Mile

**Files:**
- Create: `src/hiking_router/scoring/difficulty.py`
- Test: `tests/scoring/test_strenuous_filter.py`

**Step 1: Write the failing test**

```python
from hiking_router.scoring.difficulty import is_strenuous


def test_strenuous_requires_min_gain_per_mile():
    assert is_strenuous(gain_per_mile_ft=600, threshold_ft_per_mile=500) is True
    assert is_strenuous(gain_per_mile_ft=300, threshold_ft_per_mile=500) is False
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/scoring/test_strenuous_filter.py::test_strenuous_requires_min_gain_per_mile -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
def is_strenuous(gain_per_mile_ft: float, threshold_ft_per_mile: float = 500) -> bool:
    return gain_per_mile_ft >= threshold_ft_per_mile
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/scoring/test_strenuous_filter.py::test_strenuous_requires_min_gain_per_mile -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/scoring/difficulty.py tests/scoring/test_strenuous_filter.py
git commit -m "feat: add strenuous difficulty threshold filter"
```

### Task 9: Orchestrate OSM+USGS Pipeline and Emit V2 Envelope

**Files:**
- Modify: `src/hiking_router/use_cases/generate_loop.py`
- Test: `tests/use_cases/test_generate_loop_v2_envelope.py`

**Step 1: Write the failing test**

```python
from hiking_router.use_cases.generate_loop import generate_top_loops


def test_generate_top_loops_returns_v2_envelope_with_cache_meta():
    payload = generate_top_loops({"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})
    assert payload["meta"]["engine_version"] == "v2-osm-usgs"
    assert "cache" in payload["meta"]
    assert isinstance(payload["routes"], list)
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/use_cases/test_generate_loop_v2_envelope.py::test_generate_top_loops_returns_v2_envelope_with_cache_meta -v`
Expected: FAIL with old shape mismatch.

**Step 3: Write minimal implementation**

```python
def generate_top_loops(query: dict) -> dict:
    # call adapters/search/scoring and build JSON envelope
    return {
        "query": query,
        "meta": {
            "engine_version": "v2-osm-usgs",
            "cache": {"osm": "miss", "usgs": "miss"},
            "candidates_considered": 0,
            "routes_returned": 0,
        },
        "routes": [],
    }
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/use_cases/test_generate_loop_v2_envelope.py::test_generate_top_loops_returns_v2_envelope_with_cache_meta -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/use_cases/generate_loop.py tests/use_cases/test_generate_loop_v2_envelope.py
git commit -m "feat: orchestrate v2 response envelope with cache metadata"
```

### Task 10: Add Cold-vs-Warm Cache Integration Test

**Files:**
- Modify: `tests/e2e/test_roanoke_query_fixture.py`
- Create: `tests/e2e/test_cache_hit_second_run.py`

**Step 1: Write the failing test**

```python
from hiking_router.use_cases.generate_loop import generate_top_loops


def test_second_run_reports_cache_hits(tmp_path, monkeypatch):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))
    _ = generate_top_loops({"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})
    second = generate_top_loops({"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})
    assert second["meta"]["cache"]["osm"] in {"hit", "partial"}
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/e2e/test_cache_hit_second_run.py::test_second_run_reports_cache_hits -v`
Expected: FAIL with cache status mismatch.

**Step 3: Write minimal implementation**

```python
# track cache status from adapter return tuples and propagate to meta.cache
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/e2e/test_cache_hit_second_run.py::test_second_run_reports_cache_hits -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add tests/e2e/test_cache_hit_second_run.py src/hiking_router/use_cases/generate_loop.py src/hiking_router/adapters/osm_client.py src/hiking_router/adapters/usgs_client.py
git commit -m "test: validate warm-cache behavior on repeated query"
```

### Task 11: Update Docs and Run Full Verification (@verification-before-completion)

**Files:**
- Modify: `README.md`
- Modify: `docs/architecture.md`

**Step 1: Write the failing test**

```python
# Add/adjust a docs-referenced CLI JSON shape assertion in tests/test_cli_generate_loop_json.py if needed.
```

**Step 2: Run full test suite**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest -v`
Expected: PASS.

**Step 3: Run manual CLI check**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m hiking_router.cli generate-loop --near "Roanoke, VA" --miles-min 12 --miles-max 15 --difficulty strenuous`
Expected: Valid JSON with `query`, `meta`, and `routes`.

**Step 4: Update docs**

Document:
- JSON response shape and field semantics.
- Cache behavior (`miss` first run, `hit/partial` warm run).
- Current v2 limits (ridge/scenic null placeholders).

**Step 5: Commit**

```bash
git add README.md docs/architecture.md tests/test_cli_generate_loop_json.py
git commit -m "docs: document v2 JSON contract and cache behavior"
```

## Implementation Notes

- Use @test-driven-development for each task (red -> green -> refactor).
- Keep adapter network code isolated behind tiny interfaces to simplify fixture-based testing.
- Treat rate-limiting/network failures as expected paths; prefer explicit errors over silent fallbacks.
- Keep response contract stable as soon as Task 2 lands.
