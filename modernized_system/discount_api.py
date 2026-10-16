
from decimal import Decimal, InvalidOperation

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from modernized_system.discount_service import (
    calculate_discount,
)


app = FastAPI(
    title="Discount Microservice",
    version="1.0.0",
)


class DiscountRequest(BaseModel):
    subtotal: str


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "discount",
    }


@app.post("/calculate-discount")
def calculate(request: DiscountRequest):
    try:
        subtotal = Decimal(request.subtotal)

        if not subtotal.is_finite() or subtotal < 0:
            raise ValueError("Invalid subtotal")

    except (InvalidOperation, ValueError):
        raise HTTPException(
            status_code=422,
            detail="Invalid subtotal",
        )

    discount = calculate_discount(subtotal)

    return {
        "discount": str(discount)
    }
