
import httpx
import pytest


LEGACY_URL = "http://127.0.0.1:8001"
MODERNIZED_URL = "http://127.0.0.1:8002"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=15.0) as http_client:
        yield http_client


def test_legacy_health(client):
    response = client.get(
        f"{LEGACY_URL}/health"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_modernized_health(client):
    response = client.get(
        f"{MODERNIZED_URL}/health"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_legacy_checkout(client):
    response = client.post(
        f"{LEGACY_URL}/checkout",
        json={
            "quantity": 2,
            "unit_price": "500.00",
        },
    )

    assert response.status_code == 200
    assert response.json()["final_total"] == "1062.00"


def test_modernized_checkout(client):
    response = client.post(
        f"{MODERNIZED_URL}/checkout",
        json={
            "quantity": 2,
            "unit_price": "500.00",
        },
    )

    assert response.status_code == 200
    assert response.json()["final_total"] == "1180.00"


def test_api_pipeline_detects_drift():
    from behavior_recorder.api_recorder import (
        record_api_behaviors,
    )
    from differential_analysis.analyzer import (
        analyze_observations,
    )
    from ldi_calculator.calculator import (
        calculate_ldi,
    )

    observations = record_api_behaviors()
    drift_report = analyze_observations(
        observations
    )
    ldi_report = calculate_ldi(
        drift_report
    )

    assert drift_report["drifted_case_ids"] == [
        "TC002"
    ]

    assert ldi_report["ldi_score"] == pytest.approx(
        0.5
    )
