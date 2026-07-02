import logging
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union

class BaseCleaner(ABC):

    def __init__(self):
        self.valid_records: List[Dict[str, Any]] = []
        self.invalid_records: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    def remove_duplicates(self, data: pd.DataFrame) -> pd.DataFrame:
        data.drop_duplicates(inplace=True)
        return data

    def handle_nulls(self, data: pd.DataFrame, strategy: str = 'drop') -> pd.DataFrame:
        if strategy == 'drop':
            data = data.dropna()
        elif strategy == 'fill_zero':
            data = data.fillna(0)
        elif strategy == 'fill_empty':
            data = data.fillna("")
        else:
            self.logger.warning(f"Estrategia '{strategy}' no reconocida")
        return data
    
    def filter_existing_in_db(
        self,
        data: Union[pd.DataFrame, pd.Series],
        existing_values: set,
        column: str = None,
    ) -> Union[pd.DataFrame, pd.Series]:
        """
        Descarta los registros que ya existen en la base de datos.

        - Si `data` es una Series (p. ej. nombres de categoría/estado), compara
          directamente cada valor contra `existing_values`.
        - Si `data` es un DataFrame, se debe indicar `column` con el nombre de
          la columna a comparar contra `existing_values`.

        Registra cuántos registros fueron descartados por ya existir en BD.
        """
        before = len(data)

        if isinstance(data, pd.DataFrame):
            if column is None:
                raise ValueError("Debes indicar 'column' cuando 'data' es un DataFrame")
            filtered = data[~data[column].isin(existing_values)]
        else:
            filtered = data[~data.isin(existing_values)]

        removed = before - len(filtered)
        if removed:
            self.logger.info(
                f"{removed} registro(s) descartado(s) por ya existir en la base de datos."
            )
        return filtered

    def get_valid_records(self) -> List[Dict[str, Any]]:
        return self.valid_records
    
    def get_invalid_records(self) -> List[Dict[str, Any]]:
        return self.invalid_records
    
    def invalid_record_to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.invalid_records)