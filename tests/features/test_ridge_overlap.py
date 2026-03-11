from hiking_router.features.ridge_overlap import route_ridge_fraction


def test_route_ridge_fraction_computes_overlap_ratio():
    route_nodes = ["1", "2", "3"]
    edge_details = {
        frozenset(("1", "2")): {
            "length_m": 100.0,
            "from_coord": (37.0, -80.0),
            "to_coord": (37.001, -80.001),
        },
        frozenset(("2", "3")): {
            "length_m": 100.0,
            "from_coord": (37.001, -80.001),
            "to_coord": (37.002, -80.002),
        },
    }
    ridges = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-80.0, 37.0],
                        [-80.001, 37.001],
                    ],
                },
                "properties": {},
            }
        ],
    }

    frac = route_ridge_fraction(route_nodes=route_nodes, edge_details=edge_details, ridge_feature_collection=ridges)

    assert round(frac, 2) == 0.5
