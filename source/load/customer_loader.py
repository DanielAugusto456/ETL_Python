from .sql_server_loader import SqlServerLoader

class CustomerLoader(SqlServerLoader):
    table_name = "Customers"
    column_map = {
        "first_name": "FirstName",
        "last_name": "LastName",
        "email": "Email",
        "phone": "Phone",
        "city": "City",
        "countryID": "Country",
    }
