import logging

import boto3
from botocore.client import Config
from config_data.config import ConfigEnv, load_config

config: ConfigEnv = load_config()
logger = logging.getLogger(__name__)


# Конфигурация S3 клиента
s3_client = boto3.client(
    's3',
    config=Config(signature_version='s3v4'),
    endpoint_url=config.s3.url,
    aws_access_key_id=config.s3.key_id,
    aws_secret_access_key=config.s3.key_secret,
)
def upload_to_s3(file_stream, file_name, bucket_name=config.s3.name, expiration=129600):
    try:
        s3_client.upload_fileobj(file_stream, bucket_name, file_name)
        s3_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': file_name},
                                                  ExpiresIn=expiration)

        print(s3_url)
        return s3_url

    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        return None

def generate_presigned_s3_url(file_name, bucket_name=config.s3.name, expiration=129600):  # 36 часов (129600 секунд)
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        logger.error(f"Error generating presigned URL: {e}")
        return None