import numpy as np
import rasterio
from rasterio.transform import from_origin

from hiking_router.features.dem_sampling import profile_from_dem_route_geometry


def test_profile_from_dem_route_geometry_samples_in_route_order(tmp_path):
    dem_path = tmp_path / "dem.tif"
    data = np.array(
        [
            [100.0, 110.0, 120.0],
            [130.0, 140.0, 150.0],
            [160.0, 170.0, 180.0],
        ],
        dtype="float32",
    )
    with rasterio.open(
        dem_path,
        "w",
        driver="GTiff",
        height=3,
        width=3,
        count=1,
        dtype="float32",
        transform=from_origin(0, 3, 1, 1),
    ) as dst:
        dst.write(data, 1)

    route_points = [(2.5, 0.5), (1.5, 1.5), (0.5, 2.5)]  # (lat, lon)
    profile = profile_from_dem_route_geometry(dem_path, route_points)

    assert profile == [100.0, 140.0, 180.0]


def test_profile_from_dem_route_geometry_returns_fallback_for_empty_points(tmp_path):
    dem_path = tmp_path / "dem.tif"
    data = np.array([[100.0]], dtype="float32")
    with rasterio.open(
        dem_path,
        "w",
        driver="GTiff",
        height=1,
        width=1,
        count=1,
        dtype="float32",
        transform=from_origin(0, 1, 1, 1),
    ) as dst:
        dst.write(data, 1)

    profile = profile_from_dem_route_geometry(dem_path, [])
    assert len(profile) >= 1
    assert profile[0] == 100.0
