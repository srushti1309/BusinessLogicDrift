
from pathlib import Path

import pytest

from repair_engine.localizer import localize_root_cause
from repair_engine.patch_generator import (
    generate_candidate_patch,
    SOURCE_PATH,
    CANDIDATE_PATH,
)
from repair_engine.evaluator import evaluate_candidate


def test_localizer_finds_known_defect():
    report = localize_root_cause()

    assert report["known_defect_found"] is True
    assert report["suspected_root_cause"] == (
        "discount_service"
    )


def test_patch_generator_preserves_original():
    before = SOURCE_PATH.read_bytes()

    report = generate_candidate_patch()

    after = SOURCE_PATH.read_bytes()

    assert before == after
    assert report["syntax_valid"] is True
    assert CANDIDATE_PATH.exists()

    candidate = CANDIDATE_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "subtotal >= DISCOUNT_THRESHOLD"
        in candidate
    )


def test_candidate_discount_boundary():
    from repair_engine.candidate_discount_service import (
        calculate_discount,
    )
    from decimal import Decimal

    result = calculate_discount(
        Decimal("1000.00")
    )

    assert result == Decimal("100.00")


def test_repair_evaluation():
    report = evaluate_candidate()

    assert report["baseline_ldi"] == pytest.approx(
        0.5
    )
    assert report["candidate_ldi"] == pytest.approx(
        0.0
    )
    assert report["critical_rule_passed"] is True
    assert report["repair_accepted"] is True
