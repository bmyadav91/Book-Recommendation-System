import boto3
from botocore.exceptions import NoCredentialsError
import os

def s3_bucket_connection():
    try:
        return boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
    except NoCredentialsError:
        print("Credentials not available.")
    except Exception as e:
        print(f"Error connecting to S3: {e}")
        return None

