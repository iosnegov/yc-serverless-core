# app/cloud_function/schemas/list_objects_request.py
from pydantic import BaseModel, Field, ConfigDict


class ListObjectsRequest(BaseModel):
    """
    Request schema for listing objects in an S3-compatible object storage bucket via the REST API.
    """

    max_keys: int = Field(
        ...,
        ge=1,
        le=1000,
        description=(
            "Maximum number of objects to return in the response. "
            "Must be an integer between 1 and 1000 (inclusive). "
            "Default is 100."
        )
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "max_keys": 50
                }
            ]
        }
    )