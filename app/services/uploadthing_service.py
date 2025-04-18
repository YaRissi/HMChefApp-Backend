"""Use UploadThing API to upload files."""

import logging
from typing import Any, Dict, Optional

import requests
from fastapi import HTTPException

from app.internal.settings import settings


class UploadThingService:
    """Service for interacting with the UploadThing API."""

    def __init__(self):
        self.secret_key = settings.UPLOADTHING_SECRET_KEY
        self.base_url = "https://api.uploadthing.com/v6"
        self.headers = {
            "x-uploadthing-api-key": self.secret_key,
        }
        self.max_file_size = 30 * 1024 * 1024  # 30MB in bytes
        self.allowed_file_types = {
            "image/jpeg",
            "image/png",
        }
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Make a request to the UploadThing API with error handling.

        Args:
            method: HTTP method to use
            endpoint: API endpoint
            data: Request data
            timeout: Custom timeout for this request

        Returns:
            Dict containing the API response

        Raises:
            HTTPException: If any error occurs during the request
        """
        try:
            response = self.session.request(
                method=method,
                url=f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=data,
                timeout=timeout or 30.0,
            )

            if response.status_code == 200:
                return response.json()

            raise HTTPException(
                status_code=response.status_code,
            )

        except requests.RequestException as e:
            raise HTTPException(
                status_code=504, detail="Request to UploadThing timed out"
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Unexpected error: {str(e)}"
            ) from e

    def upload_file(self, file_data: bytes, file_type: str, username: str) -> str:
        """Upload a file to UploadThing with size and type validation.

        Args:
            file_data: The binary file data
            file_type: The MIME type of the file
            username: The username associated with the upload

        Returns:
            str: The URL of the uploaded file

        Raises:
            HTTPException: If file size or type is invalid
        """

        self.logger.info(f"File size: {len(file_data)} bytes")
        if len(file_data) > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail={
                    "message": "File too large",
                    "max_size": f"{self.max_file_size / 1024 / 1024}MB",
                },
            )
        self.logger.info(f"File type: {file_type}")

        if file_type not in self.allowed_file_types:
            raise HTTPException(
                status_code=415,
                detail={
                    "message": "Unsupported file type",
                    "allowed_types": list(self.allowed_file_types),
                },
            )

        try:
            self.logger.info(f"Uploading file to UploadThing for user: {username}")
            presigned_data = self._make_request(
                method="POST",
                endpoint="uploadFiles",
                data={
                    "files": [
                        {"name": username, "type": file_type, "size": len(file_data)}
                    ]
                },
            )

            upload_url = presigned_data["data"][0]["url"]
            fields = presigned_data["data"][0]["fields"]
            file_url = presigned_data["data"][0]["fileUrl"]

            self.logger.info(f"Uploading file to UploadThing S3 for user: {username}")

            files = {"file": (username, file_data, file_type)}

            upload_response = requests.post(
                upload_url, data=fields, files=files, timeout=30.0
            )
            upload_response.raise_for_status()
            self.logger.info(f"File uploaded to UploadThing for user: {username}")

            return file_url
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Unexpected error: {str(e)}"
            ) from e

    def delete_file(self, url: str) -> bool:
        """Delete a file from UploadThing.

        Args:
            file_key: The key of the file to delete

        Returns:
            bool: True if deletion was successful
        """
        file_key = url.split("/")[-1]
        self.logger.info(f"Deleting file from UploadThing for key: {file_key}")
        self._make_request(
            method="POST", endpoint="deleteFile", data={"fileKeys": [file_key]}
        )
        return True

    def close(self):
        """Cleanup resources."""
        if self.session:
            self.session.close()
            self.logger.info("UploadThing session closed")
