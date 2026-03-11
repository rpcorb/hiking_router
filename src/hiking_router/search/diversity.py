def loop_overlap_similarity(loop_a: list[str], loop_b: list[str]) -> float:
    set_a = set(loop_a)
    set_b = set(loop_b)
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 0.0
    inter = set_a & set_b
    return len(inter) / len(union)


def select_diverse_loops(
    candidates: list[list[str]],
    max_loops: int,
    max_similarity: float = 0.75,
) -> list[list[str]]:
    selected: list[list[str]] = []
    for candidate in candidates:
        if len(selected) >= max_loops:
            break
        if all(
            loop_overlap_similarity(candidate, chosen) <= max_similarity
            for chosen in selected
        ):
            selected.append(candidate)
    return selected

