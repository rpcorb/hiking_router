# V4 Terrain Intelligence Roadmap Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deliver the next roadmap phase by populating terrain fields (`ridge_fraction`, `summit_proximity_min_m`, `scenic_score`) and improving route engine quality while preserving stable JSON contract and deterministic test behavior.

**Architecture:** Build in vertical milestones that each introduce one new terrain capability end-to-end (data ingestion -> feature computation -> route integration -> tests/docs). Keep route output schema stable; only replace `null` terrain placeholders with computed values as each milestone lands. Continue cache-first/live-fallback model and strict-live semantics from v3.

**Tech Stack:** Python 3.13, pytest, pydantic, networkx, numpy, rasterio, existing OSM/USGS provider stack

---

## Status Note (2026-03-11)

- V4 milestones A-E are complete and merged.
- Follow-on work moved to V5 planning:
  - live ridge/summit providers (`Overpass -> GNIS` for summits),
  - per-route DEM geometry sampling realism,
  - warm-cache performance hardening.

## Milestone Sequence

### Milestone A: Ridge/Watershed Metrics (Week 1-2)

**Objective:** Populate `routes[].terrain.ridge_fraction` from real ridge overlap.

**Tasks:**
1. Add ridge data source adapter and cache path strategy.
2. Normalize ridge geometries for overlap checks with route geometries.
3. Compute per-route ridge overlap fraction.
4. Integrate into `generate_top_loops` route payload.
5. Update response-contract tests for non-null ridge values.

**Key files:**
- Create: `src/hiking_router/adapters/ridge_client.py` (upgrade from stub)
- Create: `src/hiking_router/features/ridge_overlap.py`
- Modify: `src/hiking_router/use_cases/generate_loop.py`
- Create: `tests/features/test_ridge_overlap.py`
- Modify: `tests/test_cli_generate_loop_json.py`

**Verification commands:**
- `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/features/test_ridge_overlap.py -v`
- `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/test_cli_generate_loop_json.py -v`

**Definition of done:**
- `ridge_fraction` is numeric (0-1) for routes where ridge data is available.
- Fallback semantics documented for missing ridge coverage.

---

### Milestone B: Summit Proximity (Week 2-3)

**Objective:** Populate `routes[].terrain.summit_proximity_min_m` from a summit dataset.

**Tasks:**
1. Add summit data adapter (cache-first/live-fallback).
2. Add nearest-summit distance computation for route polylines.
3. Integrate proximity metric into route terrain payload.
4. Add edge-case handling (no summits within search radius).

**Key files:**
- Create: `src/hiking_router/adapters/summit_client.py`
- Create: `src/hiking_router/features/summit_proximity.py`
- Modify: `src/hiking_router/use_cases/generate_loop.py`
- Create: `tests/features/test_summit_proximity.py`
- Modify: `tests/use_cases/test_generate_loop_v2_envelope.py`

**Verification commands:**
- `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/features/test_summit_proximity.py -v`
- `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/use_cases/test_generate_loop_v2_envelope.py -v`

**Definition of done:**
- `summit_proximity_min_m` is populated when summit data exists, else explicitly `null` + reason.

---

### Milestone C: Scenic Score v1 (Week 3-4)

**Objective:** Replace `terrain.scenic_score: null` with a deterministic weighted score.

**Tasks:**
1. Define scenic factors and default weights.
2. Implement weighted score function and normalization bounds.
3. Expose score in route payload.
4. Add weight-config override via env/config.
5. Add stability tests using fixed fixtures.

**Key files:**
- Create: `src/hiking_router/scoring/scenic.py`
- Modify: `src/hiking_router/config/providers.py` (or create `config/scoring.py`)
- Modify: `src/hiking_router/use_cases/generate_loop.py`
- Create: `tests/scoring/test_scenic_score.py`
- Create: `tests/use_cases/test_scenic_score_stability.py`

**Verification commands:**
- `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/scoring/test_scenic_score.py -v`
- `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/use_cases/test_scenic_score_stability.py -v`

**Definition of done:**
- `scenic_score` is non-null and reproducible for fixture inputs.

---

### Milestone D: Route Engine Quality Upgrade (Week 4-6)

**Objective:** Improve candidate quality, diversity, and ranking behavior.

**Tasks:**
1. Add route-overlap similarity and diversity filtering.
2. Improve distance/elevation fit objective.
3. Add optional sustained-grade penalty/bonus in difficulty fit.
4. Benchmark route quality on multi-region fixtures.

**Key files:**
- Create: `src/hiking_router/search/diversity.py`
- Modify: `src/hiking_router/use_cases/generate_loop.py`
- Modify: `src/hiking_router/scoring/composite.py`
- Create: `tests/search/test_diversity_filter.py`
- Create: `tests/e2e/test_multi_region_quality.py`

**Verification commands:**
- `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/search/test_diversity_filter.py -v`
- `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/e2e/test_multi_region_quality.py -v`

**Definition of done:**
- Top-k results are materially less duplicate and better fit requested distance/difficulty.

---

### Milestone E: Data Quality and Reliability Hardening (Week 6-7)

**Objective:** Strengthen ingestion/validation robustness and regression safety.

**Tasks:**
1. Tighten OSM normalization validation (unsupported/invalid element handling).
2. Harden TNM download validation (file type/size/readability checks).
3. Expand strict-live and fallback regression matrix.
4. Ensure deterministic, no-network default test mode remains intact.

**Key files:**
- Modify: `src/hiking_router/graph/osm_normalize.py`
- Modify: `src/hiking_router/adapters/usgs_client.py`
- Modify: `src/hiking_router/providers/fetcher.py`
- Create: `tests/providers/test_live_failure_matrix.py`
- Create: `tests/graph/test_osm_normalization_robustness.py`

**Verification commands:**
- `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/providers/test_live_failure_matrix.py -v`
- `. .venv/bin/activate && PYTHONPATH=src python -m pytest tests/graph/test_osm_normalization_robustness.py -v`
- `. .venv/bin/activate && PYTHONPATH=src python -m pytest -q`

**Definition of done:**
- Failure modes are explicit and tested; full suite remains deterministic and fast.

---

## Cross-Cutting Constraints

1. Preserve top-level JSON contract:
- `query`, `meta`, `routes` keys remain stable.
- Terrain fields transition from null to computed values gradually by milestone.

2. Keep deterministic test defaults:
- Tests run with network disabled unless explicitly testing network wrappers.

3. Commit discipline:
- One commit per atomic feature/test slice.
- Include regression tests in same commit as behavior changes.

## Suggested Commit Pattern Per Milestone

1. Add failing tests.
2. Minimal implementation to pass.
3. Integration wiring.
4. Docs update.
5. Verification pass commit if needed.

## Final Verification Gate (end of V4)

Run:
- `. .venv/bin/activate && PYTHONPATH=src python -m pytest -q`
- `. .venv/bin/activate && PYTHONPATH=src python -m hiking_router.cli generate-loop --near "Roanoke, VA" --miles-min 12 --miles-max 15 --difficulty strenuous`

Expected:
- Deterministic green test suite.
- JSON response with non-null terrain metrics where data coverage exists.
- Clear `meta.reason` for degraded/insufficient-data scenarios.
