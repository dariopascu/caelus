import click

from caelus.az.auth import AzureAuth
from caelus.az.storages import BlobStorage
import logging


@click.command()
@click.option('-ak', '--access_key', type=str, help='Azure access key')
@click.option('-an', '--account_name', type=str, help='Blob account name')
@click.option('-cn', '--container_name', type=str, help='Azure access key')
def azure_storage_test(access_key, account_name, container_name):
    az_logger = logging.getLogger('az')
    az_logger.setLevel(logging.DEBUG)

    auth = AzureAuth(
        access_key=access_key)
    blob = BlobStorage(auth, account_name=account_name, container_name=container_name)

    file_list = blob.list_objects(filter_extension='csv', filter_filename='demo')

    for blob_file in file_list:
        print(blob_file.name)
        blob.read_object_to_file(blob_file)

    ###########
    # READERS #
    ###########
    csv = blob.read_csv('demo.csv', index_col=0)
    excel = blob.read_excel('demo.xlsx')
    json = blob.read_json('demo.json')
    yaml = blob.read_yaml('demo.yaml')
    parquet = blob.read_parquet('demo.parquet', folder='parquet')

    blob_object = blob.read_object('demo.jpeg')

    ###########
    # WRITERS #
    ###########
    blob.write_csv(csv, 'demo_write.csv', folder='caelus')
    blob.write_excel(excel, 'demo_write.xlsx', folder='caelus')
    blob.write_json(json, 'demo_write.json', folder='caelus')
    blob.write_yaml(yaml, 'demo_write.yaml', folder='caelus')
    blob.write_parquet(parquet, 'demo_write.parquet', folder='caelus')

    blob.write_object(blob_object, 'demo_write.jpeg', folder='caelus')

    with open('../image.jpeg', 'rb') as image:
        blob.write_object(image, 'demo_load_write.jpeg', folder='caelus')

    blob.write_object_from_file('../image.jpeg', 'demo_from_file.jpeg', folder='caelus')


if __name__ == '__main__':
    azure_storage_test.main(standalone_mode=False)
