# V3 Live Ingestion and Real Terrain Metrics Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement pluggable live OSM + USGS ingestion with cache-first fallback and real DEM-derived elevation metrics while preserving the v2 JSON contract.

**Architecture:** Introduce provider config and shared HTTP fetch infrastructure, then upgrade OSM/USGS adapters to perform live fetch on cache miss with explicit fallback behavior. Keep use-case orchestration responsible for surfacing cache states/reasons and returning the existing JSON envelope shape.

**Tech Stack:** Python 3.13, pytest, pydantic, requests/httpx, typer, networkx, rasterio, numpy

---

### Task 1: Provider Config Model

**Files:**
- Create: `src/hiking_router/config/providers.py`
- Create: `tests/config/test_provider_config.py`

**Step 1: Write the failing test**

```python
from hiking_router.config.providers import ProviderConfig


def test_provider_config_defaults_to_overpass_and_tnm():
    cfg = ProviderConfig.from_env({})
    assert cfg.osm_provider == "overpass"
    assert cfg.usgs_provider == "tnm"
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/config/test_provider_config.py::test_provider_config_defaults_to_overpass_and_tnm -v`
Expected: FAIL with missing module/class.

**Step 3: Write minimal implementation**

```python
from pydantic import BaseModel


class ProviderConfig(BaseModel):
    osm_provider: str = "overpass"
    usgs_provider: str = "tnm"
    osm_base_url: str = "https://overpass-api.de/api/interpreter"
    usgs_base_url: str = "https://tnmaccess.nationalmap.gov/api/v1/products"
    timeout_seconds: int = 20
    retry_count: int = 3

    @classmethod
    def from_env(cls, env: dict[str, str]) -> "ProviderConfig":
        return cls(
            osm_provider=env.get("HIKING_ROUTER_OSM_PROVIDER", "overpass"),
            usgs_provider=env.get("HIKING_ROUTER_USGS_PROVIDER", "tnm"),
            osm_base_url=env.get("HIKING_ROUTER_OSM_BASE_URL", cls.model_fields["osm_base_url"].default),
            usgs_base_url=env.get("HIKING_ROUTER_USGS_BASE_URL", cls.model_fields["usgs_base_url"].default),
            timeout_seconds=int(env.get("HIKING_ROUTER_TIMEOUT_SECONDS", "20")),
            retry_count=int(env.get("HIKING_ROUTER_RETRY_COUNT", "3")),
        )
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/config/test_provider_config.py::test_provider_config_defaults_to_overpass_and_tnm -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/config/providers.py tests/config/test_provider_config.py
git commit -m "feat: add provider configuration model"
```

### Task 2: Shared Fetch Client with Retry/Errors

**Files:**
- Create: `src/hiking_router/providers/fetcher.py`
- Create: `tests/providers/test_fetcher_errors.py`

**Step 1: Write the failing test**

```python
import pytest
from hiking_router.providers.fetcher import parse_json_or_raise, FetchParseError


def test_parse_json_or_raise_raises_on_invalid_payload():
    with pytest.raises(FetchParseError):
        parse_json_or_raise("not-json")
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/providers/test_fetcher_errors.py::test_parse_json_or_raise_raises_on_invalid_payload -v`
Expected: FAIL with missing module.

**Step 3: Write minimal implementation**

```python
import json


class FetchError(Exception):
    pass


class FetchParseError(FetchError):
    pass


def parse_json_or_raise(payload: str) -> dict:
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise FetchParseError("Invalid JSON payload") from exc
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/providers/test_fetcher_errors.py::test_parse_json_or_raise_raises_on_invalid_payload -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/providers/fetcher.py tests/providers/test_fetcher_errors.py
git commit -m "feat: add shared fetch error primitives"
```

### Task 3: Overpass Provider Adapter (Live Payload Path)

**Files:**
- Create: `src/hiking_router/providers/overpass.py`
- Create: `tests/providers/test_overpass_provider.py`

**Step 1: Write the failing test**

```python
from hiking_router.providers.overpass import build_bbox_query


def test_build_bbox_query_contains_bbox_bounds():
    q = build_bbox_query((-80.0, 37.0, -79.0, 38.0))
    assert "37.0,-80.0,38.0,-79.0" in q
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/providers/test_overpass_provider.py::test_build_bbox_query_contains_bbox_bounds -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
def build_bbox_query(bbox: tuple[float, float, float, float]) -> str:
    min_lon, min_lat, max_lon, max_lat = bbox
    return f"[out:json];(way[\"highway\"~\"path|footway|track\"]({min_lat},{min_lon},{max_lat},{max_lon}););out body;>;out skel qt;"
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/providers/test_overpass_provider.py::test_build_bbox_query_contains_bbox_bounds -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/providers/overpass.py tests/providers/test_overpass_provider.py
git commit -m "feat: add overpass query builder for bbox ingestion"
```

### Task 4: TNM Provider Adapter (Product Selection)

**Files:**
- Create: `src/hiking_router/providers/tnm.py`
- Create: `tests/providers/test_tnm_provider.py`

**Step 1: Write the failing test**

```python
from hiking_router.providers.tnm import pick_first_download_url


def test_pick_first_download_url_returns_none_on_empty_items():
    assert pick_first_download_url({"items": []}) is None
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/providers/test_tnm_provider.py::test_pick_first_download_url_returns_none_on_empty_items -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
def pick_first_download_url(payload: dict) -> str | None:
    items = payload.get("items", [])
    if not items:
        return None
    return items[0].get("downloadURL")
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/providers/test_tnm_provider.py::test_pick_first_download_url_returns_none_on_empty_items -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/providers/tnm.py tests/providers/test_tnm_provider.py
git commit -m "feat: add TNM product selection helper"
```

### Task 5: Upgrade OSM Adapter to Provider-Based Fetch

**Files:**
- Modify: `src/hiking_router/adapters/osm_client.py`
- Create: `tests/adapters/test_osm_client_fallback.py`

**Step 1: Write the failing test**

```python
from hiking_router.adapters.osm_client import OSMClient


def test_osm_client_returns_partial_when_live_fails_but_cache_exists(tmp_path):
    client = OSMClient(cache_dir=tmp_path)
    tile_id = "z10-290-391"
    cached = tmp_path / "raw" / "osm" / f"{tile_id}.geojson"
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_text('{"type":"FeatureCollection","features":[]}')

    data, status = client.fetch_trails(tile_id=tile_id, bbox=(-80, 37, -79, 38), force_live=True)

    assert status in {"hit", "partial"}
    assert data["type"] == "FeatureCollection"
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/adapters/test_osm_client_fallback.py::test_osm_client_returns_partial_when_live_fails_but_cache_exists -v`
Expected: FAIL on signature/behavior mismatch.

**Step 3: Write minimal implementation**

```python
# support force_live path and fallback semantics
# if live fetch fails and cache exists -> return cached, "partial"
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/adapters/test_osm_client_fallback.py::test_osm_client_returns_partial_when_live_fails_but_cache_exists -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/adapters/osm_client.py tests/adapters/test_osm_client_fallback.py
git commit -m "feat: add OSM live-fetch fallback semantics"
```

### Task 6: Upgrade USGS Adapter to Provider-Based Fetch

**Files:**
- Modify: `src/hiking_router/adapters/usgs_client.py`
- Create: `tests/adapters/test_usgs_client_fallback.py`

**Step 1: Write the failing test**

```python
from hiking_router.adapters.usgs_client import USGSClient


def test_usgs_client_returns_partial_when_live_fails_but_cache_exists(tmp_path):
    client = USGSClient(cache_dir=tmp_path)
    tile_id = "z10-290-391"
    cached = tmp_path / "raw" / "usgs" / f"{tile_id}.tif"
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(b"dem")

    dem_path, status = client.fetch_dem(tile_id=tile_id, bbox=(-80, 37, -79, 38), force_live=True)

    assert status in {"hit", "partial"}
    assert dem_path.exists()
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/adapters/test_usgs_client_fallback.py::test_usgs_client_returns_partial_when_live_fails_but_cache_exists -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
# support force_live path and fallback semantics for DEM source
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/adapters/test_usgs_client_fallback.py::test_usgs_client_returns_partial_when_live_fails_but_cache_exists -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/adapters/usgs_client.py tests/adapters/test_usgs_client_fallback.py
git commit -m "feat: add USGS live-fetch fallback semantics"
```

### Task 7: DEM Sampling to Real Route Metrics

**Files:**
- Modify: `src/hiking_router/features/dem_sampling.py`
- Create: `tests/features/test_route_elevation_metrics.py`

**Step 1: Write the failing test**

```python
from hiking_router.features.dem_sampling import route_elevation_metrics


def test_route_elevation_metrics_returns_gain_and_gain_per_mile():
    metrics = route_elevation_metrics(samples=[100, 120, 110, 140], distance_miles=2.0)
    assert metrics["gain_ft"] > 0
    assert metrics["gain_per_mile_ft"] > 0
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/features/test_route_elevation_metrics.py::test_route_elevation_metrics_returns_gain_and_gain_per_mile -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
def route_elevation_metrics(samples: list[float], distance_miles: float) -> dict:
    gain_m = elevation_gain_from_profile(samples)
    gain_ft = gain_m * 3.28084
    gain_per_mile_ft = gain_ft / distance_miles if distance_miles > 0 else 0.0
    return {"gain_ft": gain_ft, "gain_per_mile_ft": gain_per_mile_ft}
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/features/test_route_elevation_metrics.py::test_route_elevation_metrics_returns_gain_and_gain_per_mile -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/features/dem_sampling.py tests/features/test_route_elevation_metrics.py
git commit -m "feat: add route elevation metric derivation from DEM samples"
```

### Task 8: Wire Live-Source Status and Reason in Use Case

**Files:**
- Modify: `src/hiking_router/use_cases/generate_loop.py`
- Create: `tests/use_cases/test_reason_on_partial_cache.py`

**Step 1: Write the failing test**

```python
from hiking_router.use_cases.generate_loop import generate_top_loops


def test_meta_reason_present_when_partial_cache_used(tmp_path, monkeypatch):
    monkeypatch.setenv("HIKING_ROUTER_CACHE_DIR", str(tmp_path))
    # First run seeds cache
    _ = generate_top_loops({"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})
    # Force live path to trigger fallback semantics
    payload = generate_top_loops({"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous", "force_live": True})
    if payload["meta"]["cache"]["osm"] == "partial" or payload["meta"]["cache"]["usgs"] == "partial":
        assert payload["meta"]["reason"] is not None
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/use_cases/test_reason_on_partial_cache.py::test_meta_reason_present_when_partial_cache_used -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
# propagate partial statuses and include explanatory reason in meta.reason
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/use_cases/test_reason_on_partial_cache.py::test_meta_reason_present_when_partial_cache_used -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/hiking_router/use_cases/generate_loop.py tests/use_cases/test_reason_on_partial_cache.py
git commit -m "feat: surface fallback reason when partial cache is used"
```

### Task 9: Contract and Integration Regression Gate

**Files:**
- Modify: `tests/test_cli_generate_loop_json.py`
- Modify: `tests/e2e/test_roanoke_query_fixture.py`

**Step 1: Write the failing test**

```python
# Add assertions for stable v2 envelope keys and route metric fields
```

**Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/test_cli_generate_loop_json.py tests/e2e/test_roanoke_query_fixture.py -v`
Expected: FAIL on missing/changed fields if contract drifted.

**Step 3: Write minimal implementation adjustments**

```python
# adjust formatting/mapping in use case and/or CLI to maintain stable contract
```

**Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/test_cli_generate_loop_json.py tests/e2e/test_roanoke_query_fixture.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add tests/test_cli_generate_loop_json.py tests/e2e/test_roanoke_query_fixture.py src/hiking_router/use_cases/generate_loop.py src/hiking_router/cli.py
git commit -m "test: enforce stable JSON contract under live-ingestion changes"
```

### Task 10: Documentation and Full Verification (@verification-before-completion)

**Files:**
- Modify: `README.md`
- Modify: `docs/architecture.md`

**Step 1: Run full test suite**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest -v`
Expected: PASS.

**Step 2: Run manual CLI check**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m hiking_router.cli generate-loop --near "Roanoke, VA" --miles-min 12 --miles-max 15 --difficulty strenuous`
Expected: Valid JSON, cache statuses, real metric fields present.

**Step 3: Update docs**

Document:
- Provider config env vars.
- Live fetch + fallback semantics.
- `meta.reason` behavior on degraded mode.

**Step 4: Re-run quick smoke tests**

Run: `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/test_cli_generate_loop_json.py tests/use_cases/test_generate_loop_v2_envelope.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add README.md docs/architecture.md
git commit -m "docs: add v3 live ingestion and fallback behavior"
```

## Implementation Notes

- Use @test-driven-development on every task.
- Keep network and parsing concerns isolated in provider/fetcher modules.
- Prefer deterministic fixtures/mocks for tests to avoid flaky external API dependence.
- Preserve response schema stability while values become more realistic.
