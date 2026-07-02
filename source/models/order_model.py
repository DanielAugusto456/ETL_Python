from pydantic import BaseModel, Field, field_validator
from validations import validation as va

class Order(BaseModel):

    customer_id: int = Field(..., description="The ID of the customer")

    order_date: str = Field(..., description="The date of the order")

    statusID: int = Field(..., description="The ID of the order status")

    @field_validator("order_date")
    @classmethod
    def validate_string_fields(cls, value: str) -> str:
        return va.validate_string_fields(value)