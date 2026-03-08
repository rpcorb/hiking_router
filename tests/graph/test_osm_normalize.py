from hiking_router.graph.osm_normalize import extract_segment_edges


def test_extract_segment_edges_from_overpass_elements():
    payload = {
        "elements": [
            {"type": "node", "id": 1, "lat": 37.0, "lon": -80.0},
            {"type": "node", "id": 2, "lat": 37.001, "lon": -80.001},
            {"type": "node", "id": 3, "lat": 37.002, "lon": -80.002},
            {"type": "way", "id": 10, "nodes": [1, 2, 3], "tags": {"highway": "path"}},
        ]
    }

    edges = extract_segment_edges(payload)

    assert len(edges) == 2
    assert edges[0]["from_node"] == "1"
    assert edges[0]["to_node"] == "2"
    assert edges[0]["length_m"] > 0
