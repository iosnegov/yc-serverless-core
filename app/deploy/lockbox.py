# app/deploy/lockbox.py
import os
import requests


def create_secret(
    iam_token: str,
    payload_entries: dict[str, str],
) -> str:
    """
    Create a new secret in Yandex Lockbox with an initial version containing the provided entries.

    Parameters
    ----------
    iam_token : str
        Valid IAM token for authentication.
    payload_entries : dict[str, str]
        Key-value pairs to store as text entries in the first version of the secret.

    Returns
    -------
    str
        ID of the newly created secret.
    """
    
    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json"
    }

    url = "https://lockbox.api.cloud.yandex.net/lockbox/v1/secrets"

    payload = {
        "folderId": os.environ["YC_FOLDER_ID"],
        "name": os.environ["LOCKBOX_SECRET_NAME"],
        "versionPayloadEntries": [
            {
                "key": key,
                "textValue": value
            }
            for key, value in payload_entries.items()
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status() # Raises HTTPError for 4xx/5xx
    return response.json()["metadata"]["secretId"]