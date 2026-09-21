from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_validate_and_run_pipeline() -> None:
    payload = {
        "name": "Contoso Bronze Load",
        "parameters": {"environment": {"type": "string", "default": "dev"}},
        "activities": [
            {"name": "LookupTables", "type": "Lookup", "settings": {"first_row": {"table": "customers"}}},
            {
                "name": "CopyCustomers",
                "type": "Copy",
                "depends_on": [{"activity": "LookupTables", "condition": "Succeeded"}],
                "settings": {"rows": 12504},
            },
        ],
    }
    created = client.post("/api/v1/pipelines", json=payload)
    assert created.status_code == 201
    pipeline_id = created.json()["id"]

    validation = client.post(f"/api/v1/pipelines/{pipeline_id}/validate")
    assert validation.status_code == 200
    assert validation.json()["valid"] is True

    run = client.post(f"/api/v1/pipelines/{pipeline_id}/runs", json={"parameters": {"environment": "test"}})
    assert run.status_code == 200
    body = run.json()
    assert body["status"] == "Succeeded"
    assert body["parameters"]["environment"] == "test"
    assert body["activities"][1]["output"]["rowsWritten"] == 12504


def test_validation_rejects_unknown_dependency() -> None:
    created = client.post(
        "/api/v1/pipelines",
        json={
            "name": "Broken",
            "activities": [
                {
                    "name": "Copy",
                    "type": "Copy",
                    "depends_on": [{"activity": "Missing", "condition": "Succeeded"}],
                }
            ],
        },
    )
    pipeline_id = created.json()["id"]
    result = client.post(f"/api/v1/pipelines/{pipeline_id}/validate").json()
    assert result["valid"] is False
    assert result["issues"][0]["code"] == "UNKNOWN_DEPENDENCY"


def test_expression_evaluation() -> None:
    response = client.post(
        "/api/v1/expressions/evaluate",
        json={"expression": "@pipeline().parameters.environment", "parameters": {"environment": "dev"}},
    )
    assert response.status_code == 200
    assert response.json()["value"] == "dev"
