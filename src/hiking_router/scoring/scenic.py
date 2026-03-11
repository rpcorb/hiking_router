from hiking_router.config.scoring import ScenicConfig


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


def scenic_score(
    ridge_fraction: float,
    summit_proximity_min_m: float | None,
    elevation_gain_per_mile_ft: float,
    cfg: ScenicConfig,
) -> float:
    ridge_component = _clamp_01(ridge_fraction)

    if summit_proximity_min_m is None:
        summit_component = 0.0
    else:
        summit_component = _clamp_01(
            1.0 - (summit_proximity_min_m / max(cfg.summit_max_distance_m, 1.0))
        )

    elevation_component = _clamp_01(
        elevation_gain_per_mile_ft / max(cfg.elevation_scale_ft_per_mile, 1.0)
    )

    total_weight = cfg.weight_ridge + cfg.weight_summit + cfg.weight_elevation
    if total_weight <= 0:
        return 0.0

    weighted = (
        cfg.weight_ridge * ridge_component
        + cfg.weight_summit * summit_component
        + cfg.weight_elevation * elevation_component
    ) / total_weight
    return _clamp_01(weighted)

