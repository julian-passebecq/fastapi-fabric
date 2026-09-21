from fastapi import APIRouter

from app.domain.models import ActivityType

router = APIRouter(tags=["capabilities"])


@router.get("/capabilities")
def capabilities() -> dict:
    return {
        "executionModes": ["simulated"],
        "plannedExecutionModes": ["local", "external"],
        "activityTypes": [activity.value for activity in ActivityType],
        "features": {
            "pipelineValidation": True,
            "parameters": True,
            "variables": True,
            "dependencyConditions": True,
            "expressionEvaluation": True,
            "runHistory": True,
        },
    }
