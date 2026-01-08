# app/deploy/iam.py
import os
import json
import time
import jwt
import requests


def generate_token() -> str:
    """
    Generate an IAM token for a Yandex Cloud service account using its authorized key.

    This function reads a service account's private key from a JSON file specified
    in the ``YC_AUTHORIZED_KEY`` environment variable, signs a JWT with it, and exchanges
    the JWT for a short-lived IAM token via the Yandex Cloud IAM API.

    The JWT is valid for 300 seconds, and the resulting IAM token can be used
    to authenticate API requests to Yandex Cloud services.

    Returns
    -------
    str
        A valid IAM token string.
    """

    authorized_key = os.environ["YC_AUTHORIZED_KEY"]

    with open(authorized_key, "r") as f:
        key = json.load(f)

    service_account_id = key["service_account_id"]
    key_id = key["id"]
    private_key = key["private_key"]

    # Prepare JWT
    token_url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    now = int(time.time())
    payload = {
        'aud': token_url,
        'iss': service_account_id,
        'iat': now,
        'exp': now + 300
    }

    # Yandex Cloud requires PS256 for JWT signing when exchanging for an IAM token
    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id}
    )

    # Exchange JWT for IAM token
    body = {"jwt": encoded_token}
    headers = {"Content-Type": "application/json"}

    response = requests.post(token_url, json=body, headers=headers)
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx
    return response.json()["iamToken"]