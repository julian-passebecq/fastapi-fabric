# fastapi-fabric

Standalone FastAPI backend for **Fabric Factory Lab**, an independent Microsoft Fabric Data Factory learning/simulation app.

## Scope

- Own pipeline definitions, parameters, variables, dependencies and runs.
- Simulate Fabric/Data Factory orchestration without requiring Datapass or Microsoft Fabric.
- Keep adapter seams for optional Datapass Spark and future real Fabric execution.
- Expose a stable API for a separate React + Fluent UI Fabric Factory frontend.

## Run locally

```bash
uv sync
uv run fastapi dev main.py
```

Open `/docs` for the OpenAPI explorer.

## V0.1 API

- `GET /health`
- `GET /api/v1/capabilities`
- CRUD for `/api/v1/pipelines`
- `POST /api/v1/pipelines/{pipeline_id}/validate`
- `POST /api/v1/pipelines/{pipeline_id}/runs`
- `GET /api/v1/runs`
- `GET /api/v1/runs/{run_id}`
- `POST /api/v1/runs/{run_id}/cancel`
- `POST /api/v1/expressions/evaluate`

The first runtime is deterministic and simulated. The next milestones add persistent metadata, activity executors, local data execution, and optional external adapters.
