import networkx as nx
from hiking_router.search.loop_search import find_loops


def test_find_loops_returns_simple_cycle():
    g = nx.Graph()
    g.add_edges_from([(1, 2), (2, 3), (3, 1)])
    loops = find_loops(g, start=1, max_loops=3)
    assert len(loops) >= 1
