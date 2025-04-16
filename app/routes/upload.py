"""Upload file to UploadThing and store the mapping."""

from fastapi import (
    APIRouter,
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse

from app.routes.recipes import validate_header
from app.services.uploadthing_service import UploadThingService

uploadthing_service = UploadThingService()


async def lifespan(_: FastAPI):
    """lipespan event for the FastAPI application, to close the UploadThing service."""
    yield
    await uploadthing_service.close()


router = APIRouter(lifespan=lifespan)


@router.post("")
async def upload_file(
    request: Request,
    user: str,
    file: UploadFile = File(...),
) -> dict:
    """
    Upload a file to UploadThing and store the mapping.

    Args:
        user (str): The username
        file (UploadFile): The file to upload

    Returns:
        dict: A dictionary containing the user and image URL
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User Param is missing"
        )
    await validate_header(request, user)

    file_data = await file.read()
    file_type = file.content_type or "application/octet-stream"

    url = uploadthing_service.upload_file(file_data, file_type, user)

    return JSONResponse(
        content={"user": user, "image_url": url}, status_code=status.HTTP_200_OK
    )
