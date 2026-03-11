from hiking_router.search.diversity import (
    loop_overlap_similarity,
    select_diverse_loops,
)


def test_loop_overlap_similarity_uses_jaccard_on_nodes():
    a = ["1", "2", "3", "4"]
    b = ["2", "3", "4", "5"]
    similarity = loop_overlap_similarity(a, b)
    assert round(similarity, 2) == 0.60


def test_select_diverse_loops_rejects_high_overlap_candidates():
    candidates = [
        ["1", "2", "3", "4"],
        ["1", "2", "3", "4", "5"],  # high overlap with first loop
        ["8", "9", "10", "11"],
    ]
    selected = select_diverse_loops(
        candidates=candidates,
        max_loops=3,
        max_similarity=0.7,
    )
    assert selected == [
        ["1", "2", "3", "4"],
        ["8", "9", "10", "11"],
    ]
