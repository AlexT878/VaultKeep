from fastapi import APIRouter, Depends, HTTPException
from db.models import UserRecord
from db.database import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])


def get_user_by_id(id: int, db: Session):
    query = select(UserRecord).where(UserRecord.id == id)
    return db.execute(query).scalars().first()


def check_duplicate_email(email: str, db: Session):
    query = select(UserRecord).where(UserRecord.email == email)
    user = db.execute(query).scalars().first()

    return user is not None


@router.get("/")
async def read_users(db: Session = Depends(get_db)):
    stmt = select(UserRecord)
    users = db.scalars(stmt).all()

    return users


@router.post("/")
async def create_user(
    name: str,
    email: str,
    phone: str,
    avatar_url: str,
    password_hash: str,
    db: Session = Depends(get_db),
):
    # Check if there is already a user with that email
    query = select(UserRecord).where(UserRecord.email == email)
    existing_users = db.execute(query).scalars().first()
    if existing_users:
        raise HTTPException(400, detail="Email already registered")

    # Add new user
    new_user = UserRecord(
        name=name,
        email=email,
        phone=phone,
        avatar_url=avatar_url,
        password_hash=password_hash,
    )
    db.add(new_user)
    db.commit()

    db.refresh(new_user)

    return new_user


@router.delete("/{user_id}")
async def delete_user(id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(id, db)

    if not user:
        raise HTTPException(status_code=404, detail=f"User ID: {id} was not found.")

    deleted_id = id
    db.delete(user)
    db.commit()

    return deleted_id


@router.patch("/{user_id}")
async def update_user(
    id: int,
    name: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    avatar_url: str | None = None,
    password_hash: str | None = None,
    db: Session = Depends(get_db),
):
    user = get_user_by_id(id, db)

    if not user:
        raise HTTPException(status_code=404, detail=f"User ID: {id} was not found.")

    if name is not None:
        user.name = name

    if email is not None:
        if check_duplicate_email(email, db) is True:
            raise HTTPException(400, detail="Email already registered")
        user.email = email

    if phone is not None:
        user.phone = phone

    if avatar_url is not None:
        user.avatar_url = avatar_url

    if password_hash is not None:
        user.password_hash = password_hash

    db.commit()
    db.refresh(user)

    return user.id
