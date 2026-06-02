from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.rate_limit import limiter
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserOut
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_register)
def register(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register(db, payload)


@router.post("/login", response_model=Token)
@limiter.limit(settings.rate_limit_login)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    token = auth_service.login(db, email=form.username, password=form.password)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
