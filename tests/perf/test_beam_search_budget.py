import networkx as nx

from hiking_router.search.beam_loop_search import synthesize_loops_with_beam


def test_beam_search_budget_respects_max_expansions_and_returns_bounded_candidates():
    graph = nx.Graph()
    for idx in range(8):
        graph.add_edge(str(idx), str((idx + 1) % 8), length_m=100.0)
    graph.add_edge("0", "4", length_m=100.0)
    graph.add_edge("1", "5", length_m=100.0)
    graph.add_edge("2", "6", length_m=100.0)
    graph.add_edge("3", "7", length_m=100.0)

    loops = synthesize_loops_with_beam(
        graph=graph,
        start="0",
        beam_width=3,
        max_expansions=10,
        max_depth=6,
        max_candidates=2,
    )

    assert len(loops) <= 2
