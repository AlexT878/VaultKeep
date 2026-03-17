from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from db.models import FileContentRecord, FileRecord
from sqlalchemy import func


class FileService:
    def __init__(self, base_dir: Path | str = "files") -> None:
        self.base_dir = Path(base_dir)

    def get_upload_dir(self, user_id: int) -> Path:
        """Return the upload directory for a given user (without creating it)."""
        return self.base_dir / str(user_id)

    async def store(self, file: UploadFile, user_id: int) -> dict:
        """Store an uploaded file on disk under files/{user_id}/ and return metadata (including raw bytes)."""

        original_name = Path(file.filename or "").name
        ext = Path(original_name).suffix

        random_name = f"{uuid4().hex}{ext}"

        user_dir = self.get_upload_dir(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        dest = user_dir / random_name

        content = await file.read()
        dest.write_bytes(content)

        return {
            "filename": original_name,
            "stored_filename": random_name,
            "content_type": file.content_type or "application/octet-stream",
            "size": len(content),
            "path": str(dest),
            "raw_bytes": content,
        }

    async def store_and_record(
        self,
        *,
        file: UploadFile,
        user_id: int,
        db: Session,
    ) -> FileRecord:
        """Store file on disk and create a FileRecord in the database."""

        # 1. Store file on disk
        stored = await self.store(file=file, user_id=user_id)

        # 2. Store file metadata in DB
        record = FileRecord(
            original_name=stored["filename"],
            random_name=stored["stored_filename"],
            content_type=stored["content_type"],
            size=stored["size"],
            path=stored["path"],
            user_id=user_id,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # 3. Store file content as tsvector in DB

        raw_bytes = stored.get("raw_bytes", b"")
        try:
            text_content = raw_bytes.decode("utf-8", errors="ignore")
        except Exception:
            text_content = ""

        if text_content:
            content_record = FileContentRecord(
                file_id=record.id,
                content_tsv=func.to_tsvector("english", text_content),
            )
            db.add(content_record)

        db.commit()
        db.refresh(record)

        return record

    def get_files_by_user(self, db: Session, user_id: int):
        return db.query(FileRecord).filter(FileRecord.user_id == user_id).all()

    def get_file_by_id(self, db: Session, file_id: int, user_id: int):
        return (
            db.query(FileRecord)
            .filter(FileRecord.id == file_id, FileRecord.user_id == user_id)
            .first()
        )

    def search_files(self, db: Session, user_id: int, query_text: str):
        return (
            db.query(FileRecord)
            .join(FileContentRecord)
            .filter(
                FileRecord.user_id == user_id,
                FileContentRecord.content_tsv.op("@@")(
                    func.plainto_tsquery("english", query_text)
                ),
            )
            .all()
        )


def get_file_service() -> FileService:
    """FastAPI dependency to provide a FileService instance."""
    return FileService()
