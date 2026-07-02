import pandas as pd
from .base_cleaner import BaseCleaner
from models.country_model import Country
from config.database import get_creds

class CountryCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        # 1. Aislar y limpiar la columna de países del origen (p. ej. customers.csv)
        countries = data["Country"].astype(str).str.strip()
        countries = self.remove_duplicates(countries)
        countries = self.handle_nulls(countries, strategy='drop')
        countries = countries[countries != ""]

        # 2. Traer los países que ya existen en BD
        creds = get_creds()
        countries_in_db = pd.read_sql_query(
            "SELECT CountryName FROM Country", con=creds.engine
        )
        countries_db = set(countries_in_db['CountryName'])

        # 3. Quedarnos solo con los países nuevos (que no están en BD)
        new_countries = self.filter_existing_in_db(countries, countries_db)

        if new_countries.empty:
            print("No new countries to insert.")
            return pd.DataFrame()

        # 4. Validar cada país nuevo con el modelo Pydantic
        for name in new_countries:
            try:
                country = Country(name=name)
                self.valid_records.append(country.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": name, "error": str(e)})

        return pd.DataFrame(self.valid_records)
