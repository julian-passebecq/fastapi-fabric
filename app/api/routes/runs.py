from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.domain.models import PipelineRun, RunStatus
from app.services.store import store

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("")
def list_runs() -> list[PipelineRun]:
    return store.list_runs()


@router.get("/{run_id}")
def get_run(run_id: str) -> PipelineRun:
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post("/{run_id}/cancel")
def cancel_run(run_id: str) -> PipelineRun:
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.status in {RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.CANCELLED}:
        raise HTTPException(status_code=409, detail=f"Run is already {run.status.value}")
    run.status = RunStatus.CANCELLED
    run.ended_at = datetime.now(timezone.utc)
    return store.put_run(run)
