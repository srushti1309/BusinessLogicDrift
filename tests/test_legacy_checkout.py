
import pytest

from legacy_system.checkout import process_checkout


@pytest.mark.parametrize(
    "quantity,unit_price,expected_total",
    [
        (2, "200.00", "472.00"),
        (2, "500.00", "1062.00"),
        (3, "500.00", "1593.00"),
        (1, "999.99", "1179.99"),
        (1, "0.00", "0.00"),
        (3, "333.335", "1062.01"),
    ],
)
def test_valid_checkout(
    quantity,
    unit_price,
    expected_total
):
    response = process_checkout({
        "quantity": quantity,
        "unit_price": unit_price,
    })

    assert response["status"] == "success"
    assert response["business_decision"] == "APPROVED"
    assert response["order_created"] is True
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
    assert response["error_type"] == "VALIDATION_ERROR"
    assert response["business_decision"] == "REJECTED"
    assert response["order_created"] is False
    assert response["final_total"] is None


def test_discount_boundary():
    response = process_checkout({
        "quantity": 2,
        "unit_price": "500.00",
    })

    assert response["subtotal"] == "1000.00"
    assert response["discount"] == "100.00"
    assert response["tax"] == "162.00"
    assert response["final_total"] == "1062.00"
