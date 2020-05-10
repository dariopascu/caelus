import click

from caelus.gcp.auth import GCPAuth
from caelus.gcp.storages import CloudStorage
import logging


@click.command()
@click.option('-cf', '--credentials_file', type=str, help='GCP Credentials Json')
@click.option('-bn', '--bucket_name', type=str, help='GCP Cloud Storage bucket name')
def cloud_storage_test(credentials_file, bucket_name):
    gcp_logger = logging.getLogger('gcp')
    gcp_logger.setLevel(logging.DEBUG)

    auth = GCPAuth(credentials_file=credentials_file)
    cloud_storage = CloudStorage(auth, bucket_name=bucket_name)

    file_list = cloud_storage.list_objects(filter_extension='csv', filter_filename='demo')

    for file in file_list:
        print(file.name)
        cloud_storage.read_object_to_file(file)

    ###########
    # READERS #
    ###########
    csv = cloud_storage.read_csv('demo.csv', index_col=0)
    excel = cloud_storage.read_excel('demo.xlsx')
    json = cloud_storage.read_json('demo.json')
    yaml = cloud_storage.read_yaml('demo.yaml')
    parquet = cloud_storage.read_parquet('demo.parquet', folder='parquet')

    cloud_storage_object = cloud_storage.read_object('demo.jpeg')

    # Move example
    cloud_storage.move_object(cloud_storage.bucket_name, 'demo.json', 'move/demo.json', remove_copied=False)
    moved_objects = cloud_storage.list_objects(folder='move')
    for moved_object in moved_objects:
        print(moved_object.name)

    ###########
    # WRITERS #
    ###########
    cloud_storage.write_csv(csv, 'demo_write.csv', folder='caelus')
    cloud_storage.write_excel(excel, 'demo_write.xlsx', folder='caelus')
    cloud_storage.write_json(json, 'demo_write.json', folder='caelus')
    cloud_storage.write_yaml(yaml, 'demo_write.yaml', folder='caelus')
    cloud_storage.write_parquet(parquet, 'demo_write.parquet', folder='caelus')

    cloud_storage.write_object(cloud_storage_object, 'demo_write.jpeg', folder='caelus')

    with open('../image.jpeg', 'rb') as image:
        cloud_storage.write_object(image, 'demo_load_write.jpeg', folder='caelus')

    cloud_storage.write_object_from_file('../image.jpeg', 'demo_from_file.jpeg', folder='caelus')


if __name__ == '__main__':
    cloud_storage_test.main(standalone_mode=False)
