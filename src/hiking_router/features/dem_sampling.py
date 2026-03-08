from pathlib import Path


def elevation_gain_from_profile(samples: list[float]) -> float:
    gain = 0.0
    for a, b in zip(samples, samples[1:]):
        if b > a:
            gain += b - a
    return gain


def route_elevation_metrics(samples: list[float], distance_miles: float) -> dict:
    gain_m = elevation_gain_from_profile(samples)
    gain_ft = gain_m * 3.28084
    gain_per_mile_ft = gain_ft / distance_miles if distance_miles > 0 else 0.0
    return {"gain_ft": gain_ft, "gain_per_mile_ft": gain_per_mile_ft}


def profile_from_dem_artifact(dem_path: Path) -> list[float]:
    """Derive a deterministic pseudo-profile from cached DEM bytes."""
    data = dem_path.read_bytes() if dem_path.exists() else b""
    if not data:
        return [100.0, 100.0, 100.0]
    sample = list(data[:4])
    if len(sample) < 4:
        sample = sample + [sample[-1]] * (4 - len(sample))
    base = 100.0
    return [base + float(v % 40) for v in sample]
