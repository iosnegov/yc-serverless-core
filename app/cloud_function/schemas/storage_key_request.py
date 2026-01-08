# app/cloud_function/schemas/storage_key_request.py
from pydantic import BaseModel, Field, field_validator, ConfigDict


class StorageKeyRequest(BaseModel):
    """
    A universal request schema for any S3 operation that requires only an object key.
    """
    storage_key: str = Field(
        ...,
        min_length = 1,
        description = "The key (path) of the object in the bucket."
    )

    @field_validator("storage_key")
    @classmethod
    def validate_storage_key(cls, v: str) -> str:
        """Validate that string fields are non-empty, non-blank and has no leading/trailing whitespace."""
        if not v:
            raise ValueError("Object name cannot be empty")
        if not v.strip():
            raise ValueError("Object name cannot be blank")
        if v != v.strip():
            raise ValueError("Object name must not have leading or trailing whitespace")
        return v
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {"storage_key": "cute-cat.png"},
            ]
        }
    )