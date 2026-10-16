
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from config import (
    LDI_WEIGHTS,
    LDI_THRESHOLD,
)


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR / "results" / "drift_report.json"
)

OUTPUT_PATH = (
    BASE_DIR / "results" / "ldi_report.json"
)


def calculate_output_divergence(legacy, modernized):
    """
    Calculate output divergence using
    the final checkout total.

    Returns a score between 0 and 1.
    """

    legacy_status = legacy.get("status")
    modernized_status = modernized.get("status")

    # Different success/error outcomes are
    # treated as maximum output divergence.
    if legacy_status != modernized_status:
        return 1.0

    # If both requests failed, monetary output
    # divergence is not applicable.
    # Error differences are scored separately.
    if legacy_status != "success":
        return 0.0

    legacy_total = legacy.get("final_total")
    modernized_total = modernized.get("final_total")

    try:
        if legacy_total is None or modernized_total is None:
            return 1.0

        legacy_value = Decimal(str(legacy_total))
        modernized_value = Decimal(str(modernized_total))

        if (
            not legacy_value.is_finite()
            or not modernized_value.is_finite()
        ):
            return 1.0

        difference = abs(
            legacy_value - modernized_value
        )

        denominator = max(
            abs(legacy_value),
            abs(modernized_value),
            Decimal("0.01"),
        )

        divergence = difference / denominator

        return float(min(Decimal("1"), divergence))

    except (InvalidOperation, ValueError, TypeError):
        return 1.0


def calculate_binary_divergence(
    legacy,
    modernized,
    fields
):
    """
    Return 1 if any relevant field differs,
    otherwise return 0.
    """

    for field in fields:
        if legacy.get(field) != modernized.get(field):
            return 1.0

    return 0.0


def calculate_case_ldi(comparison):
    """
    Calculate weighted divergence for one
    test case.
    """

    legacy = comparison["legacy"]
    modernized = comparison["modernized"]

    output_score = calculate_output_divergence(
        legacy,
        modernized
    )

    state_score = calculate_binary_divergence(
        legacy,
        modernized,
        ["order_created"]
    )

    error_score = calculate_binary_divergence(
        legacy,
        modernized,
        [
            "status",
            "error_type",
            "error_message",
        ]
    )

    workflow_score = calculate_binary_divergence(
        legacy,
        modernized,
        ["business_decision"]
    )

    weighted_score = (
        LDI_WEIGHTS["output"] * output_score
        + LDI_WEIGHTS["state"] * state_score
        + LDI_WEIGHTS["error"] * error_score
        + LDI_WEIGHTS["workflow"] * workflow_score
    )

    return {
        "test_id": comparison["test_id"],
        "output_divergence": round(output_score, 6),
        "state_divergence": state_score,
        "error_divergence": error_score,
        "workflow_divergence": workflow_score,
        "weighted_divergence": round(
            weighted_score,
            6
        ),
    }


def calculate_ldi(drift_report):
    """
    Calculate aggregate LDI for the
    evaluated test suite.

    All test cases have equal weight
    in this first prototype.
    """

    comparisons = drift_report["comparisons"]

    if not comparisons:
        raise ValueError(
            "Cannot calculate LDI for an empty test suite."
        )

    case_results = [
        calculate_case_ldi(comparison)
        for comparison in comparisons
    ]

    total_divergence = sum(
        case["weighted_divergence"]
        for case in case_results
    )

    ldi = (
        total_divergence / len(case_results)
    ) * 100

    return {
        "total_test_cases": len(case_results),
        "drifted_test_cases": drift_report[
            "drifted_test_cases"
        ],
        "weights": LDI_WEIGHTS,
        "ldi_score": round(ldi, 4),
        "threshold": LDI_THRESHOLD,
        "threshold_exceeded": ldi > LDI_THRESHOLD,
        "case_results": case_results,
    }


def run_ldi_calculation():
    """
    Load differential analysis results,
    calculate LDI, and save the report.
    """

    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        drift_report = json.load(file)

    report = calculate_ldi(drift_report)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nLOGIC DRIFT INDEX REPORT")
    print("=" * 55)

    print(
        f"Total test cases: "
        f"{report['total_test_cases']}"
    )

    print(
        f"Cases with drift: "
        f"{report['drifted_test_cases']}"
    )

    print(
        f"LDI Score: "
        f"{report['ldi_score']:.4f} / 100"
    )

    print(
        f"Threshold: "
        f"{report['threshold']}"
    )

    print(
        f"Threshold exceeded: "
        f"{report['threshold_exceeded']}"
    )

    print("\nPer-case divergence:")

    for case in report["case_results"]:
        print(
            f"  {case['test_id']}: "
            f"{case['weighted_divergence']:.6f}"
        )

    print(f"\nReport saved to: {OUTPUT_PATH}")

    return report


if __name__ == "__main__":
    run_ldi_calculation()
