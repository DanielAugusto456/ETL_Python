from pathlib import Path
from typing import Union

_DB_HINTS = (
    "mssql", "sqlserver", "postgresql", "postgres", "mysql",
    "sqlite", "oracle", "odbc", "driver=", "server=", "trusted_connection",
)

def detect_source_type(source: Union[str, "Path"]) -> str:
    text = str(source).strip()
    lower = text.lower()

    if lower.startswith("http://") or lower.startswith("https://"):
        return "API"

    if any(hint in lower for hint in _DB_HINTS):
        return "Database"

    suffix = Path(text).suffix.lower().lstrip(".")

    if suffix == "csv":
        return "CSV"
    if suffix in ("json", "xml"):
        return "CSV"

    if suffix:
        return suffix.upper()

    return "Unknown"
