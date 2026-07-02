from pydantic import BaseModel, Field, field_validator
from validations import validation as va

class SourceType(BaseModel):
    name: str = Field(..., description="The name of the data source type (e.g. API, CSV, Database)", max_length=50)

    @field_validator("name")
    @classmethod
    def validate_string_fields(cls, value: str) -> str:
        return va.validate_string_fields(value)
