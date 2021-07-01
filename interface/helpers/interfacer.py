import boto3
import redis 
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

redis_client = redis.Redis(host='redis', port=6379, db=0)

def upload_file(filename, new_filename, author):
    response = client.upload_file(filename, constants.S3_BUCKET,
                                  new_filename, ExtraArgs={'ACL': 'public-read', 'Metadata': {'author': author}})
    return response

def get_site_metadata(sitename, user):
    name_slugged = slugify(sitename)
    path = constants.SITES_DIR + name_slugged + '/info.json'
    site_exists = False
    head = None

    try:
        # if this doesn't result in a 404, it already exists
        head = client.head_object(Bucket=constants.S3_BUCKET,
                           Key=path)
        site_exists = True
    except ClientError as e:
        site_exists = int(e.response['Error']['Code']) != 404
    
    if site_exists: 
        # check that the user has permission to edit it 
        if head.get('Metadata')['author'] == user:
            return head.get('Metadata')
        else:
            return None
    else:
        return {'subdomain': name_slugged, 'author': user, 'new': True}
    
def create_site(metadata):
    del metadata['new']
    # upload the info file with metadata to indicate that the site exists
    path = constants.SITES_DIR + metadata['subdomain'] + '/info.json'
    client.put_object(Body="", Bucket=constants.S3_BUCKET, Key=path, ContentType='text/json', Metadata=metadata)


def create_session_url(metadata):
    session_id = str(uuid.uuid4())
    redis_client.set(session_id, json.dumps(metadata))
    # expire the key after two hours 
    redis_client.expire(session_id, 7200)
    return constants.DEPLOY_DOMAIN + 'settings/session/' + session_id


def create_post(sitename, author, title, content, files):

    path = constants.SITES_DIR + sitename + '/'
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
        upload_file(filename, new_filename, author)

        # replace local references to files to the uploaded locations
        content = content.replace(
            filename, constants.CDN_DOMAIN + new_filename)

    client.put_object(Body=content, Bucket=constants.S3_BUCKET, Key="{}{}/index.html".format(
        path, slug), ContentType='text/html', ACL='public-read', Metadata={'author': author})

    if sitename == 'assorted':
        return constants.DEPLOY_DOMAIN + slug
    else: 
        return constants.DEPLOY_DOMAIN.replace("https://", "https://{}.".format(sitename)) + slug
