
from config import TAX_RATE

from modernized_system.pricing_service import round_money


def calculate_tax(taxable_amount):
    """
    Calculate tax after the discount.
    """
    return round_money(
        taxable_amount * TAX_RATE
    )
