# app/deploy/function.py
import os
import zipfile
import tempfile
import requests
from ..cloud_function.s3.client import get_s3_client


def create_function(
    iam_token: str
) -> str:
    """
    Create a new Yandex Cloud Function resource in the specified folder.

    Parameters
    ----------
    iam_token : str
        Valid IAM token for authentication.

    Returns
    -------
    str
        ID of the newly created function.
    """

    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json"
    }

    url = "https://serverless-functions.api.cloud.yandex.net/functions/v1/functions"

    payload = {
        "folderId": os.environ["YC_FOLDER_ID"],
        "name": os.environ["SERVERLESS_FUNCTION_NAME"]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status() # Raises HTTPError for 4xx/5xx
    return response.json()["metadata"]["functionId"]


def _create_zip_archive(source_dir: str, zip_path: str) -> None:
    """Create a ZIP archive from a source directory, excluding all __pycache__/ directories and their contents."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zf.write(file_path, arcname)


def _upload_zip_to_storage(zip_path: str, object_key: str) -> None:
    """
    Upload ZIP to Yandex Object Storage.
    
    Note: 
    -----
    It would be better to use a dedicated deployment bucket for storing
    function artifacts (ZIP files) separately from application data.
    However, for simplicity and due to the educational nature of this project,
    I reuse the same S3 bucket for both purposes.
    """

    client = get_s3_client()
    client.upload_file(Filename=zip_path, Bucket=os.environ["S3_BUCKET_NAME"], Key=object_key)


def create_function_version(
    iam_token: str,
    function_id: str,
    secret_id: str,
    runtime: str = "python312",
    entrypoint: str = "index.handler",
) -> str:
    """
    Deploy a new version of a Yandex Cloud Function by packaging code into a ZIP archive,
    uploading it to Object Storage, and linking environment variables to Lockbox secrets.

    Parameters
    ----------
    iam_token : str
        IAM token for authenticating management API requests.
    function_id : str
        ID of the existing Cloud Function to update.
    secret_id : str
        ID of the Lockbox secret containing S3 credentials and configuration.
    runtime : str, optional
        Runtime environment (default: "python312").
    entrypoint : str, optional
        Handler entrypoint in the form "module.submodule.function" (default: "index.handler").

    Returns
    -------
    str
        ID of the newly created function version.
    """
    
    # Generate a unique ZIP filename to prevent overwrites in Object Storage
    zip_filename = f"function-{function_id}.zip"
    
    # Create and upload deployment archive in a temporary directory (auto-cleaned)
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, zip_filename)
        _create_zip_archive(os.environ["SERVERLESS_FUNCTION_PATH"], zip_path)
        _upload_zip_to_storage(zip_path, zip_filename)

    # Prepare authenticated request to Cloud Functions management API
    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json"
    }
    
    url = "https://serverless-functions.api.cloud.yandex.net/functions/v1/versions"

    secrets = [
        {"id": secret_id, "key": "S3_BUCKET_NAME", "environmentVariable": "S3_BUCKET_NAME"},
        {"id": secret_id, "key": "S3_REGION", "environmentVariable": "S3_REGION"},
        {"id": secret_id, "key": "S3_ACCESS_KEY", "environmentVariable": "S3_ACCESS_KEY"},
        {"id": secret_id, "key": "S3_SECRET_KEY", "environmentVariable": "S3_SECRET_KEY"},
    ]

    payload = {
        "functionId": function_id,
        "runtime": runtime,
        "entrypoint": entrypoint,
        "serviceAccountId": os.environ["YC_SERVICE_ACCOUNT_ID"],
        "secrets": secrets,
        "package": {
            "bucketName": os.environ["S3_BUCKET_NAME"],
            "objectName": zip_filename
        },
        "resources": {
            "memory": 512 * 1024 * 1024,  # 512 MB
        },
        "executionTimeout": "10s"
    }

    # Submit version creation request
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status() # Raises HTTPError for 4xx/5xx
    return response.json()["metadata"]["functionVersionId"]