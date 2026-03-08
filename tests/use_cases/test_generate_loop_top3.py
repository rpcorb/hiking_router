from hiking_router.use_cases.generate_loop import generate_top_loops


def test_generate_top_loops_returns_three_or_fewer_ranked_results():
    results = generate_top_loops(query={"near": "Roanoke, VA", "miles_min": 12, "miles_max": 15, "difficulty": "strenuous"})
    assert len(results) <= 3
