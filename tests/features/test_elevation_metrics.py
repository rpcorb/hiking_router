from hiking_router.features.elevation import gain_per_mile


def test_gain_per_mile():
    assert round(gain_per_mile(gain_m=600, length_m=1609.34), 2) == 600.00
