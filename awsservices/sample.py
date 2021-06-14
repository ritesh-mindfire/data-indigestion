import logging
import boto3
from botocore.exceptions import ClientError
import pprint
from botocore.client import Config


s3_client = boto3.client('s3')
# s3_client = boto3.resource('s3', config=Config(signature_version='s3v4'))
# s3_resource = boto3.resource('s3')

# s3_resource.create_bucket(Bucket='botos3newbucket',
#                           CreateBucketConfiguration={
#                               'LocationConstraint': 'ap-south-1'})

# # Retrieve the list of existing buckets
# s3 = boto3.client('s3')
# response = s3.list_buckets()

# # Output the bucket names
# print('Existing buckets:')
# for bucket in response['Buckets']:
#     print(f'  {bucket["Name"]}')

# session = boto3.session.Session()
# current_region = session.region_name
# print(current_region)
 
OBJECT_NAME = 'myimage.png'
FILE_NAME = './%s' % OBJECT_NAME # file_path or file on local m/c
BUCKET_NAME = 'botos3quickbucket'


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # #If S3 object_name was not specified, use file_name
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        print('Truee')
    except ClientError as e:
        logging.error(e)
        print('FFFalse')

# upload_file(FILE_NAME, BUCKET_NAME, OBJECT_NAME)

#-------------------for downloading file from S3--------------------

# FILE_NAME = './imagr.png'
# s3_client.download_file(BUCKET_NAME, OBJECT_NAME, FILE_NAME)

#-------------------Presigned URLs--------------------------------
# try:
#     response = s3_client.generate_presigned_url('get_object',
#                                                 Params={'Bucket': BUCKET_NAME,
#                                                         'Key': OBJECT_NAME},
#                                                 ExpiresIn=60*10)
#     print('resoponse------ >',response)
# except ClientError as e:
#     logging.error(e)
#     print(e)

try:
    response = s3_client.generate_presigned_url('put_object',
                                                Params={'Bucket': BUCKET_NAME,
                                                        'Key': OBJECT_NAME},
                                                ExpiresIn=60*10,
                                                HttpMethod='PUT')
    print(response)
except ClientError as e:
    logging.error(e)
    print(e)

# # Generate a presigned S3 POST URL
# s3_client = boto3.client('s3')
# try:
#     response = s3_client.generate_presigned_post(BUCKET_NAME,
#                                                     OBJECT_NAME,
#                                                     Fields=None,
#                                                     Conditions=None,
#                                                     ExpiresIn=60*10)
#     # The response contains the presigned URL and required fields
#     pprint.pprint(response)
# except ClientError as e:
#     logging.error(e)
#     print(e)

# import requests    # To install: pip install requests

# # Generate a presigned S3 POST URL

# # Demonstrate how another Python program can use the presigned URL to upload a file
# with open('horse.jpg', 'rb') as f:
#     files = {'file': ('testing', f)}
#     http_response = requests.post(response['url'], data=response['fields'], files=files)
# # If successful, returns HTTP status code 204
# print('File upload HTTP status code: %s' % http_response.status_code)
# print(http_response)
# logging.info(f'File upload HTTP status code: {http_response.status_code}')


import json

# Create a bucket policy
# bucket_name = BUCKET_NAME
# bucket_policy = {
#     'Version': '2012-10-17',
#     'Statement': [{
#         'Sid': 'AddPerm1',
#         'Effect': 'Allow',
#         'Principal': '*',
#         'Action': ['s3:GetObject'],
#         'Resource': f'arn:aws:s3:::{bucket_name}/*'
#     }]
# }

# # Convert the policy from JSON dict to string
# bucket_policy = json.dumps(bucket_policy)

# # Set the new policy
# # s3 = boto3.client('s3')
# s3_client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)

# result = s3_client.get_bucket_policy(Bucket=BUCKET_NAME)
# print(result['Policy'])

# result = s3_client.get_bucket_acl(Bucket=BUCKET_NAME)
# print(result)

# response = s3_client.get_bucket_cors(Bucket=bucket_name)
# print(response)