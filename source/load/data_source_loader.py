from .sql_server_loader import SqlServerLoader

class DataSourceLoader(SqlServerLoader):
    table_name = "DataSource"
    column_map = {
        "source_name": "SourceName",
        "source_type": "SourceType",
        "connection_string": "ConnectionString",
        "file_format": "FileFormat",
        "extracted_at": "ExtractedAt",
        "loaded_at": "LoadedAt",
        "status": "Status",
        "records_extracted": "RecordsExtracted",
        "records_loaded": "RecordsLoaded",
        "records_failed": "RecordsFailed",
        "error_log": "ErrorLog",
        "created_by": "CreatedBy",
    }
