from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.models import LoginRequest, SignupRequest, TokenResponse, UserResponse
from db.database import get_db
from db.models import UserRecord
from utils.auth import create_token, hash_password, verify_password
from db.repository import get_user_by_email, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    if get_user_by_email(db, body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    user = create_user(db, body.email, body.name, body.password)

    return TokenResponse(
        access_token=create_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, body.email)

    if (
        not user
        or not user.password_hash
        or not verify_password(body.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    return TokenResponse(
        access_token=create_token(user.id),
        user=UserResponse.model_validate(user),
    )
