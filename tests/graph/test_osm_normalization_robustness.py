from hiking_router.graph.osm_normalize import extract_segment_edges


def test_extract_segment_edges_ignores_invalid_node_records():
    payload = {
        "elements": [
            {"type": "node", "id": "bad", "lat": 37.0, "lon": -80.0},
            {"type": "node", "id": 2, "lat": 37.001, "lon": -80.001},
            {"type": "node", "id": 3, "lat": 37.002, "lon": -80.002},
            {"type": "way", "id": 10, "nodes": [2, 3], "tags": {"highway": "path"}},
        ]
    }
    edges = extract_segment_edges(payload)
    assert len(edges) == 1


def test_extract_segment_edges_handles_invalid_way_node_refs_gracefully():
    payload = {
        "elements": [
            {"type": "node", "id": 1, "lat": 37.0, "lon": -80.0},
            {"type": "node", "id": 2, "lat": 37.001, "lon": -80.001},
            {"type": "way", "id": 10, "nodes": [1, "oops", 2], "tags": {"highway": "path"}},
        ]
    }
    edges = extract_segment_edges(payload)
    assert isinstance(edges, list)
    assert len(edges) == 0


def test_extract_segment_edges_handles_non_list_elements():
    edges = extract_segment_edges({"elements": "invalid"})
    assert edges == []

