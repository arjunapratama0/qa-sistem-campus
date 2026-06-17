from sqlalchemy.types import UserDefinedType


class Vector(UserDefinedType):
    cache_ok = True

    def __init__(self, dimensions: int):
        self.dimensions = dimensions

    def get_col_spec(self, **kwargs):
        return f"vector({self.dimensions})"


def vector_literal(values: list[float]) -> str:
    numeric_values = [float(value) for value in values]
    return "[" + ",".join(f"{value:.10f}" for value in numeric_values) + "]"

