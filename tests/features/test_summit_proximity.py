from hiking_router.features.summit_proximity import route_summit_proximity_min_m


def test_route_summit_proximity_returns_min_distance_to_summit_points():
    route_nodes = ["1", "2", "3"]
    edge_details = {
        frozenset(("1", "2")): {
            "length_m": 100.0,
            "from_coord": (37.0000, -80.0000),
            "to_coord": (37.0010, -80.0000),
        },
        frozenset(("2", "3")): {
            "length_m": 100.0,
            "from_coord": (37.0010, -80.0000),
            "to_coord": (37.0010, -80.0010),
        },
    }
    summits = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-80.0000, 37.0010]},
                "properties": {"name": "Test Summit"},
            }
        ],
    }

    distance_m = route_summit_proximity_min_m(
        route_nodes=route_nodes,
        edge_details=edge_details,
        summit_feature_collection=summits,
    )

    assert distance_m is not None
    assert distance_m == 0.0

