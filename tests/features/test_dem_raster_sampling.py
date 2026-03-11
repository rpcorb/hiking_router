import numpy as np
import rasterio
from rasterio.transform import from_origin

from hiking_router.features.dem_sampling import (
    profile_from_dem_artifact,
    profile_from_dem_route_geometry,
    route_elevation_metrics,
)


def test_profile_from_dem_artifact_reads_real_raster(tmp_path):
    dem_path = tmp_path / "dem.tif"
    data = np.array([[100.0, 110.0], [120.0, 130.0]], dtype="float32")
    with rasterio.open(
        dem_path,
        "w",
        driver="GTiff",
        height=2,
        width=2,
        count=1,
        dtype="float32",
        transform=from_origin(0, 2, 1, 1),
    ) as dst:
        dst.write(data, 1)

    profile = profile_from_dem_artifact(dem_path)
    metrics = route_elevation_metrics(samples=profile, distance_miles=1.0)

    assert len(profile) >= 2
    assert metrics["gain_ft"] > 0


def test_profile_from_dem_route_geometry_differs_by_route_points(tmp_path):
    dem_path = tmp_path / "dem.tif"
    data = np.array(
        [[100.0, 110.0], [120.0, 130.0]],
        dtype="float32",
    )
    with rasterio.open(
        dem_path,
        "w",
        driver="GTiff",
        height=2,
        width=2,
        count=1,
        dtype="float32",
        transform=from_origin(0, 2, 1, 1),
    ) as dst:
        dst.write(data, 1)

    route_a = [(1.5, 0.5), (0.5, 1.5)]  # top-left to bottom-right
    route_b = [(0.5, 0.5), (1.5, 1.5)]  # bottom-left to top-right

    profile_a = profile_from_dem_route_geometry(dem_path, route_a)
    profile_b = profile_from_dem_route_geometry(dem_path, route_b)

    assert profile_a != profile_b
