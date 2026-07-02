from .sql_server_loader import SqlServerLoader

class OrderLoader(SqlServerLoader):
    table_name = "Orders"
    column_map = {
        "order_id": "OrderID",
        "customer_id": "CustomerID",
        "order_date": "OrderDate",
        "statusID": "Status",
    }

    def load(self, data):
        super().load(data, identity_insert=True)
