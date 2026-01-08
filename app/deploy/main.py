# app/deploy/main.py
import os
from dotenv import load_dotenv
from .iam import generate_token
from .bucket import create_bucket
from .lockbox import create_secret
from .function import create_function, create_function_version
from .apigateway import create_apigateway, get_apigateway_domain


def deploy() -> str:
    """
    Full deployment pipeline for the Yandex Cloud serverless application.

    This function performs the following steps in order:
    1. Creates an S3-compatible Object Storage bucket (for application data).
    2. Packages sensitive configuration (S3 credentials, bucket name, region)
       into a Lockbox secret.
    3. Creates a Cloud Function resource.
    4. Deploys the function code as a new version, linking secrets securely.
    5. Creates an API Gateway and retrieves its public domain URL.

    Returns
    -------
    str
        Public HTTPS URL of the created API Gateway.
    """

    load_dotenv()

    token = generate_token()
    print("✅ IAM token created successfully.")

    create_bucket()
    print("✅ Bucket created successfully.")

    # Prepare secret payload from environment
    secrets = {
        "S3_ACCESS_KEY": os.environ["S3_ACCESS_KEY"],
        "S3_SECRET_KEY": os.environ["S3_SECRET_KEY"],
        "S3_BUCKET_NAME": os.environ["S3_BUCKET_NAME"],
        "S3_REGION": os.environ["S3_REGION"],
    }

    secret_id = create_secret(
        iam_token=token,
        payload_entries=secrets
    )
    print(f"✅ Lockbox secret created: {secret_id}")

    function_id = create_function(iam_token=token)
    print(f"✅ Cloud Function created: {function_id}")

    function_version_id = create_function_version(
        iam_token=token,
        function_id=function_id,
        secret_id=secret_id
    )
    print(f"✅ Function version deployed: {function_version_id}")

    gateway_id = create_apigateway(
        iam_token=token,
        function_id=function_id
    )
    print(f"✅ API Gateway created: {gateway_id}")

    gateway_url = get_apigateway_domain(iam_token=token, api_gateway_id=gateway_id)
    print(f"✅ API Gateway public URL: {gateway_url}")

    return gateway_url


# Execute only when the file is run directly (e.g., `python -m app.deploy.main`),
# not when imported as a module (e.g., `from app.deploy.main import deploy`).
if __name__ == "__main__":
    deploy()