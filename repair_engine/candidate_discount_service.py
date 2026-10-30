
from decimal import Decimal

from config import (
    DISCOUNT_THRESHOLD,
    DISCOUNT_RATE,
)

from modernized_system.pricing_service import round_money


def calculate_discount(subtotal):
    """
    Calculate the checkout discount.

    WARNING:
    This version intentionally contains a
    boundary-condition business-logic defect.
    """

    # INTENTIONAL DRIFT:
    # Expected business rule: subtotal >= 1000
    # Implemented rule: subtotal > 1000

    if subtotal >= DISCOUNT_THRESHOLD:
        return round_money(
            subtotal * DISCOUNT_RATE
        )

    return Decimal("0.00")
