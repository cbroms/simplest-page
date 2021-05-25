import constants as constants

import boto3
from boto3 import session
from botocore.client import Config
from boto3.s3.transfer import S3Transfer

session = session.Session()
client = session.client('s3',
                        region_name=constants.S3_REGION,
                        endpoint_url=constants.S3_ENDPOINT,
                        aws_access_key_id=constants.S3_KEY,
                        aws_secret_access_key=constants.S3_SECRET)

transfer = S3Transfer(client)


def upload_file(filename, new_filename):
    transfer.upload_file(filename, constants.S3_BUCKET, new_filename)
    response = client.put_object_acl(
        ACL='public-read', Bucket=constants.S3_BUCKET, Key=new_filename)
    return response
