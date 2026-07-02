import pandas as pd
from .base_cleaner import BaseCleaner
from models.country_model import Country
from config.database import get_creds

class CountryCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        countries = data["Country"].astype(str).str.strip()
        countries = self.remove_duplicates(countries)
        countries = self.handle_nulls(countries, strategy='drop')
        countries = countries[countries != ""]

        creds = get_creds()
        countries_in_db = pd.read_sql_query(
            "SELECT CountryName FROM Country", con=creds.engine
        )
        countries_db = set(countries_in_db['CountryName'])

        new_countries = self.filter_existing_in_db(countries, countries_db)

        if new_countries.empty:
            print("No new countries to insert.")
            return pd.DataFrame()

        for name in new_countries:
            try:
                country = Country(name=name)
                self.valid_records.append(country.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": name, "error": str(e)})

        return pd.DataFrame(self.valid_records)
