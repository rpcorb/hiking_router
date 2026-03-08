from pydantic import BaseModel, Field


class TrailEdge(BaseModel):
    edge_id: str
    from_node: str
    to_node: str
    length_m: float = Field(ge=0)
    elev_gain_m: float = 0
    elev_loss_m: float = 0
    avg_grade: float = 0
    max_grade: float = 0
    ridge_fraction: float = 0
    summit_proximity_min_m: float = 0
    scenic_score: float = 0
