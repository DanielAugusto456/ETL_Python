from .sql_server_loader import SqlServerLoader

class CategoryLoader(SqlServerLoader):
    table_name = "Category"
    column_map = {"name": "CategoryName"}
