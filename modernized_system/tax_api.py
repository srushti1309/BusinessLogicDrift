
from decimal import Decimal, InvalidOperation

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from modernized_system.tax_service import (
    calculate_tax,
)


app = FastAPI(
    title="Tax Microservice",
    version="1.0.0",
)


class TaxRequest(BaseModel):
    taxable_amount: str


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "tax",
    }


@app.post("/calculate-tax")
def calculate(request: TaxRequest):
    try:
        taxable_amount = Decimal(
            request.taxable_amount
        )

        if (
            not taxable_amount.is_finite()
            or taxable_amount < 0
        ):
            raise ValueError("Invalid taxable amount")

    except (InvalidOperation, ValueError):
        raise HTTPException(
            status_code=422,
            detail="Invalid taxable amount",
        )

    tax = calculate_tax(taxable_amount)

    return {
        "tax": str(tax)
    }
