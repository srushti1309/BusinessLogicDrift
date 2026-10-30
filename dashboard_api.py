
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from behavior_recorder.api_recorder import record_api_behaviors
from differential_analysis.analyzer import analyze_observations
from ldi_calculator.calculator import calculate_ldi

from repair_engine.localizer import localize_root_cause
from repair_engine.patch_generator import generate_candidate_patch
from repair_engine.evaluator import evaluate_candidate


app = FastAPI(
    title="DriftScope Analysis API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"


def read_report(filename):
    path = RESULTS_DIR / filename

    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_report(filename, data):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(
        RESULTS_DIR / filename,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "application": "DriftScope",
    }


@app.get("/api/dashboard")
def get_dashboard():
    return {
        "drift": read_report("api_drift_report.json"),
        "ldi": read_report("api_ldi_report.json"),
        "observations": read_report(
            "api_behavior_observations.json"
        ),
        "localization": read_report(
            "localization_report.json"
        ),
        "patch": read_report("patch_report.json"),
        "repair": read_report(
            "repair_evaluation.json"
        ),
    }


@app.post("/api/analyze")
def run_analysis():
    try:
        observations = record_api_behaviors()
        drift_report = analyze_observations(observations)
        ldi_report = calculate_ldi(drift_report)

        save_report(
            "api_drift_report.json",
            drift_report,
        )
        save_report(
            "api_ldi_report.json",
            ldi_report,
        )

        return {
            "success": True,
            "message": "Drift analysis completed",
            "drift": drift_report,
            "ldi": ldi_report,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@app.post("/api/localize")
def run_localization():
    try:
        report = localize_root_cause()

        return {
            "success": True,
            "message": "Root-cause localization completed",
            "localization": report,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@app.post("/api/repair")
def run_repair():
    try:
        patch = generate_candidate_patch()
        evaluation = evaluate_candidate()

        return {
            "success": True,
            "message": "Candidate repair evaluated",
            "patch": patch,
            "repair": evaluation,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
