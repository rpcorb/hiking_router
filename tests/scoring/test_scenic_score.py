from hiking_router.config.scoring import ScenicConfig
from hiking_router.scoring.scenic import scenic_score


def test_scenic_score_is_bounded_and_improves_with_better_inputs():
    weak = scenic_score(
        ridge_fraction=0.1,
        summit_proximity_min_m=1800.0,
        elevation_gain_per_mile_ft=200.0,
        cfg=ScenicConfig(),
    )
    strong = scenic_score(
        ridge_fraction=0.8,
        summit_proximity_min_m=150.0,
        elevation_gain_per_mile_ft=1200.0,
        cfg=ScenicConfig(),
    )
    assert 0.0 <= weak <= 1.0
    assert 0.0 <= strong <= 1.0
    assert strong > weak


def test_scenic_config_reads_weight_overrides_from_env():
    cfg = ScenicConfig.from_env(
        {
            "HIKING_ROUTER_SCENIC_WEIGHT_RIDGE": "0.6",
            "HIKING_ROUTER_SCENIC_WEIGHT_SUMMIT": "0.3",
            "HIKING_ROUTER_SCENIC_WEIGHT_ELEVATION": "0.1",
            "HIKING_ROUTER_SCENIC_SUMMIT_MAX_DISTANCE_M": "3000",
            "HIKING_ROUTER_SCENIC_ELEVATION_SCALE_FT_PER_MILE": "1000",
        }
    )
    assert cfg.weight_ridge == 0.6
    assert cfg.weight_summit == 0.3
    assert cfg.weight_elevation == 0.1
    assert cfg.summit_max_distance_m == 3000.0
    assert cfg.elevation_scale_ft_per_mile == 1000.0

