from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

class DataSource(BaseModel):
    source_name: str = Field(..., description="Nombre identificador de la fuente (ej. 'products.csv')", max_length=50)
    source_type: int = Field(..., description="FK -> SourceType.SourceTypeID")
    connection_string: Optional[str] = Field(None, description="Connection string, si la fuente es una BD")
    file_format: str = Field(..., description="Formato de la fuente (ej. 'csv', 'sql', 'json')", max_length=50)
    extracted_at: date = Field(..., description="Fecha en que inició la extracción")
    loaded_at: date = Field(..., description="Fecha en que terminó la carga")
    status: int = Field(..., description="FK -> Status.StatusID (ej. 'Success', 'Failed')")
    records_extracted: int = Field(0, ge=0)
    records_loaded: int = Field(0, ge=0)
    records_failed: int = Field(0, ge=0)
    error_log: str = Field("N/A", description="Detalle del error, 'N/A' si el proceso fue exitoso")
    created_by: str = Field("ETL_Pipeline", description="Proceso o usuario que generó el registro", max_length=50)
