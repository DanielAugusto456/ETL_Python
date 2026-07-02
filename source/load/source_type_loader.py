from .sql_server_loader import SqlServerLoader

class SourceTypeLoader(SqlServerLoader):
    table_name = "SourceType"
    column_map = {"name": "SourceTypeName"}
