def estimated_total_miles_with_closure(
    distance_so_far_miles: float,
    estimated_return_miles: float,
) -> float:
    return distance_so_far_miles + estimated_return_miles


def can_close_within_band(
    distance_so_far_miles: float,
    estimated_return_miles: float,
    miles_min: float,
    miles_max: float,
) -> bool:
    total = estimated_total_miles_with_closure(
        distance_so_far_miles=distance_so_far_miles,
        estimated_return_miles=estimated_return_miles,
    )
    return miles_min <= total <= miles_max
