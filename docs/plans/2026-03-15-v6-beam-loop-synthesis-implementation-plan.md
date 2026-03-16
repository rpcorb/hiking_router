# V6 Terrain-Aware Beam Loop Synthesis Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a bounded terrain-aware beam-search loop synthesizer that improves route discovery quality while preserving the existing CLI response contract and retaining the legacy search path as a fallback.

**Architecture:** Introduce a new search stack centered on partial-route states, heuristic beam pruning, and explicit closure checks. Integrate the new engine into `generate_top_loops` as the preferred candidate generator, with the existing cycle-based search retained as a safe fallback during rollout.

**Tech Stack:** Python 3.13, pytest, networkx, existing terrain feature and scoring modules

---

### Task 1: Add Search State Model

**Files:**
- Create: `src/hiking_router/search/state.py`
- Test: `tests/search/test_search_state.py`

**Step 1: Write the failing test**
- Add tests covering:
  - state construction
  - edge reuse tracking
  - distance/elevation accumulator updates

**Step 2: Run test to verify it fails**
- Run: `PYTHONPATH=src python -m pytest tests/search/test_search_state.py -v`
- Expected: FAIL because module is missing.

**Step 3: Write minimal implementation**
- Add a simple state dataclass with fields for node/path/metrics and helper methods for expansion.

**Step 4: Run test to verify it passes**
- Run the same command; expected PASS.

**Step 5: Commit**
```bash
git add src/hiking_router/search/state.py tests/search/test_search_state.py
git commit -m "feat(search): add beam-search route state model"
```

---

### Task 2: Add Closure Feasibility Logic

**Files:**
- Create: `src/hiking_router/search/closure.py`
- Test: `tests/search/test_closure.py`

**Step 1: Write the failing test**
- Cover:
  - estimated return distance
  - acceptance when a loop can close inside the band
  - rejection when closure is implausible

**Step 2: Run test to verify it fails**
- Run: `PYTHONPATH=src python -m pytest tests/search/test_closure.py -v`

**Step 3: Write minimal implementation**
- Add helpers that evaluate closure viability against target mileage bounds.

**Step 4: Run test to verify it passes**
- Expected PASS.

**Step 5: Commit**
```bash
git add src/hiking_router/search/closure.py tests/search/test_closure.py
git commit -m "feat(search): add loop closure feasibility checks"
```

---

### Task 3: Add Terrain-Aware Heuristic Scoring For Partial States

**Files:**
- Create: `src/hiking_router/search/heuristics.py`
- Test: `tests/search/test_beam_heuristics.py`

**Step 1: Write the failing test**
- Cover heuristic ordering for:
  - better loopability
  - stronger ridge continuity
  - lower backtracking penalty
  - better distance trajectory

**Step 2: Run test to verify it fails**
- Run: `PYTHONPATH=src python -m pytest tests/search/test_beam_heuristics.py -v`

**Step 3: Write minimal implementation**
- Add a transparent weighted heuristic function using existing route-quality signals where available.

**Step 4: Run test to verify it passes**
- Expected PASS.

**Step 5: Commit**
```bash
git add src/hiking_router/search/heuristics.py tests/search/test_beam_heuristics.py
git commit -m "feat(search): add beam-search heuristic scoring"
```

---

### Task 4: Implement Bounded Beam Loop Search

**Files:**
- Create: `src/hiking_router/search/beam_loop_search.py`
- Test: `tests/search/test_beam_loop_search.py`

**Step 1: Write the failing test**
- Cover:
  - simple loop discovery
  - beam width pruning
  - max expansion bounds
  - emitted loop candidate structure

**Step 2: Run test to verify it fails**
- Run: `PYTHONPATH=src python -m pytest tests/search/test_beam_loop_search.py -v`

**Step 3: Write minimal implementation**
- Add bounded state expansion with:
  - beam pruning
  - closure checks
  - candidate emission
  - deterministic ordering

**Step 4: Run test to verify it passes**
- Expected PASS.

**Step 5: Commit**
```bash
git add src/hiking_router/search/beam_loop_search.py tests/search/test_beam_loop_search.py
git commit -m "feat(search): add bounded beam loop synthesis engine"
```

---

### Task 5: Integrate Beam Search Into Route Generation With Fallback

**Files:**
- Modify: `src/hiking_router/use_cases/generate_loop.py`
- Modify: `src/hiking_router/search/loop_search.py`
- Test: `tests/use_cases/test_beam_search_fallback.py`
- Modify: `tests/use_cases/test_generate_loop_top3.py`

**Step 1: Write the failing test**
- Cover:
  - beam search is attempted first
  - legacy search is used when beam search returns no candidates
  - output contract remains unchanged

**Step 2: Run test to verify it fails**
- Run: `PYTHONPATH=src python -m pytest tests/use_cases/test_beam_search_fallback.py tests/use_cases/test_generate_loop_top3.py -v`

**Step 3: Write minimal implementation**
- Wire beam search into `generate_top_loops`.
- Preserve legacy fallback behavior.

**Step 4: Run test to verify it passes**
- Expected PASS.

**Step 5: Commit**
```bash
git add src/hiking_router/use_cases/generate_loop.py src/hiking_router/search/loop_search.py tests/use_cases/test_beam_search_fallback.py tests/use_cases/test_generate_loop_top3.py
git commit -m "feat(usecase): prefer beam loop synthesis with legacy fallback"
```

---

### Task 6: Add Quality Comparison Fixtures

**Files:**
- Create: `tests/e2e/test_beam_search_quality.py`
- Modify: `tests/e2e/test_multi_region_quality.py`

**Step 1: Write the failing test**
- Add a fixture where beam search should find a better loop family than legacy search.
- Assert stronger fit or more terrain-structured output.

**Step 2: Run test to verify it fails**
- Run: `PYTHONPATH=src python -m pytest tests/e2e/test_beam_search_quality.py tests/e2e/test_multi_region_quality.py -v`

**Step 3: Write minimal implementation**
- Adjust beam-search integration or heuristic weighting only as needed to satisfy the fixture.

**Step 4: Run test to verify it passes**
- Expected PASS.

**Step 5: Commit**
```bash
git add tests/e2e/test_beam_search_quality.py tests/e2e/test_multi_region_quality.py
git commit -m "test(search): add beam-search quality fixtures"
```

---

### Task 7: Add Search Bounds And Performance Guardrails

**Files:**
- Modify: `src/hiking_router/search/beam_loop_search.py`
- Test: `tests/perf/test_beam_search_budget.py`
- Modify: `tests/perf/test_warm_cache_latency.py`

**Step 1: Write the failing test**
- Cover:
  - bounded expansions
  - warm-cache latency guardrail
  - deterministic result count under fixed fixtures

**Step 2: Run test to verify it fails**
- Run: `PYTHONPATH=src python -m pytest tests/perf/test_beam_search_budget.py tests/perf/test_warm_cache_latency.py -v`

**Step 3: Write minimal implementation**
- Add hard limits and deterministic pruning order.

**Step 4: Run test to verify it passes**
- Expected PASS.

**Step 5: Commit**
```bash
git add src/hiking_router/search/beam_loop_search.py tests/perf/test_beam_search_budget.py tests/perf/test_warm_cache_latency.py
git commit -m "perf(search): bound beam search and add latency guardrails"
```

---

### Task 8: Documentation And Verification

**Files:**
- Modify: `README.md`
- Create: `docs/plans/2026-03-15-v6-beam-loop-synthesis-design.md` (already created)
- Create: `docs/plans/2026-03-15-v6-beam-loop-synthesis-implementation-plan.md` (already created)

**Step 1: Update docs**
- Describe:
  - beam-search-first candidate generation
  - legacy fallback behavior
  - bounded search safety limits

**Step 2: Run contract and full verification**
- Run: `PYTHONPATH=src python -m pytest tests/test_cli_generate_loop_json.py tests/models/test_response_contract.py -v`
- Run: `PYTHONPATH=src python -m pytest -q`
- Run: `PYTHONPATH=src python -m hiking_router.cli generate-loop --near "Roanoke, VA" --miles-min 12 --miles-max 15 --difficulty strenuous`

**Step 3: Commit**
```bash
git add README.md
git commit -m "docs: describe beam-search route synthesis"
```

---

## Cross-Cutting Rules
- Preserve top-level JSON contract.
- Keep deterministic tests and explicit search bounds.
- Follow TDD strictly for every new behavior.
- Keep legacy search path available until beam search is proven by fixtures and perf tests.
