import redis
import boto3
import json
import uuid
from datetime import datetime
from slugify import slugify

from boto3 import session
from botocore.client import Config
from boto3.s3.transfer import S3Transfer

import constants as constants

r = redis.Redis(host=constants.REDIS_HOST, port=constants.REDIS_PORT)


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


def get_site(name):
    res = r.get(name)
    if res != None:
        return json.loads(res)
    return None


def create_site(name, user, title="", description=""):
    r.set(name, json.dumps(
        {'id': str(uuid.uuid4()),
         'user': user,
         'path': "{}{}/".format(constants.SITES_DIR, name),
         'created': datetime.utcnow(),
         'title': title,
         'description': description}))


def create_post(site, title, content, files):
    slug = slugify(title)
    for filename in files.values():
        new_filename = "{}{}/{}".format(site['path'], slug, str(uuid.uuid4()))
        # content.
    return
