import networkx as nx

from hiking_router.search.beam_loop_search import synthesize_loops_with_beam


def test_synthesize_loops_with_beam_finds_simple_cycle():
    graph = nx.Graph()
    graph.add_edge("a", "b", length_m=100.0)
    graph.add_edge("b", "c", length_m=100.0)
    graph.add_edge("c", "a", length_m=100.0)

    loops = synthesize_loops_with_beam(
        graph=graph,
        start="a",
        beam_width=5,
        max_expansions=20,
        max_depth=4,
        max_candidates=3,
    )

    assert loops
    assert set(loops[0]) == {"a", "b", "c"}


def test_synthesize_loops_with_beam_respects_max_candidates():
    graph = nx.Graph()
    graph.add_edge("a", "b", length_m=100.0)
    graph.add_edge("b", "c", length_m=100.0)
    graph.add_edge("c", "a", length_m=100.0)
    graph.add_edge("a", "d", length_m=100.0)
    graph.add_edge("d", "e", length_m=100.0)
    graph.add_edge("e", "a", length_m=100.0)

    loops = synthesize_loops_with_beam(
        graph=graph,
        start="a",
        beam_width=5,
        max_expansions=50,
        max_depth=4,
        max_candidates=1,
    )

    assert len(loops) == 1


def test_synthesize_loops_with_beam_returns_empty_when_no_cycle_exists():
    graph = nx.Graph()
    graph.add_edge("a", "b", length_m=100.0)
    graph.add_edge("b", "c", length_m=100.0)

    loops = synthesize_loops_with_beam(
        graph=graph,
        start="a",
        beam_width=5,
        max_expansions=20,
        max_depth=4,
        max_candidates=3,
    )

    assert loops == []
