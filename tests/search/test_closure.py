from hiking_router.search.closure import can_close_within_band
from hiking_router.search.closure import estimated_total_miles_with_closure


def test_estimated_total_miles_with_closure_adds_return_distance():
    total = estimated_total_miles_with_closure(
        distance_so_far_miles=6.0,
        estimated_return_miles=2.5,
    )

    assert total == 8.5


def test_can_close_within_band_accepts_viable_loop():
    assert can_close_within_band(
        distance_so_far_miles=8.0,
        estimated_return_miles=3.0,
        miles_min=10.0,
        miles_max=12.0,
    ) is True


def test_can_close_within_band_rejects_overshoot():
    assert can_close_within_band(
        distance_so_far_miles=11.0,
        estimated_return_miles=2.5,
        miles_min=10.0,
        miles_max=12.0,
    ) is False
