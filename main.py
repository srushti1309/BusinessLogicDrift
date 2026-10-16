
from behavior_recorder.recorder import (
    record_behaviors,
)

from differential_analysis.analyzer import (
    analyze_observations,
)

from ldi_calculator.calculator import (
    calculate_ldi,
)

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"


def save_json(filename, data):
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RESULTS_DIR / filename,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def main():

    print("\n" + "=" * 65)
    print("BUSINESS-LOGIC DRIFT DETECTION SYSTEM")
    print("=" * 65)

    print("\n[1/3] Recording business behavior...")
    observations = record_behaviors()

    print("\n[2/3] Running differential analysis...")
    drift_report = analyze_observations(
        observations
    )

    save_json(
        "drift_report.json",
        drift_report
    )

    print(
        f"Detected drift in "
        f"{drift_report['drifted_test_cases']} "
        f"of {drift_report['total_test_cases']} cases."
    )

    print(
        f"Drifted IDs: "
        f"{drift_report['drifted_case_ids']}"
    )

    print("\n[3/3] Calculating Logic Drift Index...")
    ldi_report = calculate_ldi(
        drift_report
    )

    save_json(
        "ldi_report.json",
        ldi_report
    )

    print("\n" + "=" * 65)
    print("FINAL RESULTS")
    print("=" * 65)

    print(
        f"Total test cases: "
        f"{ldi_report['total_test_cases']}"
    )

    print(
        f"Drifted test cases: "
        f"{ldi_report['drifted_test_cases']}"
    )

    print(
        f"LDI: "
        f"{ldi_report['ldi_score']:.4f} / 100"
    )

    print(
        f"Threshold exceeded: "
        f"{ldi_report['threshold_exceeded']}"
    )

    print("\nReports generated:")
    print("  results/behavior_observations.json")
    print("  results/drift_report.json")
    print("  results/ldi_report.json")

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()
