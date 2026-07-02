from .sql_server_loader import SqlServerLoader

class OrderDetailLoader(SqlServerLoader):
    table_name = "OrderDetail"
    column_map = {
        "order_id": "OrderID",
        "product_id": "ProductID",
        "quantity": "Quantity",
        "total_price": "TotalPrice",
    }
