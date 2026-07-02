from datetime import date, datetime
from typing import Optional, Union

import pandas as pd

from config.database import get_creds
from models.data_source_model import DataSource
from load.data_source_loader import DataSourceLoader
from utils.source_detector import detect_source_type

_FILE_FORMAT_BY_SOURCE_TYPE = {
    "CSV": "csv",
    "Database": "sql",
    "API": "json",
}

def _to_date(value: Union[datetime, date]) -> date:
    if isinstance(value, datetime):
        return value.date()
    return value

class ProcessLogger:

    def __init__(self):
        self.loader = DataSourceLoader()

    def _resolve_id(self, table: str, id_col: str, name_col: str, name: str) -> int:
        creds = get_creds()
        query = f"SELECT {id_col} FROM {table} WHERE {name_col} = '{name}'"
        result = pd.read_sql_query(query, con=creds.engine)
        if result.empty:
            raise ValueError(
                f"'{name}' no existe en la tabla {table}. "
                f"Debe insertarse antes de poder registrar el log."
            )
        return int(result.iloc[0][id_col])

    def log(
        self,
        source_name: str,
        source_descriptor: str,
        extracted_at: Union[datetime, date],
        loaded_at: Union[datetime, date],
        records_extracted: int = 0,
        records_loaded: int = 0,
        records_failed: int = 0,
        status_name: str = "Success",
        connection_string: Optional[str] = None,
        error_log: str = "N/A",
        created_by: str = "ETL_Pipeline",
    ) -> None:
        source_type_name = detect_source_type(source_descriptor)

        source_type_id = self._resolve_id(
            "SourceType", "SourceTypeID", "SourceTypeName", source_type_name
        )
        status_id = self._resolve_id("Status", "StatusID", "StatusName", status_name)

        file_format = _FILE_FORMAT_BY_SOURCE_TYPE.get(source_type_name, "unknown")

        record = DataSource(
            source_name=source_name,
            source_type=source_type_id,
            connection_string=connection_string,
            file_format=file_format,
            extracted_at=_to_date(extracted_at),
            loaded_at=_to_date(loaded_at),
            status=status_id,
            records_extracted=records_extracted,
            records_loaded=records_loaded,
            records_failed=records_failed,
            error_log=error_log or "N/A",
            created_by=created_by,
        )

        self.loader.load(pd.DataFrame([record.model_dump()]))
