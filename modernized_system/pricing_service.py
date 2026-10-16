
from decimal import Decimal

from config import (
    CURRENCY_QUANTUM,
    ROUNDING_MODE,
)


def round_money(value):
    """
    Round a monetary amount to two decimal places.
    """
    return value.quantize(
        CURRENCY_QUANTUM,
        rounding=ROUNDING_MODE
    )


def calculate_subtotal(quantity, unit_price):
    """
    Calculate the checkout subtotal.
    """
    subtotal = Decimal(quantity) * unit_price

    return round_money(subtotal)
