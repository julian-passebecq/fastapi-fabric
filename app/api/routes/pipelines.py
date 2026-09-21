from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Response, status

from app.domain.models import PipelineCreate, PipelineDefinition, PipelineUpdate, RunRequest
from app.services.runtime import execute_pipeline
from app.services.store import store
from app.services.validator import validate_pipeline

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("")
def list_pipelines() -> list[PipelineDefinition]:
    return store.list_pipelines()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_pipeline(payload: PipelineCreate) -> PipelineDefinition:
    pipeline = PipelineDefinition(**payload.model_dump())
    return store.put_pipeline(pipeline)


@router.get("/{pipeline_id}")
def get_pipeline(pipeline_id: str) -> PipelineDefinition:
    pipeline = store.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline


@router.put("/{pipeline_id}")
def update_pipeline(pipeline_id: str, payload: PipelineUpdate) -> PipelineDefinition:
    existing = store.get_pipeline(pipeline_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    pipeline = PipelineDefinition(
        id=existing.id,
        created_at=existing.created_at,
        updated_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )
    return store.put_pipeline(pipeline)


@router.delete("/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pipeline(pipeline_id: str) -> Response:
    if not store.delete_pipeline(pipeline_id):
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{pipeline_id}/validate")
def validate(pipeline_id: str):
    pipeline = store.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return validate_pipeline(pipeline)


@router.post("/{pipeline_id}/runs")
def run_pipeline(pipeline_id: str, request: RunRequest):
    pipeline = store.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    try:
        return execute_pipeline(pipeline, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
