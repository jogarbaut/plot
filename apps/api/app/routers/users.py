from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import verify_token
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreate,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db),
) -> User:
    user = User(
        auth0_id=token["sub"],
        email=body.email,
        username=body.username,
        first_name=body.first_name,
        last_name=body.last_name,
        birthday=body.birthday,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    return user


@router.get("/me", response_model=UserResponse)
def get_me(
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db),
) -> User:
    user = db.query(User).filter(User.auth0_id == token["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
