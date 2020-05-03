import io
import json
import logging
from contextlib import contextmanager
from tempfile import TemporaryFile
from typing import Union, Generator

import yaml
from google.cloud import storage
from google.cloud.storage.blob import Blob

import pandas as pd

from caelus.core.storages import Storage
from caelus.gcp.auth import GCPAuth


class CloudStorage(Storage):
    _gcp_logger = logging.getLogger('gcp')

    def __init__(self, auth: GCPAuth, bucket_name: str, base_path: str = ""):
        Storage.__init__(self, base_path=base_path)
        self._bucket_name = bucket_name
        self.storage_client = storage.Client(project=auth.project_id, credentials=auth.credential)
        self.bucket = self.storage_client.get_bucket(self._bucket_name)

    @property
    def bucket_name(self):
        return self._bucket_name

    ################
    # OBJECT ADMIN #
    ################
    def _list_bucket_objects(self, prefix: str, filter_filename: Union[None, str] = None,
                             only_files: bool = True, filter_extension: Union[None, str, tuple] = None) -> Generator:
        response = self.storage_client.list_blobs(bucket_or_name=self.bucket_name, prefix=prefix)

        while True:
            for key in response:
                filtered_key = self._filter_key(key, filter_filename, only_files, filter_extension)
                if filtered_key is not None:
                    yield filtered_key

            if response.next_page_token is not None:
                response = self.storage_client.list_blobs(bucket_or_name=self.bucket_name, prefix=prefix,
                                                          page_token=response.next_page_token)
            else:
                break

    @staticmethod
    def _filter_key(key, filter_filename, only_files, filter_extension):
        key_name = key.name
        if (filter_filename is not None and filter_filename not in key_name) or (
                only_files and key_name.endswith('/')) or (
                filter_extension is not None and not key_name.endswith(filter_extension)):
            return None
        else:
            return key

    def list_files(self, folder: Union[None, str] = None, filter_filename: Union[None, str] = None,
                   filter_extension: Union[None, str, tuple] = None) -> Generator:
        return self._list_bucket_objects(self._get_folder_path(folder), filter_filename=filter_filename,
                                         filter_extension=filter_extension)

    def _blob_copy(self, dest_bucket_name: str, blob_name: str, remove_copied: bool):

        source_blob = self.bucket.blob(blob_name)
        destination_bucket = self.storage_client.bucket(dest_bucket_name)
        self.bucket.copy_blob(source_blob, destination_bucket, blob_name)
        self._gcp_logger.debug(f'{blob_name} copied from {self.bucket_name} to {dest_bucket_name}')

        if remove_copied:
            source_blob.delete()
            self._gcp_logger.debug(f'{blob_name} removed from {self.bucket_name}')

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
        self._gcp_logger.debug(f'Reading from {self.bucket_name}: {path}')
        blob_file = self.bucket.blob(path)
        with io.BytesIO() as buff:
            blob_file.download_to_file(buff)
            buff.seek(0)
            yield buff

    @contextmanager
    def _read_to_str_buffer(self, path):
        self._gcp_logger.debug(f'Reading from {self.bucket_name}: {path}')
        blob_file = self.bucket.blob(path)
        with io.StringIO() as buff:
            blob_file.download_as_string(buff)
            yield buff

    def read_csv(self, filename: str, folder: Union[str, None] = None, **kwargs):
        with self._read_to_buffer(self._get_full_path(filename, folder)) as buff:
            return pd.read_csv(buff, **kwargs)

    def read_excel(self, filename: str, folder: Union[str, None] = None, **kwargs):
        with self._read_to_buffer(self._get_full_path(filename, folder)) as buff:
            return pd.read_excel(buff, **kwargs)

    def read_parquet(self, filename: str, folder: Union[str, None] = None, **kwargs):
        with self._read_to_buffer(self._get_full_path(filename, folder)) as buff:
            return pd.read_parquet(buff, **kwargs)

    def read_yaml(self, filename: str, folder: Union[str, None] = None, yaml_loader=yaml.FullLoader):
        with self._read_to_buffer(self._get_full_path(filename, folder)) as buff:
            return yaml.load(buff, Loader=yaml_loader)

    def read_json(self, filename: str, folder: Union[str, None] = None, **kwargs):
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
        self._gcp_logger.debug(f'Writing in: {bucket_path}')

        return bucket_path

    def write_csv(self, df: pd.DataFrame, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.StringIO() as buff:
            df.to_csv(buff, **kwargs)
            buff.seek(0)
            self.bucket.blob(self._get_bucket_path(filename, folder)).upload_from_file(buff)

    def write_excel(self, df: pd.DataFrame, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.BytesIO() as buff:
            df.to_excel(buff, **kwargs)
            buff.seek(0)
            self.bucket.blob(self._get_bucket_path(filename, folder)).upload_from_file(buff)

    def write_parquet(self, df: pd.DataFrame, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.BytesIO() as buff:
            df.to_parquet(buff, **kwargs)
            buff.seek(0)
            self.bucket.blob(self._get_bucket_path(filename, folder)).upload_from_file(buff)

    def write_yaml(self, data: dict, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.StringIO() as buff:
            yaml.dump(data, buff, **kwargs)
            buff.seek(0)
            self.bucket.blob(self._get_bucket_path(filename, folder)).upload_from_file(buff)

    def write_json(self, data: dict, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.StringIO() as buff:
            json.dump(data, buff, **kwargs)
            buff.seek(0)
            self.bucket.blob(self._get_bucket_path(filename, folder)).upload_from_file(buff)

    def write_object(self, write_object, filename: str, folder: Union[str, None] = None, **kwargs):
        if isinstance(write_object, bytes):
            self.bucket.blob(self._get_bucket_path(filename,
                                                   folder)).upload_from_string(write_object,
                                                                               content_type='application/octet-stream')
        else:
            self.bucket.blob(self._get_bucket_path(filename, folder)).upload_from_file(write_object, **kwargs)

    def write_object_from_file(self, object_filename: str, filename: str, folder: Union[str, None] = None, **kwargs):
        self.bucket.blob(self._get_bucket_path(filename, folder)).upload_from_filename(object_filename, **kwargs)
