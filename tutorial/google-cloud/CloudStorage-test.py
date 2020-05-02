from caelus.gcp.auth import GCPAuth
from caelus.gcp.storages import CloudStorage
import logging

if __name__ == '__main__':
    gcp_logger = logging.getLogger('gcp')
    gcp_logger.setLevel(logging.DEBUG)

    auth = GCPAuth(credentials_file='gcp-credentials.json')
    cloud_storage = CloudStorage(auth, bucket_name='caelus-storage-test')

    file_list = cloud_storage.list_files(filter_extension='csv', filter_filename='demo')

    for file in file_list:
        print(file)

    ###########
    # READERS #
    ###########
    csv = cloud_storage.read_csv('demo.csv', index_col=0)
    excel = cloud_storage.read_excel('demo.xlsx')
    json = cloud_storage.read_json('demo.json')
    yaml = cloud_storage.read_yaml('demo.yaml')
    parquet = cloud_storage.read_parquet('demo.parquet', folder='parquet')

    cloud_storage_object = cloud_storage.read_object('demo.jpeg')

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
