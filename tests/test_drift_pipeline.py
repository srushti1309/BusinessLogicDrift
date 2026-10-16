
import pytest

from behavior_recorder.recorder import (
    record_behaviors,
)

from differential_analysis.analyzer import (
    analyze_observations,
)

from ldi_calculator.calculator import (
    calculate_ldi,
    calculate_output_divergence,
)


def test_output_divergence_for_seeded_defect():
    legacy = {
        "status": "success",
        "final_total": "1062.00",
    }

    modernized = {
        "status": "success",
        "final_total": "1180.00",
    }

    score = calculate_output_divergence(
        legacy,
        modernized
    )

    assert score == pytest.approx(0.10)


def test_identical_outputs_have_zero_divergence():
    response = {
        "status": "success",
        "final_total": "500.00",
    }

    assert calculate_output_divergence(
        response,
        response.copy()
    ) == 0.0


def test_zero_totals_are_handled():
    legacy = {
        "status": "success",
        "final_total": "0.00",
    }

    modernized = {
        "status": "success",
        "final_total": "0.00",
    }

    assert calculate_output_divergence(
        legacy,
        modernized
    ) == 0.0


def test_full_drift_pipeline():
    observations = record_behaviors()

    assert len(observations) == 8

    drift_report = analyze_observations(
        observations
    )

    assert drift_report["total_test_cases"] == 8
    assert drift_report["drifted_test_cases"] == 1
    assert drift_report["drifted_case_ids"] == [
        "TC002"
    ]

    tc002 = next(
        comparison
        for comparison in drift_report["comparisons"]
        if comparison["test_id"] == "TC002"
    )

    changed_fields = {
        difference["field"]
        for difference in tc002["differences"]
    }

    assert changed_fields == {
        "discount",
        "tax",
        "final_total",
    }

    ldi_report = calculate_ldi(
        drift_report
    )

    assert ldi_report["ldi_score"] == pytest.approx(
        0.5
    )

    assert ldi_report["threshold_exceeded"] is False


def test_empty_suite_is_rejected():
    empty_report = {
        "comparisons": [],
        "drifted_test_cases": 0,
    }

    with pytest.raises(ValueError):
        calculate_ldi(empty_report)
