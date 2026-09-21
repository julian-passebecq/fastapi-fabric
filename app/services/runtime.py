from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.domain.models import ActivityDefinition, ActivityRun, PipelineDefinition, PipelineRun, RunRequest, RunStatus
from app.services.store import store
from app.services.validator import validate_pipeline


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _simulate(activity: ActivityDefinition, run: PipelineRun) -> ActivityRun:
    started = utcnow()
    fail = bool(activity.settings.get("simulate_failure", False))
    output: dict[str, Any]
    error = None
    status = RunStatus.FAILED if fail else RunStatus.SUCCEEDED

    if fail:
        output = {}
        error = activity.settings.get("error_message", "Simulated activity failure")
    elif activity.type.value == "Copy":
        rows = int(activity.settings.get("rows", 1000))
        output = {"rowsRead": rows, "rowsWritten": rows, "throughputRowsPerSecond": max(1, rows // 2)}
    elif activity.type.value == "Lookup":
        output = {"firstRow": activity.settings.get("first_row", {"table": "customers"})}
    elif activity.type.value == "SetVariable":
        name = str(activity.settings.get("name", "value"))
        value = activity.settings.get("value")
        run.variables[name] = value
        output = {"name": name, "value": value}
    else:
        output = {"message": f"Simulated {activity.type.value} completed"}

    return ActivityRun(
        activity_name=activity.name,
        activity_type=activity.type,
        status=status,
        started_at=started,
        ended_at=utcnow(),
        input=activity.settings,
        output=output,
        error=error,
    )


def execute_pipeline(pipeline: PipelineDefinition, request: RunRequest) -> PipelineRun:
    validation = validate_pipeline(pipeline)
    if not validation.valid:
        raise ValueError("Pipeline is invalid and cannot run")
    if request.mode != "simulated":
        raise ValueError(f"Execution mode '{request.mode}' is reserved for a later milestone")

    resolved_parameters = {name: spec.default for name, spec in pipeline.parameters.items()}
    resolved_parameters.update(request.parameters)

    run = PipelineRun(
        pipeline_id=pipeline.id,
        pipeline_name=pipeline.name,
        status=RunStatus.RUNNING,
        parameters=resolved_parameters,
        variables=dict(pipeline.variables),
        started_at=utcnow(),
    )
    store.put_run(run)

    completed: dict[str, ActivityRun] = {}
    remaining = {a.name: a for a in pipeline.activities}

    while remaining:
        progressed = False
        for name, activity in list(remaining.items()):
            if not all(dep.activity in completed for dep in activity.depends_on):
                continue

            dependency_failed = any(
                dep.condition.value == "Succeeded" and completed[dep.activity].status != RunStatus.SUCCEEDED
                for dep in activity.depends_on
            )
            if dependency_failed:
                activity_run = ActivityRun(
                    activity_name=activity.name,
                    activity_type=activity.type,
                    status=RunStatus.SKIPPED,
                    started_at=utcnow(),
                    ended_at=utcnow(),
                    error="Skipped because dependency condition was not met",
                )
            else:
                activity_run = _simulate(activity, run)

            run.activities.append(activity_run)
            completed[name] = activity_run
            del remaining[name]
            progressed = True

        if not progressed:
            run.status = RunStatus.FAILED
            run.ended_at = utcnow()
            store.put_run(run)
            return run

    run.status = RunStatus.FAILED if any(a.status == RunStatus.FAILED for a in run.activities) else RunStatus.SUCCEEDED
    run.ended_at = utcnow()
    store.put_run(run)
    return run
