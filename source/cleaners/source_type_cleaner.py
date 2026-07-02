import pandas as pd
from .base_cleaner import BaseCleaner
from models.source_type_model import SourceType
from config.database import get_creds

DEFAULT_SOURCE_TYPES = ["API", "CSV", "Database"]

class SourceTypeCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame = None) -> pd.DataFrame:
        source_types = pd.Series(DEFAULT_SOURCE_TYPES)

        creds = get_creds()
        types_in_db = pd.read_sql_query(
            "SELECT SourceTypeName FROM SourceType", con=creds.engine
        )
        types_db = set(types_in_db['SourceTypeName'])

        new_types = self.filter_existing_in_db(source_types, types_db)

        if new_types.empty:
            print("No new source types to insert.")
            return pd.DataFrame()

        for name in new_types:
            try:
                source_type = SourceType(name=name)
                self.valid_records.append(source_type.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": name, "error": str(e)})

        return pd.DataFrame(self.valid_records)
