from pydantic import BaseModel


class ScenicConfig(BaseModel):
    weight_ridge: float = 0.45
    weight_summit: float = 0.35
    weight_elevation: float = 0.20
    summit_max_distance_m: float = 2000.0
    elevation_scale_ft_per_mile: float = 1500.0

    @classmethod
    def from_env(cls, env: dict[str, str]) -> "ScenicConfig":
        return cls(
            weight_ridge=float(
                env.get(
                    "HIKING_ROUTER_SCENIC_WEIGHT_RIDGE",
                    str(cls.model_fields["weight_ridge"].default),
                )
            ),
            weight_summit=float(
                env.get(
                    "HIKING_ROUTER_SCENIC_WEIGHT_SUMMIT",
                    str(cls.model_fields["weight_summit"].default),
                )
            ),
            weight_elevation=float(
                env.get(
                    "HIKING_ROUTER_SCENIC_WEIGHT_ELEVATION",
                    str(cls.model_fields["weight_elevation"].default),
                )
            ),
            summit_max_distance_m=float(
                env.get(
                    "HIKING_ROUTER_SCENIC_SUMMIT_MAX_DISTANCE_M",
                    str(cls.model_fields["summit_max_distance_m"].default),
                )
            ),
            elevation_scale_ft_per_mile=float(
                env.get(
                    "HIKING_ROUTER_SCENIC_ELEVATION_SCALE_FT_PER_MILE",
                    str(cls.model_fields["elevation_scale_ft_per_mile"].default),
                )
            ),
        )

