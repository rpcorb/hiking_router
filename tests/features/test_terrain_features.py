from hiking_router.features.terrain import ridge_fraction


def test_ridge_fraction():
    assert ridge_fraction(total_m=1000, ridge_m=250) == 0.25
