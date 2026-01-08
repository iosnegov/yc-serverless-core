# app/deploy/apigateway.py
import os
import requests


def create_apigateway(
    iam_token: str,
    function_id: str,
) -> str:
    """
    Create a Yandex Cloud API Gateway from an OpenAPI specification file,
    dynamically injecting the function ID and service account ID.

    The OpenAPI file (YAML or JSON) must contain the following placeholders:
    - <FUNCTION_ID>
    - <SERVICE_ACCOUNT_ID>

    These are replaced at runtime with actual values before sending the request.

    Parameters
    ----------
    iam_token : str
        IAM token for authenticating Yandex Cloud management API requests.
    function_id : str
        ID of the deployed Cloud Function to integrate with.

    Returns
    -------
    str
        ID of the newly created API Gateway.
    """

    # Read and inject values in one step
    spec_path = os.environ["OPENAPI_SPEC_PATH"]
    with open(spec_path, "r", encoding="utf-8") as f:
        openapi_spec = f.read()

    # Replace placeholders with real values
    openapi_spec = openapi_spec.replace("<FUNCTION_ID>", function_id)
    openapi_spec = openapi_spec.replace(
        "<SERVICE_ACCOUNT_ID>",
        os.environ["YC_SERVICE_ACCOUNT_ID"]
    )

    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json"
    }

    url = "https://serverless-apigateway.api.cloud.yandex.net/apigateways/v1/apigateways"

    payload = {
        "folderId": os.environ["YC_FOLDER_ID"],
        "name": os.environ["API_GATEWAY_NAME"],
        "openapiSpec": openapi_spec
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["metadata"]["apiGatewayId"]


def get_apigateway_domain(
    iam_token: str,
    api_gateway_id: str
) -> str:
    """
    Retrieve the public domain URL of a Yandex Cloud API Gateway.

    Parameters
    ----------
    iam_token : str
        IAM token for authenticating management API requests.
    api_gateway_id : str
        ID of the API Gateway.

    Returns
    -------
    str
        Public HTTPS URL of the API Gateway.
    """

    headers = {"Authorization": f"Bearer {iam_token}"}
    url = f"https://serverless-apigateway.api.cloud.yandex.net/apigateways/v1/apigateways/{api_gateway_id}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    gateway_info = response.json()
    domain = gateway_info["domain"]
    return f"https://{domain}"