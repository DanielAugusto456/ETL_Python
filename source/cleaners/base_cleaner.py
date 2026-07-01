import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseCleaner(ABC):

    def __init__(self):
        self.valid_records: List[Dict[str, Any]] = []
        self.invalid_records: List[Dict[str, Any]] = []

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
    
    def get_valid_records(self) -> List[Dict[str, Any]]:
        return self.valid_records
    
    def get_invalid_records(self) -> List[Dict[str, Any]]:
        return self.invalid_records
    
    def invalid_record_to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.invalid_records)