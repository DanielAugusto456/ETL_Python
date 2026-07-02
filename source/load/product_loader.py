from .sql_server_loader import SqlServerLoader
import pandas as pd

class ProductLoader(SqlServerLoader):
    table_name = "Products"
    column_map = {
        "name": "ProductName",
        "categoryID": "Category",
        "price": "Price",
        "stock": "Stock",
    }