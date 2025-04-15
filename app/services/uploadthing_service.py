import logging
import requests
from typing import Dict, Optional, Any
from app.internal.settings import settings
from fastapi import HTTPException

MAX_FILE_SIZE = 30 * 1024 * 1024  # 30MB in bytes
ALLOWED_FILE_TYPES = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp'
}

class UploadThingService:
    """Service for interacting with the UploadThing API."""
    
    def __init__(self):
        self.secret_key = settings.UPLOADTHING_SECRET_KEY
        self.base_url = "https://api.uploadthing.com/v6"
        self.headers = {
            "x-uploadthing-api-key": self.secret_key,
        }
        self.timeout = 30.0  # 30 seconds timeout
        self.max_file_size = MAX_FILE_SIZE
        self.allowed_file_types = ALLOWED_FILE_TYPES
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
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
                timeout=timeout or self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            
            raise HTTPException(
                status_code=response.status_code,
            )
                
        except requests.RequestException as e:
            raise HTTPException(
                status_code=504,
                detail="Request to UploadThing timed out"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error: {str(e)}"
            )

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
        # Validate file size
        self.logger.info(f"File size: {len(file_data)} bytes")
        if len(file_data) > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail={
                    "message": "File too large",
                    "max_size": f"{self.max_file_size / 1024 / 1024}MB"
                }
            )
        self.logger.info(f"File type: {file_type}")
        # Validate file type
        if file_type not in self.allowed_file_types:
            raise HTTPException(
                status_code=415,
                detail={
                    "message": "Unsupported file type",
                    "allowed_types": list(self.allowed_file_types)
                }
            )

        try:
            self.logger.info(f"Uploading file to UploadThing for user: {username}")
            # Get presigned URL
            presigned_data = self._make_request(
                method="POST",
                endpoint="uploadFiles",
                data={
                    "files": [{
                        "name": username,
                        "type": file_type,
                        "size": len(file_data)
                    }]
                }
            )
            
            # Extract upload details
            upload_url = presigned_data["data"][0]["url"]
            fields = presigned_data["data"][0]["fields"]
            file_url = presigned_data["data"][0]["fileUrl"]

            # Prepare multipart form data
            self.logger.info(f"Uploading file to UploadThing S3 for user: {username}")
            
            # Prepare form data for upload
            files = {'file': (username, file_data, file_type)}
            
            upload_response = requests.post(
                upload_url,
                data=fields,
                files=files,
                timeout=self.timeout
            )
            upload_response.raise_for_status()
            self.logger.info(f"File uploaded to UploadThing for user: {username}")
            
            return file_url
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error: {str(e)}"
            )

    def delete_file(self, file_key: str) -> bool:
        """Delete a file from UploadThing.
        
        Args:
            file_key: The key of the file to delete
            
        Returns:
            bool: True if deletion was successful
        """
        self.logger.info(f"Deleting file from UploadThing for key: {file_key}")
        self._make_request(
            method="POST",
            endpoint="deleteFile",
            data={"fileKeys": [file_key]}
        )
        return True
    
    def close(self):
        """Cleanup resources."""
        if self.session:
            self.session.close()
            self.logger.info("UploadThing session closed")