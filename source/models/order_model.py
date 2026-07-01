from pydantic import BaseModel, Field, field_validator

class Order(BaseModel):

    customer_id: int = Field(..., description="The ID of the customer")

    order_date: str = Field(..., description="The date of the order")

    status: str = Field(..., description="The status of the order", max_length=20)