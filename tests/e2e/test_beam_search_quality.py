import networkx as nx

from hiking_router.search.beam_loop_search import synthesize_loops_with_beam
from hiking_router.search.loop_search import find_loops


def test_beam_search_discovers_outer_loop_not_present_in_cycle_basis():
    graph = nx.Graph()
    for u, v in [
        ("a", "b"),
        ("b", "c"),
        ("c", "d"),
        ("d", "a"),
        ("a", "c"),
    ]:
        graph.add_edge(u, v, length_m=100.0)

    legacy = find_loops(graph, start="a", max_loops=10)
    beam = synthesize_loops_with_beam(
        graph=graph,
        start="a",
        beam_width=20,
        max_expansions=200,
        max_depth=6,
        max_candidates=10,
    )

    assert {"a", "b", "c", "d"} not in [set(loop) for loop in legacy]
    assert {"a", "b", "c", "d"} in [set(loop) for loop in beam]
