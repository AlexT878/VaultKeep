from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from api.services.file_service import FileService, get_file_service
from db.database import get_db
from db.models import UserRecord
from utils.auth import get_current_user

router = APIRouter(prefix="/files", tags=["files"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: UserRecord = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    db: Session = Depends(get_db),
):
    """Upload a file. Stored under files/{user_id}/ and record metadata in DB."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    record = await file_service.store_and_record(
        file=file,
        user_id=current_user.id,
        db=db,
    )

    return {
        "id": record.id,
        "original_name": record.original_name,
        "random_name": record.random_name,
        "content_type": record.content_type,
        "size": record.size,
        "user_id": record.user_id,
        "created_at": record.created_at,
        "path": record.path,
    }


@router.get("")
async def list_user_files(
    current_user: UserRecord = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    db: Session = Depends(get_db),
):
    return file_service.get_files_by_user(db, current_user.id)


@router.get("/search_content")
async def search_content(
    q: str,
    limit: int = 20,
    offset: int = 0,
    current_user: UserRecord = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    db: Session = Depends(get_db),
):
    q = (q or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Search query is required")

    liimit = max(1, min(limit, 100))
    offset = max(0, offset)

    results = file_service.search_files(db, current_user.id, q, limit, offset)
    return results


@router.get("/{file_id}")
async def get_file_info(
    file_id: int,
    current_user: UserRecord = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    db: Session = Depends(get_db),
):
    db_file = file_service.get_file_by_id(db, file_id, current_user.id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file


@router.get("/{file_id}/content")
async def get_file_content(
    file_id: int,
    current_user: UserRecord = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    db: Session = Depends(get_db),
):
    db_file = file_service.get_file_by_id(db, file_id, current_user.id)

    if not db_file or not Path(db_file.path).exists():
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(path=db_file.path, filename=db_file.original_name)
