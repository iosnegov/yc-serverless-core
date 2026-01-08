# app/deploy/bucket.py
import os
from ..cloud_function.s3.client import get_s3_client


def create_bucket() -> None:
    """
    Create the application's S3 bucket as defined in the configuration.
    """
    
    client = get_s3_client() 
    client.create_bucket(Bucket=os.environ["S3_BUCKET_NAME"])