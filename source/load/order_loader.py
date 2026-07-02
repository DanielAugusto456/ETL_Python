from .sql_server_loader import SqlServerLoader

class OrderLoader(SqlServerLoader):
    table_name = "Order"
    column_map = {
        "customer_id": "CustomerID",
        "order_date": "OrderDate",
        "statusID": "StatusID",
    }
