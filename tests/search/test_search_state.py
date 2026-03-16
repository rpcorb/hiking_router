from hiking_router.search.state import SearchState


def test_search_state_initializes_origin_and_path():
    state = SearchState.initial(origin="a")

    assert state.origin == "a"
    assert state.current_node == "a"
    assert state.path_nodes == ("a",)
    assert state.used_edges == frozenset()
    assert state.distance_miles == 0.0
    assert state.elevation_gain_ft == 0.0


def test_search_state_expand_updates_metrics_and_edge_usage():
    state = SearchState.initial(origin="a")

    expanded = state.expand(
        next_node="b",
        edge_key=("a", "b"),
        edge_distance_miles=1.25,
        edge_gain_ft=350.0,
    )

    assert expanded.origin == "a"
    assert expanded.current_node == "b"
    assert expanded.path_nodes == ("a", "b")
    assert expanded.used_edges == frozenset({("a", "b")})
    assert expanded.distance_miles == 1.25
    assert expanded.elevation_gain_ft == 350.0


def test_search_state_expand_accumulates_multiple_steps():
    state = SearchState.initial(origin="a")
    step1 = state.expand(
        next_node="b",
        edge_key=("a", "b"),
        edge_distance_miles=1.0,
        edge_gain_ft=100.0,
    )
    step2 = step1.expand(
        next_node="c",
        edge_key=("b", "c"),
        edge_distance_miles=0.5,
        edge_gain_ft=50.0,
    )

    assert step2.current_node == "c"
    assert step2.path_nodes == ("a", "b", "c")
    assert step2.used_edges == frozenset({("a", "b"), ("b", "c")})
    assert step2.distance_miles == 1.5
    assert step2.elevation_gain_ft == 150.0
