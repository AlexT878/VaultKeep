from sqlalchemy.orm import Session
from db.models import UserRecord, FileRecord
from utils.auth import hash_password
from pathlib import Path


def get_user_by_email(db: Session, email: str):
    return db.query(UserRecord).filter(UserRecord.email == email).first()


def create_user(db: Session, email: str, name: str, password: str):
    user = UserRecord(
        email=email,
        name=name,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_file_record(
    db: Session, user_id: int, original_name: str, file_path: str, size: int
):
    stored_name = Path(file_path).name

    new_file = FileRecord(
        user_id=user_id,
        original_name=original_name,
        stored_name=stored_name,
        file_path=file_path,
        size=size,
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file


def get_files_by_user(db: Session, user_id: int):
    return db.query(FileRecord).filter(FileRecord.user_id == user_id).all()


def get_file_by_id(db: Session, file_id: int, user_id: int):
    return (
        db.query(FileRecord)
        .filter(FileRecord.id == file_id, FileRecord.user_id == user_id)
        .first()
    )
