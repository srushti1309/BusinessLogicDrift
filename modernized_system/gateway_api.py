
import os
from decimal import Decimal

import httpx

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Any

from config import CURRENCY

from modernized_system.validation_service import (
    validate_checkout_request,
)

from modernized_system.pricing_service import (
    calculate_subtotal,
    round_money,
)


DISCOUNT_SERVICE_URL = os.getenv(
    "DISCOUNT_SERVICE_URL",
    "http://127.0.0.1:8003",
)

TAX_SERVICE_URL = os.getenv(
    "TAX_SERVICE_URL",
    "http://127.0.0.1:8004",
)


app = FastAPI(
    title="Modernized Checkout Gateway",
    version="1.0.0",
)


class CheckoutRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    quantity: Any
    unit_price: Any


def validation_error(message):
    return {
        "status": "error",
        "error_type": "VALIDATION_ERROR",
        "error_message": message,
        "business_decision": "REJECTED",
        "order_created": False,
        "currency": CURRENCY,
        "subtotal": None,
        "discount": None,
        "tax": None,
        "final_total": None,
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "system": "modernized_gateway",
    }


@app.post("/checkout")
async def checkout(request: CheckoutRequest):

    request_data = request.model_dump()

    is_valid, validated_data, error_message = (
        validate_checkout_request(request_data)
    )

    if not is_valid:
        return validation_error(error_message)

    quantity = validated_data["quantity"]
    unit_price = validated_data["unit_price"]

    subtotal = calculate_subtotal(
        quantity,
        unit_price
    )

    try:
        async with httpx.AsyncClient(
            timeout=10.0
        ) as client:

            discount_response = await client.post(
                f"{DISCOUNT_SERVICE_URL}/calculate-discount",
                json={
                    "subtotal": str(subtotal)
                },
            )

            discount_response.raise_for_status()

            discount = Decimal(
                discount_response.json()["discount"]
            )

            taxable_amount = round_money(
                subtotal - discount
            )

            tax_response = await client.post(
                f"{TAX_SERVICE_URL}/calculate-tax",
                json={
                    "taxable_amount": str(taxable_amount)
                },
            )

            tax_response.raise_for_status()

            tax = Decimal(
                tax_response.json()["tax"]
            )

    except (
        httpx.HTTPError,
        KeyError,
        ValueError,
    ) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Downstream service failure: {type(exc).__name__}",
        ) from exc

    final_total = round_money(
        taxable_amount + tax
    )

    return {
        "status": "success",
        "error_type": None,
        "error_message": None,
        "business_decision": "APPROVED",
        "order_created": True,
        "currency": CURRENCY,
        "subtotal": str(subtotal),
        "discount": str(discount),
        "tax": str(tax),
        "final_total": str(final_total),
    }
