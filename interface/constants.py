import os
from dotenv import load_dotenv

load_dotenv()

IMAP_HOST = os.getenv('IMAP_HOST')
IMAP_USERNAME = os.getenv('IMAP_USERNAME')
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')

SMTP_HOST = os.getenv('IMAP_HOST')
SMTP_USERNAME = os.getenv('IMAP_USERNAME')
SMTP_PASSWORD = os.getenv('IMAP_PASSWORD')

S3_KEY = os.getenv('S3_KEY')
S3_SECRET = os.getenv('S3_SECRET')
S3_BUCKET = os.getenv('S3_BUCKET')
S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_REGION = os.getenv('S3_REGION')

SITES_DIR = os.getenv('SITES_DIR')
CDN_DOMAIN = os.getenv('CDN_DOMAIN')
DEPLOY_DOMAIN = os.getenv('DEPLOY_DOMAIN')

REPLY_ADDRESS = os.getenv('REPLY_ADDRESS')
REPLY_TO_ADDRESS = os.getenv('REPLY_TO_ADDRESS')
