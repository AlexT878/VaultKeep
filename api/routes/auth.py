from fastapi import APIRouter, Depends, HTTPException, status
from db.models import UserRecord
from db.database import get_db
from pydantic import BaseModel, Field, EmailStr, ConfigDict
import hashlib
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

router = APIRouter(prefix="/auth", tags=["auth"])


def check_user_exists(db: Session, email: str):
    user = db.query(UserRecord).filter(UserRecord.email == email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    return False


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=5, max_length=20)
    avatar_url: str = Field(default="")
    password: str = Field(min_length=8, max_length=20)


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    avatar_url: str | None = None
    password_hash: str


class TokenResponse(BaseModel):
    user: User
    access_token: str
    token_type: str = "bearer"


@router.post("/login")
def login():
    """Login endpoint. Implement later."""
    pass


@router.post("/signup")
def signup(user_create: UserCreate, db=Depends(get_db)):
    check_user_exists(db, user_create.email)

    hashed_password = hashlib.sha256(user_create.password.encode()).hexdigest()

    new_user = UserRecord(
        email=user_create.email,
        name=user_create.name,
        avatar_url=user_create.avatar_url,
        password_hash=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user_pydantic = User.model_validate(new_user)
    access_token = create_access_token(data={"sub": str(user_pydantic.id)})

    return TokenResponse(
        user=user_pydantic, access_token=access_token, token_type="bearer"
    )
