import pytest
from hiking_router.graph.schema import TrailEdge


def test_edge_rejects_negative_length():
    with pytest.raises(ValueError):
        TrailEdge(edge_id="e1", from_node="a", to_node="b", length_m=-1)
