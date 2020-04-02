import io
import json
import logging
from typing import Union, Generator
from contextlib import contextmanager
import pandas as pd
import yaml

from caelus.aws.auth import AWSAuth
from caelus.core.storages import Storage


class S3Storage(Storage):
    _aws_logger = logging.getLogger('aws')

    def __init__(self, auth: AWSAuth, bucket_name: str, base_path: str = "") -> None:
        Storage.__init__(self, base_path=base_path)

        self.bucket_name = bucket_name

        self.s3_client = auth.session.client('s3')
        self.s3_resource = auth.session.resource('s3')
        self.bucket = self.s3_resource.Bucket(bucket_name)

    ################
    # OBJECT ADMIN #
    ################
    def _list_s3_objects(self, prefix: str, filter_filename: Union[None, str] = None,
                         only_files: bool = True, filter_extension: Union[None, str, tuple] = None) -> Generator:
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)

        while True:
            keys = [items['Key'] for items in response['Contents']]
            for key in keys:
                filtered_key = self._filter_key(key, filter_filename, only_files, filter_extension)
                if filtered_key is not None:
                    yield filtered_key

            if response['IsTruncated']:
                response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix,
                                                          ContinuationToken=response['NextContinuationToken'])
            else:
                break

    @staticmethod
    def _filter_key(key, filter_filename, only_files, filter_extension):
        if (filter_filename is not None and filter_filename not in key) or (only_files and key.endswith('/')) or (
                filter_extension is not None and not key.endswith(filter_extension)):
            return None
        else:
            return key

    def list_files(self, folder: Union[None, str] = None, filter_filename: Union[None, str] = None,
                   only_files: bool = True, filter_extension: Union[None, str, tuple] = None) -> Generator:
        return self._list_s3_objects(self._get_folder_path(folder), filter_filename=filter_filename,
                                     only_files=only_files, filter_extension=filter_extension)

    def _object_copy(self, dest_bucket_name: str, object_name: str, remove_copied: bool):
        self.s3_resource.Object(dest_bucket_name, object_name).copy_from(CopySource={'Bucket': self.bucket_name,
                                                                                     'Key': object_name})
        self._aws_logger.debug(f'{object_name} copied from {self.bucket_name} to {dest_bucket_name}')
        if remove_copied:
            self.s3_resource.Object(self.bucket_name, object_name).delete()
            self._aws_logger.debug(f'{object_name} removed from {self.bucket_name}')

    def copy_between_storages(self, dest_name: str, files_to_move: Union[str, list, Generator],
                              remove_copied: bool = False):
        if isinstance(files_to_move, str):
            self._object_copy(dest_name, files_to_move, remove_copied)
        else:
            for bucket_object in files_to_move:
                self._object_copy(dest_name, bucket_object, remove_copied)

    ###########
    # READERS #
    ###########
    @contextmanager
    def _read_to_buffer(self, path):
        self._aws_logger.debug(f'Reading from {self.bucket_name}: {path}')

        with io.BytesIO() as buff:
            buff = self.s3_client.get_object(Bucket=self.bucket_name, Key=path)['Body']
            yield buff

    @contextmanager
    def _download_to_buffer(self, path):
        self._aws_logger.debug(f'Reading from {self.bucket_name}: {path}')

        with io.BytesIO() as buff:
            s3_object = self.s3_resource.Object(self.bucket_name, path)
            s3_object.download_fileobj(buff)
            yield buff

    def read_csv(self, filename: str, folder: Union[str, None] = None, **kwargs):
        with self._read_to_buffer(self._get_full_path(filename, folder)) as buff:
            return pd.read_csv(buff, **kwargs)

    def read_excel(self, filename: str, folder: Union[str, None] = None, **kwargs):
        with self._download_to_buffer(self._get_full_path(filename, folder)) as buff:
            return pd.read_excel(buff, **kwargs)

    def read_parquet(self, filename: str, folder: Union[str, None] = None, **kwargs):
        with self._download_to_buffer(self._get_full_path(filename, folder)) as buff:
            return pd.read_parquet(buff, **kwargs)

    def read_yaml(self, filename: str, folder=None, **kwargs):
        with self._read_to_buffer(self._get_full_path(filename, folder)) as buff:
            return yaml.load(buff, **kwargs)

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
        self._aws_logger.debug(f'Writing in: {bucket_path}')

        return bucket_path

    def write_csv(self, df: pd.DataFrame, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.StringIO() as buff:
            df.to_csv(buff, **kwargs)
            self.s3_resource.Object(self.bucket_name, self._get_bucket_path(filename, folder)).put(Body=buff.getvalue())

    def write_excel(self, df: pd.DataFrame, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.BytesIO() as buff:
            df.to_excel(buff, **kwargs)
            self.s3_resource.Object(self.bucket_name, self._get_bucket_path(filename, folder)).put(Body=buff.getvalue())

    def write_parquet(self, df: pd.DataFrame, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.BytesIO() as buff:
            df.to_parquet(buff, **kwargs)
            self.s3_resource.Object(self.bucket_name, self._get_bucket_path(filename, folder)).put(Body=buff.getvalue())

    def write_yaml(self, data: dict, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.StringIO() as buff:
            yaml.dump(data, buff, **kwargs)
            self.s3_resource.Object(self.bucket_name, self._get_bucket_path(filename, folder)).put(Body=buff.getvalue())

    def write_json(self, data: dict, filename: str, folder: Union[str, None] = None, **kwargs):
        with io.StringIO() as buff:
            json.dump(data, buff, **kwargs)
            self.s3_resource.Object(self.bucket_name, self._get_bucket_path(filename, folder)).put(Body=buff.getvalue())

    def write_object(self, write_object, filename: str, folder: Union[str, None] = None, **kwargs):
        self.s3_resource.Object(self.bucket_name, self._get_bucket_path(filename, folder)).put(Body=write_object,
                                                                                               **kwargs)