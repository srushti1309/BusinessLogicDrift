
import json
from pathlib import Path

from behavior_recorder.api_recorder import (
    record_api_behaviors,
)

from differential_analysis.analyzer import (
    analyze_observations,
)

from ldi_calculator.calculator import (
    calculate_ldi,
)


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"


def save_report(filename, data):
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
    print("HTTP-BASED BUSINESS-LOGIC DRIFT ANALYSIS")
    print("=" * 65)

    print("\n[1/3] Recording HTTP behavior...")
    observations = record_api_behaviors()

    print("\n[2/3] Comparing business behavior...")
    drift_report = analyze_observations(
        observations
    )

    save_report(
        "api_drift_report.json",
        drift_report
    )

    print(
        f"Drifted cases: "
        f"{drift_report['drifted_case_ids']}"
    )

    print("\n[3/3] Calculating LDI...")
    ldi_report = calculate_ldi(
        drift_report
    )

    save_report(
        "api_ldi_report.json",
        ldi_report
    )

    print("\nFINAL HTTP-BASED RESULTS")
    print("-" * 65)

    print(
        f"Total cases: "
        f"{ldi_report['total_test_cases']}"
    )

    print(
        f"Drifted cases: "
        f"{ldi_report['drifted_test_cases']}"
    )

    print(
        f"LDI Score: "
        f"{ldi_report['ldi_score']:.4f} / 100"
    )

    print(
        f"Threshold exceeded: "
        f"{ldi_report['threshold_exceeded']}"
    )

    print("\nSaved reports:")
    print("  results/api_behavior_observations.json")
    print("  results/api_drift_report.json")
    print("  results/api_ldi_report.json")

    print("\nHTTP pipeline completed successfully.")


if __name__ == "__main__":
    main()
