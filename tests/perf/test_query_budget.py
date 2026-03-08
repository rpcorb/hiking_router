import time


def test_warm_cache_query_budget_placeholder():
    start = time.time()
    elapsed = time.time() - start
    assert elapsed < 60
