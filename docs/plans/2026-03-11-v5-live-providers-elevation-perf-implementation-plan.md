# V5 Live Providers, Elevation Realism, and Performance Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement real ridge/summit live ingestion (Overpass + GNIS fallback for summits), improve DEM profile realism from route geometry sampling, and add measurable warm-cache performance optimizations without breaking response contracts.

**Architecture:** Keep the existing layered pipeline and cache-first semantics. Extend providers/adapters for live ridge/summit ingestion, preserve strict-live behavior, and surface explicit degradation reasons when force-live refreshes partially fail. Upgrade elevation computation to sample along route geometry and add perf instrumentation/tests to prevent regressions.

**Tech Stack:** Python 3.13, pytest, pydantic, networkx, rasterio, urllib-based provider fetchers

---

### Task 1: Add Overpass Ridge/Summit Provider Support

**Files:**
- Modify: `src/hiking_router/providers/overpass.py`
- Test: `tests/providers/test_overpass_ridge_summit_queries.py`

**Step 1: Write failing provider tests**
- Add tests for:
  - `build_ridge_query(bbox)` includes ridge-relevant tags and bbox.
  - `build_summit_query(bbox)` includes summit peak tags and bbox.
  - `fetch_overpass_ridges(...)` returns normalized FeatureCollection(LineString).
  - `fetch_overpass_summits(...)` returns normalized FeatureCollection(Point).

**Step 2: Run tests to verify RED**
- Run: `PYTHONPATH=src python -m pytest tests/providers/test_overpass_ridge_summit_queries.py -v`
- Expected: FAIL due missing functions.

**Step 3: Implement minimal provider functions**
- Add query builders.
- Add fetch wrappers reusing existing Overpass HTTP helper paths.
- Normalize payload shapes and coordinate ordering consistently.

**Step 4: Run tests to verify GREEN**
- Run same command; expected PASS.

**Step 5: Commit**
```bash
git add src/hiking_router/providers/overpass.py tests/providers/test_overpass_ridge_summit_queries.py
git commit -m "feat(providers): add overpass ridge and summit fetch helpers"
```

---

### Task 2: Add GNIS Summit Provider and Normalization

**Files:**
- Create: `src/hiking_router/providers/gnis.py`
- Test: `tests/providers/test_gnis_provider.py`

**Step 1: Write failing GNIS provider tests**
- Cover parse success, malformed payload handling, and normalization to FeatureCollection(Point).

**Step 2: Run tests to verify RED**
- Run: `PYTHONPATH=src python -m pytest tests/providers/test_gnis_provider.py -v`
- Expected: FAIL (module missing).

**Step 3: Implement minimal GNIS provider**
- Add fetch wrapper.
- Add robust parse/normalize (ignore malformed entries).

**Step 4: Run tests to verify GREEN**
- Expected PASS.

**Step 5: Commit**
```bash
git add src/hiking_router/providers/gnis.py tests/providers/test_gnis_provider.py
git commit -m "feat(providers): add gnis summit provider"
```

---

### Task 3: Add Summit Aggregator Adapter (Overpass -> GNIS)

**Files:**
- Create: `src/hiking_router/adapters/summit_aggregator.py`
- Modify: `src/hiking_router/adapters/summit_client.py` (or replace with wrapper)
- Test: `tests/adapters/test_summit_aggregator.py`

**Step 1: Write failing aggregator tests**
- Provider priority ordering.
- GNIS fallback when Overpass fails/empty.
- Point dedupe behavior.
- Cache write/read semantics (`hit|miss|partial`).

**Step 2: Run tests to verify RED**
- Run: `PYTHONPATH=src python -m pytest tests/adapters/test_summit_aggregator.py -v`

**Step 3: Implement minimal aggregator**
- Accept provider callables.
- Merge + dedupe points by rounded lat/lon + name.
- Persist merged cache artifact.

**Step 4: Run tests to verify GREEN**
- Expected PASS.

**Step 5: Commit**
```bash
git add src/hiking_router/adapters/summit_aggregator.py src/hiking_router/adapters/summit_client.py tests/adapters/test_summit_aggregator.py
git commit -m "feat(adapters): add summit provider aggregation and fallback"
```

---

### Task 4: Wire Real Live Ridge/Summit Providers into Use Case

**Files:**
- Modify: `src/hiking_router/adapters/ridge_client.py`
- Modify: `src/hiking_router/use_cases/generate_loop.py`
- Test: `tests/use_cases/test_reason_on_live_degradation.py`
- Modify: `tests/use_cases/test_generate_loop_v2_envelope.py`

**Step 1: Write failing use-case degradation tests**
- `force_live=true` and degraded refresh should still return routes with non-null `meta.reason`.
- Ensure reason references degraded sources.

**Step 2: Run tests to verify RED**
- Run: `PYTHONPATH=src python -m pytest tests/use_cases/test_reason_on_live_degradation.py tests/use_cases/test_generate_loop_v2_envelope.py -v`

**Step 3: Implement minimal wiring**
- Ridge live fetch uses Overpass-based provider.
- Summit fetch uses aggregator adapter.
- Track degraded source states and compose reason text.

**Step 4: Run tests to verify GREEN**
- Expected PASS.

**Step 5: Commit**
```bash
git add src/hiking_router/adapters/ridge_client.py src/hiking_router/use_cases/generate_loop.py tests/use_cases/test_reason_on_live_degradation.py tests/use_cases/test_generate_loop_v2_envelope.py
git commit -m "feat(usecase): wire live ridge/summit providers with degradation reason"
```

---

### Task 5: Improve Elevation Profile Realism via Route Geometry Sampling

**Files:**
- Modify: `src/hiking_router/features/dem_sampling.py`
- Modify: `src/hiking_router/use_cases/generate_loop.py`
- Test: `tests/features/test_route_geometry_dem_sampling.py`
- Modify: `tests/features/test_dem_raster_sampling.py`

**Step 1: Write failing geometry sampling tests**
- Profile sampling uses provided route coordinates against raster.
- Gains differ for distinct loop geometries over same DEM.

**Step 2: Run tests to verify RED**
- Run: `PYTHONPATH=src python -m pytest tests/features/test_route_geometry_dem_sampling.py tests/features/test_dem_raster_sampling.py -v`

**Step 3: Implement minimal sampling upgrade**
- Add function to sample DEM along polyline points.
- Use route geometry from selected loop edges instead of artifact-only fallback when possible.

**Step 4: Run tests to verify GREEN**
- Expected PASS.

**Step 5: Commit**
```bash
git add src/hiking_router/features/dem_sampling.py src/hiking_router/use_cases/generate_loop.py tests/features/test_route_geometry_dem_sampling.py tests/features/test_dem_raster_sampling.py
git commit -m "feat(elevation): sample dem profile along route geometry"
```

---

### Task 6: Add Warm-Cache Performance Harness and Optimizations

**Files:**
- Modify: `src/hiking_router/use_cases/generate_loop.py`
- Modify: `src/hiking_router/scoring/scenic.py` (remove duplicate scenic computations in loop)
- Test: `tests/perf/test_warm_cache_latency.py`
- Modify: `tests/perf/test_query_budget.py`

**Step 1: Write failing perf tests**
- Add warm-cache latency assertion for representative query.
- Add deterministic budget check for repeated call.

**Step 2: Run tests to verify RED**
- Run: `PYTHONPATH=src python -m pytest tests/perf/test_warm_cache_latency.py tests/perf/test_query_budget.py -v`

**Step 3: Implement minimal optimizations**
- Compute scenic score once per route.
- Cache reusable route point arrays.
- Avoid repeated conversions inside scoring loop.

**Step 4: Run tests to verify GREEN**
- Expected PASS.

**Step 5: Commit**
```bash
git add src/hiking_router/use_cases/generate_loop.py src/hiking_router/scoring/scenic.py tests/perf/test_warm_cache_latency.py tests/perf/test_query_budget.py
git commit -m "perf(route): add warm-cache budget tests and hot-path optimizations"
```

---

### Task 7: Documentation and Contract Updates

**Files:**
- Modify: `README.md`
- Modify: `docs/plans/2026-03-10-v4-roadmap-implementation-plan.md` (status note section)

**Step 1: Write failing docs-contract check (if available) or checklist**
- If no docs test harness exists, define manual verification checklist in commit notes.

**Step 2: Update docs**
- Provider priority (`Overpass -> GNIS` for summits).
- Degradation reason semantics.
- Elevation realism behavior.
- Performance benchmark expectations.

**Step 3: Run related tests**
- Run: `PYTHONPATH=src python -m pytest tests/test_cli_generate_loop_json.py tests/models/test_response_contract.py -v`

**Step 4: Commit**
```bash
git add README.md docs/plans/2026-03-10-v4-roadmap-implementation-plan.md
git commit -m "docs: describe live provider fallback, realism, and perf behavior"
```

---

### Task 8: Final Verification Gate

**Files:**
- No code changes expected.

**Step 1: Run full suite**
- Run: `PYTHONPATH=src python -m pytest -q`
- Expected: all tests pass.

**Step 2: Run CLI verification query**
- Run: `PYTHONPATH=src python -m hiking_router.cli generate-loop --near "Roanoke, VA" --miles-min 12 --miles-max 15 --difficulty strenuous`
- Expected: valid JSON envelope, populated terrain metrics where coverage exists, and explicit degradation reason when live refresh degrades.

**Step 3: Commit verification note (optional, only if artifacts updated)**
```bash
# only if files changed
git add <updated-files>
git commit -m "chore: finalize v5 verification"
```

---

## Cross-Cutting Rules
- Preserve top-level JSON contract (`query`, `meta`, `routes`).
- Keep deterministic no-network defaults in tests.
- Use TDD for every behavior change.
- Keep commits atomic and include tests in same commit as behavior changes.
