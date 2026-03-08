import pytest
from hiking_router.models.query import LoopQuery


def test_query_rejects_invalid_distance_range():
    with pytest.raises(ValueError):
        LoopQuery(near="Roanoke, VA", miles_min=15, miles_max=12, difficulty="strenuous")
