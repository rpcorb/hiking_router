def build_bbox_query(bbox: tuple[float, float, float, float]) -> str:
    min_lon, min_lat, max_lon, max_lat = bbox
    return (
        f"[out:json];(way[\"highway\"~\"path|footway|track\"]"
        f"({min_lat},{min_lon},{max_lat},{max_lon}););out body;>;out skel qt;"
    )
