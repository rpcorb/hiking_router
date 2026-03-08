from hiking_router.search.loop_search import filter_loops_by_distance_band


def test_filters_loops_outside_distance_band():
    loops = [[1, 2, 3], [1, 4, 5]]
    lengths = {(1, 2, 3): 13.0, (1, 4, 5): 9.0}
    out = filter_loops_by_distance_band(loops, lengths, miles_min=12, miles_max=15)
    assert out == [[1, 2, 3]]
