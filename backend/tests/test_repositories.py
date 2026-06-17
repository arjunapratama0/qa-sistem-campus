from app.infrastructure.db.vector import vector_literal


def test_vector_literal_formats_numeric_values_only():
    literal = vector_literal([1, "2.5", -0.125])

    assert literal == "[1.0000000000,2.5000000000,-0.1250000000]"

