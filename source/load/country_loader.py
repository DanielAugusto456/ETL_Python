from .sql_server_loader import SqlServerLoader

class CountryLoader(SqlServerLoader):
    table_name = "Country"
    column_map = {"name": "CountryName"}
