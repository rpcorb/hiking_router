from hiking_router.use_cases.generate_loop import generate_top_loops


def test_roanoke_strenuous_query_returns_ranked_results_shape():
    results = generate_top_loops({"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})
    assert isinstance(results, list)
    assert len(results) >= 1
