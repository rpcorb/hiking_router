import networkx as nx


def find_loops(graph: nx.Graph, start: int, max_loops: int = 3) -> list[list[int]]:
    loops: list[list[int]] = []
    for cycle in nx.cycle_basis(graph, root=start):
        loops.append(cycle)
        if len(loops) >= max_loops:
            break
    return loops
