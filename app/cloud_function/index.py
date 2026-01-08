# app/cloud_function/index.py
import json
import base64
from typing import Any
from pydantic import ValidationError
from s3 import (
    generate_upload_presigned_url,
    download_object,
    delete_object,
    get_object_metadata,
    list_objects
)
from schemas import StorageKeyRequest, ListObjectsRequest


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Yandex Cloud Function handler using action-based routing.
    
    Supports REST-like operations over S3-compatible storage (Yandex Object Storage).
    
    event : dict
        Event object passed by Yandex API Gateway.
        Contains standard HTTP fields (httpMethod, headers, queryStringParameters, body),
        as well as custom operation context injected via the OpenAPI specification:
        - requestContext.apiGateway.operationContext.action: str
    context : Any
        Runtime context provided by Yandex Cloud Functions (unused in this handler).
    
    Returns
    -------
    dict
        Standard HTTP response: {statusCode, headers, body}
    
    Supported Actions
    -----------------
    - generate_upload_url
    - download_object
    - delete_object
    - get_object_metadata
    - list_objects
    """

    action = (
        event.get("requestContext", {})
        .get("apiGateway", {})
        .get("operationContext", {})
        .get("action")
    )

    try:
        if action == "generate_upload_url":
            return _handle_generate_upload_url(event)
        elif action == "download_object":
            return _handle_download_object(event)
        elif action == "delete_object":
            return _handle_delete_object(event)
        elif action == "get_object_metadata":
            return _handle_get_object_metadata(event)
        elif action == "list_objects":
            return _handle_list_objects(event)
        else:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "UNKNOWN_ACTION",
                    "message": f"Unknown action: {action}"
                })
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            })
        }


def _handle_generate_upload_url(event: dict[str, Any]) -> dict[str, Any]:
    """
    Action: generate_upload_url — POST with { "storage_key": "..." }
    
    Returns a presigned PUT URL.
    """
    try:
        body = json.loads(event.get("body", "{}"))
        request = StorageKeyRequest(**body)
        
        url = generate_upload_presigned_url(key=request.storage_key)
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "upload_url": url,
                "storage_key": request.storage_key
            })
        }
    except ValidationError as e:
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "VALIDATION_ERROR",
                "message": "Invalid storage_key",
                "details": e.errors()
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "URL_GENERATION_FAILED",
                "message": str(e)
            })
        }


def _handle_download_object(event: dict[str, Any]) -> dict[str, Any]:
    """
    Action: download_object — GET with query param ?storage_key=...
    
    Returns binary content as base64-encoded string.
    """
    try:
        params = event.get("queryStringParameters") or {}
        request = StorageKeyRequest(storage_key=params.get("storage_key", ""))
        
        content = download_object(key=request.storage_key)
        encoded_content = base64.b64encode(content).decode('utf-8')
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/octet-stream"},
            "body": encoded_content,
            "isBase64Encoded": True
        }
    except ValidationError as e:
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "VALIDATION_ERROR",
                "message": "Invalid storage_key",
                "details": e.errors()
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "DOWNLOAD_FAILED",
                "message": str(e)
            })
        }


def _handle_delete_object(event: dict[str, Any]) -> dict[str, Any]:
    """
    Action: delete_object — DELETE with query param ?storage_key=...
    """
    try:
        params = event.get("queryStringParameters") or {}
        request = StorageKeyRequest(storage_key=params.get("storage_key", ""))
        
        delete_object(key=request.storage_key)
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": "Object deleted successfully",
                "storage_key": request.storage_key
            })
        }
    except ValidationError as e:
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "VALIDATION_ERROR",
                "message": "Invalid storage_key",
                "details": e.errors()
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "DELETION_FAILED",
                "message": str(e)
            })
        }


def _handle_get_object_metadata(event: dict[str, Any]) -> dict[str, Any]:
    """
    Action: get_object_metadata — GET with query param ?storage_key=...
    """
    try:
        params = event.get("queryStringParameters") or {}
        request = StorageKeyRequest(storage_key=params.get("storage_key", ""))
        
        metadata = get_object_metadata(key=request.storage_key)
        
        safe_metadata = {k: v for k, v in metadata.items() if k != 'ResponseMetadata'}
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(safe_metadata, default=str)
        }
    except ValidationError as e:
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "VALIDATION_ERROR",
                "message": "Invalid storage_key",
                "details": e.errors()
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "METADATA_FETCH_FAILED",
                "message": str(e)
            })
        }


def _handle_list_objects(event: dict[str, Any]) -> dict[str, Any]:
    """
    Action: list_objects — GET with optional ?max_keys=...
    """
    try:
        params = event.get("queryStringParameters") or {}
        max_keys = params.get("max_keys")
        
        request = ListObjectsRequest(max_keys=int(max_keys) if max_keys else 100)
        
        objects = list_objects(max_keys=request.max_keys)
        
        serializable_objects = []
        for obj in objects:
            obj_copy = obj.copy()
            if "LastModified" in obj_copy:
                obj_copy["LastModified"] = obj_copy["LastModified"].isoformat()
            serializable_objects.append(obj_copy)
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "objects": serializable_objects,
                "count": len(serializable_objects)
            })
        }
    except ValidationError as e:
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "VALIDATION_ERROR",
                "message": "Invalid max_keys parameter",
                "details": e.errors()
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "LISTING_FAILED",
                "message": str(e)
            })
        }