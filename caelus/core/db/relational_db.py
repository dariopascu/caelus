from abc import ABC, abstractmethod
import pandas as pd

from core.storages import Storage


class RelationalDB(ABC):

    def __init__(self, connection):
        self.connection = connection

    @abstractmethod
    def make_query(self, query: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def query_to_storage(self, query: str, storage: Storage, filename: str):
        pass
