from dataclasses import dataclass


@dataclass(frozen=True)
class SearchState:
    origin: str
    current_node: str
    path_nodes: tuple[str, ...]
    used_edges: frozenset[tuple[str, str]]
    distance_miles: float
    elevation_gain_ft: float

    @classmethod
    def initial(cls, origin: str) -> "SearchState":
        return cls(
            origin=origin,
            current_node=origin,
            path_nodes=(origin,),
            used_edges=frozenset(),
            distance_miles=0.0,
            elevation_gain_ft=0.0,
        )

    def expand(
        self,
        next_node: str,
        edge_key: tuple[str, str],
        edge_distance_miles: float,
        edge_gain_ft: float,
    ) -> "SearchState":
        return SearchState(
            origin=self.origin,
            current_node=next_node,
            path_nodes=self.path_nodes + (next_node,),
            used_edges=self.used_edges | frozenset((edge_key,)),
            distance_miles=self.distance_miles + edge_distance_miles,
            elevation_gain_ft=self.elevation_gain_ft + edge_gain_ft,
        )
