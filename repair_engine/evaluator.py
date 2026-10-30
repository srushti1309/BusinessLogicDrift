
import json
from pathlib import Path

import httpx

from behavior_recorder.normalizer import normalize_response
from differential_analysis.analyzer import analyze_observations
from ldi_calculator.calculator import calculate_ldi


BASE_DIR = Path(__file__).resolve().parent.parent

TEST_CASES_PATH = (
    BASE_DIR / "test_cases" / "checkout_cases.json"
)

BASELINE_REPORT_PATH = (
    BASE_DIR / "results" / "api_ldi_report.json"
)

OUTPUT_PATH = (
    BASE_DIR / "results" / "repair_evaluation.json"
)

LEGACY_URL = "http://127.0.0.1:8001"
CANDIDATE_URL = "http://127.0.0.1:8006"


def evaluate_candidate():

    with open(
        TEST_CASES_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        test_cases = json.load(file)

    with open(
        BASELINE_REPORT_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        baseline = json.load(file)

    observations = []

    with httpx.Client(timeout=15.0) as client:

        for test_case in test_cases:

            request = {
                "quantity": test_case["quantity"],
                "unit_price": test_case["unit_price"],
            }

            legacy_response = client.post(
                f"{LEGACY_URL}/checkout",
                json=request
            )

            candidate_response = client.post(
                f"{CANDIDATE_URL}/checkout",
                json=request
            )

            legacy_response.raise_for_status()
            candidate_response.raise_for_status()

            observations.append({
                "test_id": test_case["test_id"],
                "description": test_case["description"],
                "request": request,
                "legacy": normalize_response(
                    legacy_response.json()
                ),
                "modernized": normalize_response(
                    candidate_response.json()
                ),
            })

    drift_report = analyze_observations(observations)
    candidate_ldi = calculate_ldi(drift_report)

    boundary_case = next(
        observation
        for observation in observations
        if observation["test_id"] == "TC002"
    )

    boundary_response = boundary_case["modernized"]

    critical_rule_passed = (
        boundary_response["status"] == "success"
        and boundary_response["subtotal"] == "1000.00"
        and boundary_response["discount"] == "100.00"
        and boundary_response["final_total"] == "1062.00"
    )

    baseline_score = baseline["ldi_score"]
    repaired_score = candidate_ldi["ldi_score"]

    # The original seeded defect must be present
    # for this before/after experiment to be valid.
    baseline_valid = (
        baseline["drifted_test_cases"] == 1
        and abs(baseline_score - 0.5) < 1e-6
    )

    no_observed_regressions = (
        drift_report["drifted_test_cases"] == 0
    )

    repair_accepted = (
        baseline_valid
        and critical_rule_passed
        and no_observed_regressions
        and repaired_score < baseline_score
    )

    report = {
        "baseline_ldi": baseline_score,
        "candidate_ldi": repaired_score,
        "ldi_reduction": round(
            baseline_score - repaired_score,
            4
        ),
        "baseline_valid": baseline_valid,
        "critical_rule_passed": critical_rule_passed,
        "no_observed_regressions": no_observed_regressions,
        "candidate_drifted_cases": drift_report[
            "drifted_case_ids"
        ],
        "repair_accepted": repair_accepted,
        "evaluation_scope": (
            "Eight controlled checkout cases using "
            "HTTP API observations"
        ),
        "candidate_ldi_report": candidate_ldi,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    print("\nAUTOMATED REPAIR EVALUATION")
    print("=" * 55)

    print(f"Baseline LDI: {baseline_score:.4f}")
    print(f"Candidate LDI: {repaired_score:.4f}")
    print(
        f"LDI reduction: "
        f"{report['ldi_reduction']:.4f}"
    )
    print(f"Baseline valid: {baseline_valid}")
    print(
        f"Critical rule passed: "
        f"{critical_rule_passed}"
    )
    print(
        f"No observed regressions: "
        f"{no_observed_regressions}"
    )
    print(
        f"Repair accepted: "
        f"{repair_accepted}"
    )

    return report


if __name__ == "__main__":
    evaluate_candidate()
