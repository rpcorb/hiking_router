from pydantic import BaseModel, field_validator


class LoopQuery(BaseModel):
    near: str
    miles_min: float
    miles_max: float
    difficulty: str

    @field_validator("miles_max")
    @classmethod
    def validate_range(cls, v: float, info):
        miles_min = info.data.get("miles_min")
        if miles_min is not None and v < miles_min:
            raise ValueError("miles_max must be >= miles_min")
        return v
