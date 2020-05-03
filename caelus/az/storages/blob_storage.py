import io
import json
import logging
from contextlib import contextmanager
from typing import Union, Generator

import pandas as pd
import yaml

from caelus.az.auth import AzureAuth
from caelus.core.storages import Storage
from azure.storage.blob import BlockBlobService
from azure.storage.common import TokenCredential
from azure.storage.blob.models import Blob


class BlobStorage(Storage):
    _az_logger = logging.getLogger('az')

    def __init__(self, auth: AzureAuth, account_name: str, container_name: str,
                 base_path: str = ""):
        Storage.__init__(self, base_path=base_path)

        self.container_name = container_name
        self.blob_service = BlockBlobService(account_name=account_name, account_key=auth.key_token,
                                             token_credential=TokenCredential(auth.service_principal_token),
                                             connection_string=auth.connection_string_token)

    ################
    # OBJECT ADMIN #
    ################
    def _list_blob_objects(self, prefix: str, filter_filename: Union[None, str] = None,
                           filter_extension: Union[None, str, tuple] = None) -> Generator:
        objects_generator = self.blob_service.list_blobs(self.container_name, prefix=prefix)

        for key in objects_generator:
            filtered_key = self._filter_key(key, filter_filename, filter_extension)
            if filtered_key is not None:
                yield filtered_key

    @staticmethod
    def _filter_key(key, filter_filename, filter_extension):
        key_name = key.name
        if (filter_filename is not None and filter_filename not in key_name) or (
                filter_extension is not None and not key_name.endswith(filter_extension)):
            return None
        else:
            return key

    def list_files(self, folder: Union[None, str] = None, filter_filename: Union[None, str] = None,
                   filter_extension: Union[None, str, tuple] = None) -> Generator:
        return self._list_blob_objects(self._get_folder_path(folder), filter_filename=filter_filename,
                                       filter_extension=filter_extension)

    def _blob_copy(self, dest_container_name: str, blob_name: str, remove_copied: bool):
        blob_url = self.blob_service.make_blob_url(self.container_name, blob_name)
        self.blob_service.copy_blob(dest_container_name, blob_name, blob_url)
        self._az_logger.debug(f'{blob_name} copied from {self.container_name} to {dest_container_name}')

        if remove_copied:
            self.blob_service.delete_blob(self.container_name, blob_name)
            self._az_logger.debug(f'{blob_name} removed from {self.container_name}')

    def copy_between_storages(self, dest_name: str, files_to_move: Union[str, list, Generator],
                              remove_copied: bool = False):
        if isinstance(files_to_move, str):
            self._blob_copy(dest_name, files_to_move, remove_copied)

        else:
            for blob in files_to_move:
                if isinstance(blob, Blob):
                    self._blob_copy(dest_name, blob.name, remove_copied)
                elif isinstance(blob, str):
                    self._blob_copy(dest_name, blob, remove_copied)

    ###########
    # READERS #
    ###########
    @contextmanager
    def _read_to_buffer(self, path):
        self._az_logger.debug(f'Reading from {self.container_name}: {path}')

        with io.BytesIO() as buff:
            buff = self.blob_service.get_blob_to_bytes(container_name=self.container_name, blob_name=path).content
            yield io.BytesIO(buff)

    @contextmanager
    def _read_to_str_buffer(self, path):
        self._az_logger.debug(f'Reading from {self.container_name}: {path}')

        with io.StringIO() as buff:
            buff = self.blob_service.get_blob_to_text(container_name=self.container_name, blob_name=path).content
            yield io.StringIO(buff)

    def read_csv(self, filename: str, folder: Union[str, None] = None, **kwargs):
        with self._read_to_buffer(self._get_full_path(filename, folder)) as buff:
            return pd.read_csv(buff, **kwargs)

    def read_excel(self, filename: str, folder: Union[str, None] = None, **kwargs):
        with self._read_to_buffer(self._get_full_path(filename, folder)) as buff:
            return pd.read_excel(buff, **kwargs)

    def read_parquet(self, filename: str, folder: Union[str, None] = None, **kwargs):
        with self._read_to_buffer(self._get_full_path(filename, folder)) as buff:
            return pd.read_parquet(buff, **kwargs)

    def read_yaml(self, filename: str, folder=None, yaml_loader=yaml.FullLoader):
        with self._read_to_buffer(self._get_full_path(filename, folder)) as buff:
            return yaml.load(buff, Loader=yaml_loader)

    def read_json(self, filename: str, folder=None, **kwargs):
        with self._read_to_buffer(self._get_full_path(filename, folder)) as buff:
            return json.load(buff, **kwargs)

    def read_object(self, filename: str, folder: Union[str, None] = None, **kwargs):
        with self._read_to_buffer(self._get_full_path(filename, folder)) as buff:
            return buff.read(**kwargs)

    ###########
    # WRITERS #
    ###########
    def _get_bucket_path(self, filename: str, folder: Union[str, None] = None):
        bucket_path = self._get_full_path(filename, folder)
        self._az_logger.debug(f'Writing in: {bucket_path}')

        return bucket_path

    def write_csv(self, df: pd.DataFrame, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.StringIO() as buff:
            df.to_csv(buff, **kwargs)
            self.blob_service.create_blob_from_text(container_name=self.container_name,
                                                    blob_name=self._get_bucket_path(filename, folder),
                                                    text=buff.getvalue())

    def write_excel(self, df: pd.DataFrame, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.BytesIO() as buff:
            df.to_excel(buff, **kwargs)
            self.blob_service.create_blob_from_bytes(container_name=self.container_name,
                                                     blob_name=self._get_bucket_path(filename, folder),
                                                     blob=buff.getvalue())

    def write_parquet(self, df: pd.DataFrame, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.BytesIO() as buff:
            df.to_parquet(buff, **kwargs)
            self.blob_service.create_blob_from_bytes(container_name=self.container_name,
                                                     blob_name=self._get_bucket_path(filename, folder),
                                                     blob=buff.getvalue())

    def write_yaml(self, data: dict, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.StringIO() as buff:
            yaml.dump(data, buff, **kwargs)
            self.blob_service.create_blob_from_text(container_name=self.container_name,
                                                    blob_name=self._get_bucket_path(filename, folder),
                                                    text=buff.getvalue())

    def write_json(self, data: dict, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.StringIO() as buff:
            json.dump(data, buff, **kwargs)
            self.blob_service.create_blob_from_text(container_name=self.container_name,
                                                    blob_name=self._get_bucket_path(filename, folder),
                                                    text=buff.getvalue())

    def write_object(self, write_object, filename: str, folder: Union[str, None] = None, **kwargs):
        if isinstance(write_object, bytes):
            self.blob_service.create_blob_from_bytes(container_name=self.container_name,
                                                     blob_name=self._get_bucket_path(filename, folder),
                                                     blob=write_object)
        else:
            self.blob_service.create_blob_from_stream(container_name=self.container_name,
                                                      blob_name=self._get_bucket_path(filename, folder),
                                                      stream=write_object)

    def write_object_from_file(self, object_filename: str, filename: str, folder: Union[str, None] = None, **kwargs):
        self.blob_service.create_blob_from_path(container_name=self.container_name,
                                                blob_name=self._get_bucket_path(filename, folder),
                                                file_path=object_filename, **kwargs)
