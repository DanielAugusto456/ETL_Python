from pydantic import BaseModel, Field, field_validator
from validations import validation as va

class Order(BaseModel):

    customer_id: int = Field(..., description="The ID of the customer")

    order_date: str = Field(..., description="The date of the order")

    status: str = Field(..., description="The status of the order", max_length=20)

    @field_validator("status")
    @classmethod
    def validate_string_fields(cls, value: str) -> str:
        return va.validate_string_fields(value)