from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Generator
import pandas as pd
import yaml


class Storage(ABC):

    def __init__(self, base_path: str):
        self._base_path = base_path

    @property
    def base_path(self) -> str:
        return self._base_path

    @base_path.setter
    def base_path(self, new_path):
        self._base_path = new_path

    def _get_folder_path(self, folder: Union[None, str] = None) -> str:
        full_path = self.base_path
        if folder is not None:
            full_path = f'{full_path}/{folder}' if full_path != '' else folder

        return full_path

    def _get_full_path(self, filename: str, folder: Union[None, str] = None):
        if folder is None or folder.endswith('/'):
            return self._get_folder_path(folder=folder) + filename
        else:
            return self._get_folder_path(folder=folder) + '/' + filename

    def _create_local_path(self, object_filename: str, filename: Union[str, None] = None,
                           folder: Union[str, None] = None):
        object_filename_full = self._get_full_path(object_filename, folder)
        if filename is None:
            filename = object_filename_full
        local_path = Path(filename)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        filename = "".join(i for i in filename if i not in "\:*?<>|")
        return object_filename_full, filename

    ################
    # OBJECT ADMIN #
    ################

    @abstractmethod
    def list_objects(self, folder: Union[None, str] = None, filter_filename: Union[None, str] = None,
                     filter_extension: Union[None, str, tuple] = None) -> Generator:
        pass

    @abstractmethod
    def move_object(self, dest_storage_name: str, files_to_move: Union[str, list, Generator],
                    dest_object_name: Union[str, None] = None, remove_copied: bool = False):
        pass

    ###########
    # READERS #
    ###########

    @abstractmethod
    def read_csv(self, filename: str, folder: Union[str, None] = None, **kwargs):
        pass

    @abstractmethod
    def read_excel(self, filename: str, folder: Union[str, None] = None, **kwargs):
        pass

    @abstractmethod
    def read_parquet(self, filename: str, folder: Union[str, None] = None, **kwargs):
        pass

    @abstractmethod
    def read_yaml(self, filename: str, folder: Union[str, None] = None, yaml_loader=yaml.FullLoader):
        pass

    @abstractmethod
    def read_json(self, filename: str, folder: Union[str, None] = None, **kwargs):
        pass

    @abstractmethod
    def read_object(self, filename: str, folder: Union[str, None] = None, **kwargs):
        pass

    @abstractmethod
    def read_object_to_file(self, object_filename: str, filename: Union[str, None] = None,
                            folder: Union[str, None] = None, **kwargs):
        pass

    ###########
    # WRITERS #
    ###########

    @abstractmethod
    def write_csv(self, df: pd.DataFrame, filename: str, folder: Union[str, None] = None, **kwargs):
        pass

    @abstractmethod
    def write_excel(self, df: pd.DataFrame, filename: str, folder: Union[str, None] = None, **kwargs):
        pass

    @abstractmethod
    def write_parquet(self, df: pd.DataFrame, filename: str, folder: Union[str, None] = None, **kwargs):
        pass

    @abstractmethod
    def write_yaml(self, data: dict, filename: str, folder: Union[str, None] = None, **kwargs):
        pass

    @abstractmethod
    def write_json(self, data: dict, filename: str, folder: Union[str, None] = None, **kwargs):
        pass

    @abstractmethod
    def write_object(self, write_object, filename: str, folder: Union[str, None] = None, **kwargs):
        pass

    @abstractmethod
    def write_object_from_file(self, object_filename: str, filename: str, folder: Union[str, None] = None, **kwargs):
        pass
