from boto3.s3.transfer import TransferConfig

from caelus.aws.auth import AWSAuth
from caelus.aws.storages import S3Storage
import logging

if __name__ == '__main__':
    aws_logger = logging.getLogger('aws')
    aws_logger.setLevel(logging.DEBUG)
    auth = AWSAuth(profile_name='default')
    s3 = S3Storage(auth, bucket_name='bdaa-workload-docker')

    s3.transfer_config = None

    file_list = s3.list_files(filter_extension='csv', filter_filename='iris')

    for file in file_list:
        print(file)

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
