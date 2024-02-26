import boto3
import botocore
from botocore import UNSIGNED
from botocore.client import Config
import os

s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED),region_name='us-east-1')
my_bucket = s3.Bucket('noaa-goes16')
objects = my_bucket.objects.filter(Prefix='ABI-L2-LSTF/2024/049/')
print(objects)
download_path = '/var/py/volunclima/scripts/goes-16/GOES-16 Samples/LST'
for obj in objects:
    
    path, filename = os.path.split(obj.key)
    print(filename)
    download_file_path = os.path.join(download_path, filename)
    my_bucket.download_file(obj.key, download_file_path)
    


""" objects = my_bucket.objects.filter(Prefix='ABI-L2-RRQPEF/2024/051/')
print(objects)
download_path = '/var/py/volunclima/scripts/goes-16/GOES-16 Samples/RRQPE'
for obj in objects:
    
    path, filename = os.path.split(obj.key)
    print(filename)
    download_file_path = os.path.join(download_path, filename)
    my_bucket.download_file(obj.key, download_file_path) """
    