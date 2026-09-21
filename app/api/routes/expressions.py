from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.expressions import ExpressionError, evaluate_expression

router = APIRouter(prefix="/expressions", tags=["expressions"])


class ExpressionRequest(BaseModel):
    expression: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    variables: dict[str, Any] = Field(default_factory=dict)
    item: Any = None


@router.post("/evaluate")
def evaluate(payload: ExpressionRequest) -> dict[str, Any]:
    try:
        value = evaluate_expression(
            payload.expression,
            parameters=payload.parameters,
            variables=payload.variables,
            item=payload.item,
        )
    except ExpressionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"expression": payload.expression, "value": value}
