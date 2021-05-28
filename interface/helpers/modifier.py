import boto3

import json
import uuid
from datetime import datetime
from slugify import slugify

from boto3 import session
from botocore.client import Config
from botocore.exceptions import ClientError

import constants as constants


session = session.Session()
client = session.client('s3',
                        region_name=constants.S3_REGION,
                        endpoint_url=constants.S3_ENDPOINT,
                        aws_access_key_id=constants.S3_KEY,
                        aws_secret_access_key=constants.S3_SECRET)


def upload_file(filename, new_filename):
    response = client.upload_file(filename, constants.S3_BUCKET,
                                  new_filename, ExtraArgs={'ACL': 'public-read'})
    return response


def create_post(title, content, files):

    path = constants.SITES_DIR + 'assorted/'
    slug = slugify(title)
    slug_exists = False

    try:
        # if this doesn't result in a 404, it already exists
        client.head_object(Bucket=constants.S3_BUCKET,
                           Key="{}{}/index.html".format(path, slug))
        slug_exists = True
    except ClientError as e:
        slug_exists = int(e.response['Error']['Code']) != 404

    # the slug already exists, add a random uuid
    if slug_exists:
        slug = slug + '-' + str(uuid.uuid4())

    # upload any attached files
    for filename in files.values():
        filetype = filename.split('.')[1]
        new_filename = "{}{}/{}.{}".format(path,
                                           slug, str(uuid.uuid4()), filetype)
        upload_file(filename, new_filename)

        # replace local references to files to the uploaded locations
        content = content.replace(
            filename, constants.CDN_DOMAIN + new_filename)

    client.put_object(Body=content, Bucket=constants.S3_BUCKET, Key="{}{}/index.html".format(
        path, slug), ContentType='text/html', ACL='public-read')

    return constants.DEPLOY_DOMAIN + slug
