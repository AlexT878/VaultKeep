from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from db.database import get_db

from db.models import UserRecord, FileRecord
from utils.auth import get_current_user
from utils.files import save_file_to_disk
from db.repository import create_file_record, get_files_by_user, get_file_by_id

router = APIRouter(prefix="/files", tags=["files"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a file. Stored under files/{user_id}/. Returns metadata."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )
    file_path, file_size = await save_file_to_disk(file, current_user.id)

    new_file = create_file_record(
        db, current_user.id, file.filename, str(file_path), file_size
    )

    return new_file


@router.get("")
async def list_user_files(
    current_user: UserRecord = Depends(get_current_user), db: Session = Depends(get_db)
):
    return get_files_by_user(db, current_user.id)


@router.get("/{file_id}")
async def get_file_content(
    file_id: int,
    current_user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_file = get_file_by_id(db, file_id, current_user.id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file


@router.get("/{file_id}/content")
async def get_file_content(
    file_id: int,
    current_user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_file = get_file_by_id(db, file_id, current_user.id)

    if not db_file or not Path(db_file.file_path).exists():
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(path=db_file.file_path, filename=db_file.original_name)
