from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.capabilities import router as capabilities_router
from app.api.routes.expressions import router as expressions_router
from app.api.routes.pipelines import router as pipelines_router
from app.api.routes.runs import router as runs_router

app = FastAPI(
    title="Fabric Factory Lab API",
    version="0.1.0",
    description="Standalone orchestration backend for a Fabric/Data Factory learning clone.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "fastapi-fabric"}


app.include_router(capabilities_router, prefix="/api/v1")
app.include_router(pipelines_router, prefix="/api/v1")
app.include_router(runs_router, prefix="/api/v1")
app.include_router(expressions_router, prefix="/api/v1")
