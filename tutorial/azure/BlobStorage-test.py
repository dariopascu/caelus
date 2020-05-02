from caelus.az.auth import AzureAuth
from caelus.az.storages import BlobStorage
import logging

if __name__ == '__main__':
    az_logger = logging.getLogger('az')
    az_logger.setLevel(logging.DEBUG)

    auth = AzureAuth()
    blob = BlobStorage()

    file_list = blob.list_files(filter_extension='csv', filter_filename='demo')

    for file in file_list:
        print(file)

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
