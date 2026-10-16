
import pytest

from modernized_system.checkout_orchestrator import (
    process_checkout,
)


@pytest.mark.parametrize(
    "quantity,unit_price,expected_total",
    [
        (2, "200.00", "472.00"),
        (3, "500.00", "1593.00"),
        (1, "999.99", "1179.99"),
        (1, "0.00", "0.00"),
        (3, "333.335", "1062.01"),
    ],
)
def test_unaffected_checkout_cases(
    quantity,
    unit_price,
    expected_total
):
    response = process_checkout({
        "quantity": quantity,
        "unit_price": unit_price,
    })

    assert response["status"] == "success"
    assert response["final_total"] == expected_total


@pytest.mark.parametrize(
    "quantity,unit_price",
    [
        (0, "500.00"),
        (2, "-100.00"),
        (-1, "500.00"),
        (1.5, "500.00"),
        (True, "500.00"),
        (1, "NaN"),
        (1, "Infinity"),
    ],
)
def test_invalid_checkout(quantity, unit_price):
    response = process_checkout({
        "quantity": quantity,
        "unit_price": unit_price,
    })

    assert response["status"] == "error"
    assert response["business_decision"] == "REJECTED"
    assert response["order_created"] is False


def test_seeded_discount_boundary_drift():
    """
    Confirm that our intentional defect exists.

    This is an experiment fixture test, not a
    business-rule correctness test.
    """
    response = process_checkout({
        "quantity": 2,
        "unit_price": "500.00",
    })

    assert response["subtotal"] == "1000.00"
    assert response["discount"] == "0.00"
    assert response["tax"] == "180.00"
    assert response["final_total"] == "1180.00"
