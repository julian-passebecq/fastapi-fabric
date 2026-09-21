from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ActivityType(str, Enum):
    COPY = "Copy"
    LOOKUP = "Lookup"
    NOTEBOOK = "Notebook"
    SQL = "SqlScript"
    FOREACH = "ForEach"
    IF = "IfCondition"
    SWITCH = "Switch"
    WAIT = "Wait"
    SET_VARIABLE = "SetVariable"
    EXECUTE_PIPELINE = "ExecutePipeline"


class DependencyCondition(str, Enum):
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    COMPLETED = "Completed"
    SKIPPED = "Skipped"


class RunStatus(str, Enum):
    QUEUED = "Queued"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    SKIPPED = "Skipped"
    RETRYING = "Retrying"


class PipelineParameter(BaseModel):
    type: Literal["string", "integer", "float", "boolean", "array", "object"] = "string"
    default: Any = None


class ActivityDependency(BaseModel):
    activity: str
    condition: DependencyCondition = DependencyCondition.SUCCEEDED


class ActivityDefinition(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    type: ActivityType
    depends_on: list[ActivityDependency] = Field(default_factory=list)
    settings: dict[str, Any] = Field(default_factory=dict)
    retry: int = Field(default=0, ge=0, le=10)
    timeout_seconds: int = Field(default=3600, ge=1, le=86400)


class PipelineDefinition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    parameters: dict[str, PipelineParameter] = Field(default_factory=dict)
    variables: dict[str, Any] = Field(default_factory=dict)
    activities: list[ActivityDefinition] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    @model_validator(mode="after")
    def unique_activity_names(self) -> "PipelineDefinition":
        names = [activity.name for activity in self.activities]
        if len(names) != len(set(names)):
            raise ValueError("Activity names must be unique within a pipeline")
        return self


class PipelineCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    parameters: dict[str, PipelineParameter] = Field(default_factory=dict)
    variables: dict[str, Any] = Field(default_factory=dict)
    activities: list[ActivityDefinition] = Field(default_factory=list)


class PipelineUpdate(PipelineCreate):
    pass


class ValidationIssue(BaseModel):
    severity: Literal["error", "warning"]
    code: str
    message: str
    activity: str | None = None


class ValidationResult(BaseModel):
    valid: bool
    issues: list[ValidationIssue]


class ActivityRun(BaseModel):
    activity_name: str
    activity_type: ActivityType
    status: RunStatus
    started_at: datetime | None = None
    ended_at: datetime | None = None
    attempt: int = 1
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class PipelineRun(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    pipeline_id: str
    pipeline_name: str
    status: RunStatus = RunStatus.QUEUED
    parameters: dict[str, Any] = Field(default_factory=dict)
    variables: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    activities: list[ActivityRun] = Field(default_factory=list)


class RunRequest(BaseModel):
    parameters: dict[str, Any] = Field(default_factory=dict)
    mode: Literal["simulated", "local", "external"] = "simulated"
