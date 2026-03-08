import numpy as np
import rasterio
from rasterio.transform import from_origin

from hiking_router.features.dem_sampling import profile_from_dem_artifact, route_elevation_metrics


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
