from pydantic import BaseModel, Field, field_validator
from validations import validation as va

class Status(BaseModel):
    name: str = Field(..., description="The name of the status", max_length=50)

    @field_validator("name")
    @classmethod
    def validate_string_fields(cls, value: str) -> str:
        return va.validate_string_fields(value)