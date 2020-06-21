from abc import ABC, abstractmethod


class KeyValueDB(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_data(self, query):
        pass
