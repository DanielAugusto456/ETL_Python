from .sql_server_loader import SqlServerLoader

class StatusLoader(SqlServerLoader):
    table_name = "Status"
    column_map = {"name": "StatusName"}
