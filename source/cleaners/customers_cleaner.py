import pandas as pd
from .base_cleaner import BaseCleaner
from models.customer_model import Customer
from normalizer import normalizer
from config.database import get_creds

COLUMN_MAP = {
    "FirstName": "first_name",
    "LastName": "last_name",
    "Email": "email",
    "Phone": "phone",
    "City": "city",
}

class CustomersCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.remove_duplicates(data)
        data = self.handle_nulls(data, strategy='drop')

        data['Email'] = data['Email'].astype(str).str.strip().str.lower()
        creds = get_creds()
        customers_in_db = pd.read_sql_query("SELECT Email FROM Customers", con=creds.engine)
        emails_db = set(customers_in_db['Email'].str.lower())
        data = self.filter_existing_in_db(data, emails_db, column='Email')

        if data.empty:
            print("No new customers to insert.")
            return pd.DataFrame()

        countries_in_db = pd.read_sql_query(
            "SELECT CountryID, CountryName FROM Country", con=creds.engine
        )
        country_map = dict(zip(
            countries_in_db['CountryName'],
            countries_in_db['CountryID']
        ))
        data['countryID'] = data['Country'].map(country_map)

        if data['countryID'].isna().any():
            missing_countries = data[data['countryID'].isna()]['Country'].unique()
            print(f"Países no encontrados en BD: {missing_countries}")
            data = data.dropna(subset=['countryID'])

        if data.empty:
            print("No new customers to insert.")
            return pd.DataFrame()

        data['countryID'] = data['countryID'].astype(int)

        data = data.drop(columns=['CustomerID', 'Country'], errors='ignore')
        data = data.rename(columns=COLUMN_MAP)

        for _, row in data.iterrows():
            try:
                row['Phone'] = normalizer.phone_normalizer(row['phone'])
                row['Email'] = normalizer.email_normalizer(row['email'])
                row['First_name'] = normalizer.name_normalizer(row['first_name'])
                row['Last_name'] = normalizer.name_normalizer(row['last_name'])
                customer = Customer(**row.to_dict())
                self.valid_records.append(customer.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": row.to_dict(), "error": str(e)})

        return pd.DataFrame(self.valid_records)