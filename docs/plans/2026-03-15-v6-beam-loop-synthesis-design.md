# V6 Terrain-Aware Beam Loop Synthesis Design

## Scope
Add a new search engine that synthesizes loops by expanding partial route states, rather than relying primarily on pre-existing graph cycles. The goal is to materially improve route discovery quality while preserving the existing CLI contract and keeping the legacy search path available as a fallback.

## Why This Is The Next Best Move
- The project already has useful terrain metrics and scoring, but candidate generation is still structurally conservative.
- A terrain-aware beam search changes the system from "score available loops" to "discover loops that should exist in the terrain graph."
- Every terrain signal already built (`ridge_fraction`, `summit_proximity_min_m`, `scenic_score`, elevation fit) becomes more valuable when it shapes search, not only ranking.

## Product Goal
Generate route candidates that are more distinctive, more terrain-driven, and less dependent on whatever `cycle_basis` happens to surface, while staying within bounded CLI latency and deterministic test behavior.

## Recommended Approach
Implement a bounded beam-search loop synthesizer as a parallel search engine:
- primary path: terrain-aware beam loop synthesis
- fallback path: existing cycle-based search when the new engine finds no viable loops or hits sparse/disconnected graph conditions

This keeps rollout safe while still delivering a real engine upgrade.

## Architecture

### New Modules
- `src/hiking_router/search/state.py`
  - defines the partial-route search state
- `src/hiking_router/search/heuristics.py`
  - scores partial states by future promise
- `src/hiking_router/search/closure.py`
  - estimates and validates loop closure quality
- `src/hiking_router/search/beam_loop_search.py`
  - orchestrates bounded expansion, beam pruning, and loop emission

### Existing Modules To Integrate
- `src/hiking_router/use_cases/generate_loop.py`
  - calls beam search first, legacy search second
- `src/hiking_router/search/diversity.py`
  - keeps post-search family pruning for emitted candidates
- `src/hiking_router/scoring/composite.py`
  - remains final scoring layer for completed loops

## Search State
Each partial route state should include:
- `origin`
- `current_node`
- `path_nodes`
- `used_edges`
- `distance_miles`
- `elevation_gain_ft`
- `ridge_accumulator`
- `best_summit_proximity_m`
- `revisit_penalty`
- `estimated_closure_miles`
- `heuristic_score`

The key idea is that the engine tracks route character while building the route, not only after the route is complete.

## Search Behavior
1. Choose one or more seed nodes.
2. Expand states along adjacent edges.
3. Score expansions using a terrain-aware heuristic.
4. Keep only the top states within a bounded beam.
5. When a state can close back to origin inside the requested distance band, emit a candidate loop.
6. Dedupe and diversify emitted loops before final scoring.

## Heuristic Design
The heuristic should favor:
- progress toward requested mileage
- strong loopability back to origin
- ridge continuity
- useful summit access
- likely difficulty fit
- novelty relative to already-emitted loop families

The heuristic should penalize:
- repeated edges
- excessive backtracking
- dead-end drift
- paths that overshoot distance too early
- near-duplicate route families

## Closure Logic
Closure must be explicit rather than incidental.
- estimate shortest plausible return distance to origin
- reject partial states that cannot close within the target band
- reward states that can close cleanly with minimal ugly backtracking

This is what allows the engine to synthesize loops that are not already obvious simple cycles.

## Rollout Strategy
- keep legacy search available as a fallback
- add a config switch or internal execution ordering:
  - try beam synthesis
  - if no candidates, fall back to current search
- preserve response contract and route payload shape

## Error Handling
- hard bounds on:
  - `beam_width`
  - `max_expansions`
  - `max_depth`
  - `max_candidates`
- if limits are reached:
  - return best candidates found so far
  - do not fail the request
- if graph is too sparse:
  - fall back to legacy search path

## Testing Strategy
- unit tests:
  - state expansion
  - heuristic ordering
  - closure feasibility
  - duplicate suppression
- integration tests:
  - beam search finds viable loops on known fixtures
  - beam search outperforms legacy candidate generation on selected graphs
- regression tests:
  - distance-band compliance
  - deterministic output under fixed fixtures
  - fallback to legacy search when beam returns none
- performance tests:
  - warm-cache latency remains bounded
  - expansion limits prevent runaway search

## Risks
- Search explosion if pruning is weak
- Poor heuristic tuning can create attractive but low-quality routes
- Debuggability is harder than the current cycle-basis approach

## Mitigations
- start with tight beam bounds
- keep heuristic components simple and transparent
- log or expose internal debug counters only in tests/dev mode
- keep legacy search fallback until beam search is proven

## Success Criteria
- top routes are materially less generic than legacy search output
- candidate sets show stronger terrain structure, not just higher final scores
- deterministic tests stay green
- warm-cache performance remains within budget
