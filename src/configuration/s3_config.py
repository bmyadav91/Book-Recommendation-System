import boto3
from botocore.exceptions import NoCredentialsError
import os
from src.logger import logging

LoadedS3Connection = None
def s3_bucket_connection():
    global LoadedS3Connection
    if LoadedS3Connection is None:
        try:
            LoadedS3Connection = boto3.client(
                's3',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
                aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
                region_name=os.getenv("AWS_REGION")
            )
            logging.info("Successfully connected to S3.")
        except NoCredentialsError:
            logging.error("Credentials not available.")
            LoadedS3Connection = None
        except Exception as e:
            logging.error(f"Error connecting to S3: {e}")
            LoadedS3Connection = None
    return LoadedS3Connection

