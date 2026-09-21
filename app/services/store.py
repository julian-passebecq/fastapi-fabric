from __future__ import annotations

from threading import RLock

from app.domain.models import PipelineDefinition, PipelineRun


class MemoryStore:
    def __init__(self) -> None:
        self._pipelines: dict[str, PipelineDefinition] = {}
        self._runs: dict[str, PipelineRun] = {}
        self._lock = RLock()

    def list_pipelines(self) -> list[PipelineDefinition]:
        with self._lock:
            return list(self._pipelines.values())

    def get_pipeline(self, pipeline_id: str) -> PipelineDefinition | None:
        with self._lock:
            return self._pipelines.get(pipeline_id)

    def put_pipeline(self, pipeline: PipelineDefinition) -> PipelineDefinition:
        with self._lock:
            self._pipelines[pipeline.id] = pipeline
            return pipeline

    def delete_pipeline(self, pipeline_id: str) -> bool:
        with self._lock:
            return self._pipelines.pop(pipeline_id, None) is not None

    def list_runs(self) -> list[PipelineRun]:
        with self._lock:
            return list(self._runs.values())

    def get_run(self, run_id: str) -> PipelineRun | None:
        with self._lock:
            return self._runs.get(run_id)

    def put_run(self, run: PipelineRun) -> PipelineRun:
        with self._lock:
            self._runs[run.id] = run
            return run


store = MemoryStore()
