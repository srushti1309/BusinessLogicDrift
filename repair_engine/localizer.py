
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DRIFT_REPORT_PATH = (
    BASE_DIR / "results" / "api_drift_report.json"
)

DISCOUNT_SOURCE_PATH = (
    BASE_DIR / "modernized_system" / "discount_service.py"
)

LOCALIZATION_PATH = (
    BASE_DIR / "results" / "localization_report.json"
)


FIELD_TO_SERVICE = {
    "subtotal": "pricing_service",
    "discount": "discount_service",
    "tax": "tax_service",
    "final_total": "checkout_gateway",
    "order_created": "checkout_gateway",
    "business_decision": "checkout_gateway",
}


def localize_root_cause():

    with open(
        DRIFT_REPORT_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        drift_report = json.load(file)

    findings = []

    for comparison in drift_report["comparisons"]:

        if not comparison["has_drift"]:
            continue

        for difference in comparison["differences"]:

            field = difference["field"]

            findings.append({
                "test_id": comparison["test_id"],
                "field": field,
                "suspected_service": FIELD_TO_SERVICE.get(
                    field,
                    "unknown"
                ),
                "legacy_value": difference["legacy_value"],
                "modernized_value": difference["modernized_value"],
            })

    source_code = DISCOUNT_SOURCE_PATH.read_text(
        encoding="utf-8"
    )

    faulty_expression = (
        "subtotal > DISCOUNT_THRESHOLD"
    )

    known_defect_found = (
        faulty_expression in source_code
    )

    report = {
        "localization_method": (
            "field-to-service mapping and known-pattern "
            "source inspection"
        ),
        "findings": findings,
        "suspected_root_cause": (
            "discount_service"
            if known_defect_found
            else None
        ),
        "known_defect_found": known_defect_found,
        "faulty_expression": (
            faulty_expression
            if known_defect_found
            else None
        ),
        "proposed_expression": (
            "subtotal >= DISCOUNT_THRESHOLD"
            if known_defect_found
            else None
        ),
    }

    LOCALIZATION_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    LOCALIZATION_PATH.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    print("\nROOT-CAUSE LOCALIZATION")
    print("=" * 55)

    for finding in findings:
        print(
            f"{finding['test_id']} | "
            f"{finding['field']} | "
            f"{finding['suspected_service']}"
        )

    print(
        "\nKnown defect pattern found:",
        known_defect_found
    )

    print(
        "Suspected root cause:",
        report["suspected_root_cause"]
    )

    return report


if __name__ == "__main__":
    localize_root_cause()
