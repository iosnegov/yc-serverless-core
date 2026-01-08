# app/cloud_function/s3/client.py
import os
import boto3


def get_s3_client() -> boto3.client:
    """
    Create and return a fully configured synchronous S3-compatible client for Yandex Cloud Object Storage.

    The client is pre-configured using environment variables injected into the Cloud Function at deployment time.
    It is stateless, thread-safe, and suitable for direct use in serverless execution environments.

    Returns
    -------
    boto3.client

    Notes
    -----
    The returned client is a standard boto3 S3 client. Static type checkers (e.g., mypy, Pylance)
    may not recognize its dynamic methods, resulting in "unresolved attribute" warnings.
    These warnings are expected and safe to ignore when working with S3-compatible APIs.
    """
    
    return boto3.client(
        service_name="s3",
        endpoint_url="https://storage.yandexcloud.net",
        aws_access_key_id=os.environ["S3_ACCESS_KEY"],
        aws_secret_access_key=os.environ["S3_SECRET_KEY"],
        region_name=os.environ["S3_REGION"],
    )