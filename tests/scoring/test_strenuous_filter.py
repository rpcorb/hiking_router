from hiking_router.scoring.difficulty import is_strenuous


def test_strenuous_requires_min_gain_per_mile():
    assert is_strenuous(gain_per_mile_ft=600, threshold_ft_per_mile=500) is True
    assert is_strenuous(gain_per_mile_ft=300, threshold_ft_per_mile=500) is False
