import networkx as nx

from hiking_router.search.heuristics import score_partial_state
from hiking_router.search.state import SearchState


def _edge_length_miles(graph: nx.Graph, u: str, v: str) -> float:
    length_m = float(graph.edges[u, v].get("length_m", 0.0))
    return length_m / 1609.34


def synthesize_loops_with_beam(
    graph: nx.Graph,
    start: str,
    beam_width: int,
    max_expansions: int,
    max_depth: int,
    max_candidates: int,
) -> list[list[str]]:
    beam: list[SearchState] = [SearchState.initial(origin=start)]
    candidates: list[list[str]] = []
    expansions = 0

    while beam and expansions < max_expansions and len(candidates) < max_candidates:
        next_beam: list[tuple[float, SearchState]] = []

        for state in beam:
            if len(state.path_nodes) > max_depth:
                continue

            for neighbor in sorted(str(n) for n in graph.neighbors(state.current_node)):
                expansions += 1
                edge_key = (state.current_node, neighbor)
                expanded = state.expand(
                    next_node=neighbor,
                    edge_key=edge_key,
                    edge_distance_miles=_edge_length_miles(graph, state.current_node, neighbor),
                    edge_gain_ft=0.0,
                )

                if neighbor == state.origin and len(state.path_nodes) >= 3:
                    loop = list(state.path_nodes)
                    if set(loop) not in [set(existing) for existing in candidates]:
                        candidates.append(loop)
                        if len(candidates) >= max_candidates:
                            break
                    continue

                if neighbor in state.path_nodes:
                    continue

                score = score_partial_state(
                    expanded,
                    target_miles=10.0,
                    estimated_return_miles=0.0,
                    ridge_bonus=0.0,
                    revisit_penalty=0.0,
                )
                next_beam.append((score, expanded))

                if expansions >= max_expansions:
                    break
            if expansions >= max_expansions or len(candidates) >= max_candidates:
                break

        next_beam.sort(key=lambda item: item[0], reverse=True)
        beam = [state for _, state in next_beam[:beam_width]]

    return candidates
