# app/cloud_function/s3/objects.py
import os
from typing import Any
from .client import get_s3_client


def generate_upload_presigned_url(key: str, expires_in: int = 3600) -> str:
    """
    Generate a presigned URL for uploading an object directly to the S3 bucket.
    
    Parameters
    ----------
    key : str
        The object key (path) in the bucket.
    expires_in : int, optional
        URL expiration time in seconds (default: 3600 = 1 hour).
    
    Returns
    -------
    str
        Presigned URL for PUT request.
    """
    client = get_s3_client()
    return client.generate_presigned_url(
        'put_object',
        Params = {
            'Bucket': os.environ["S3_BUCKET_NAME"], 
            'Key': key
        },
        ExpiresIn=expires_in
    )


def download_object(key: str) -> bytes:
    """
    Download the binary content of an S3 object by its key.

    Parameters
    ----------
    key : str
        The key of the object to download.

    Returns
    -------
    bytes
        The raw content of the object.
    """

    client = get_s3_client()
    response = client.get_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=key)
    return response["Body"].read()


def delete_object(key: str) -> None:
    """
    Delete an S3 object by its key.

    Parameters
    ----------
    key : str
        The key of the object to delete.
    """
    
    client = get_s3_client()
    client.delete_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=key)


def get_object_metadata(key: str) -> dict[str, Any]:
    """
    Retrieve metadata of an S3 object without downloading its content.

    Parameters
    ----------
    key : str
        The key of the object to inspect.

    Returns
    -------
    dict[str, Any]
        Object metadata including ETag, ContentLength, LastModified, etc.
    """
    
    client = get_s3_client()
    return client.head_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=key)


def list_objects(max_keys: int = 100) -> list[dict[str, Any]]:
    """
    List objects in the S3 bucket (up to max_keys items).

    Parameters
    ----------
    max_keys : int, optional
        Maximum number of objects to return (capped at 1000).

    Returns
    -------
    list[dict[str, Any]]
        List of object summaries with Key, Size, LastModified, etc.
    """
    
    client = get_s3_client()
    response = client.list_objects_v2(
        Bucket=os.environ["S3_BUCKET_NAME"],
        MaxKeys=min(max_keys, 1000)
    )
    return response.get("Contents", [])