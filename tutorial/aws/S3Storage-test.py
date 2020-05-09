import click
from boto3.s3.transfer import TransferConfig

from caelus.aws.auth import AWSAuth
from caelus.aws.storages import S3Storage
import logging


@click.command()
@click.option('-pn', '--profile_name', type=str, help='AWS configured profile name')
@click.option('-bn', '--bucket_name', type=str, help='AWS S3 bucket name')
def s3_storage_test(profile_name, bucket_name):
    aws_logger = logging.getLogger('aws')
    aws_logger.setLevel(logging.DEBUG)
    auth = AWSAuth(profile_name=profile_name)
    s3 = S3Storage(auth, bucket_name=bucket_name)

    s3.transfer_config = TransferConfig(multipart_threshold=8388608, max_concurrency=10,
                                        multipart_chunksize=8388608,
                                        num_download_attempts=5, max_io_queue=100, io_chunksize=262144,
                                        use_threads=True)

    file_list = s3.list_files(filter_extension='csv', filter_filename='demo')

    for file in file_list:
        print(file)
        s3.read_object_to_file(file)

    ###########
    # READERS #
    ###########
    csv = s3.read_csv('demo.csv', index_col=0)
    excel = s3.read_excel('demo.xlsx')
    json = s3.read_json('demo.json')
    yaml = s3.read_yaml('demo.yaml')
    parquet = s3.read_parquet('demo.parquet', folder='parquet')

    s3_object = s3.read_object('demo.jpeg')

    ###########
    # WRITERS #
    ###########
    s3.write_csv(csv, 'demo_write.csv', folder='caelus')
    s3.write_excel(excel, 'demo_write.xlsx', folder='caelus')
    s3.write_json(json, 'demo_write.json', folder='caelus')
    s3.write_yaml(yaml, 'demo_write.yaml', folder='caelus')
    s3.write_parquet(parquet, 'demo_write.parquet', folder='caelus')

    s3.write_object(s3_object, 'demo_write.jpeg', folder='caelus')

    with open('../image.jpeg', 'rb') as image:
        s3.write_object(image, 'demo_load_write.jpeg', folder='caelus')

    s3.write_object_from_file('../image.jpeg', 'demo_from_file.jpeg', folder='caelus')


if __name__ == '__main__':
    s3_storage_test.main(standalone_mode=False)
