import networkx as nx


def find_loops(graph: nx.Graph, start: int, max_loops: int = 3) -> list[list[int]]:
    loops: list[list[int]] = []
    for cycle in nx.cycle_basis(graph, root=start):
        loops.append(cycle)
        if len(loops) >= max_loops:
            break
    return loops


def filter_loops_by_distance_band(
    loops: list[list[int]],
    lengths: dict[tuple[int, ...], float],
    miles_min: float,
    miles_max: float,
) -> list[list[int]]:
    kept: list[list[int]] = []
    for loop in loops:
        d = lengths.get(tuple(loop))
        if d is not None and miles_min <= d <= miles_max:
            kept.append(loop)
    return kept
