from __future__ import annotations

from typing import Any


class ExpressionError(ValueError):
    pass


def evaluate_expression(expression: str, *, parameters: dict[str, Any], variables: dict[str, Any], item: Any = None) -> Any:
    expression = expression.strip()
    if not expression.startswith("@"):
        return expression

    if expression.startswith("@pipeline().parameters."):
        key = expression.removeprefix("@pipeline().parameters.")
        if key not in parameters:
            raise ExpressionError(f"Unknown pipeline parameter: {key}")
        return parameters[key]

    if expression.startswith("@variables('") and expression.endswith("')"):
        key = expression[len("@variables('") : -2]
        if key not in variables:
            raise ExpressionError(f"Unknown variable: {key}")
        return variables[key]

    if expression == "@item()":
        return item

    raise ExpressionError("Unsupported expression in V1 simulator")
