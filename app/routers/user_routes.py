from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import CurrentUser, authenticate_owner, create_access_token
from app.schemas import schemas

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """OAuth2 password flow. Used by the Authorize button in /docs, and by any
    client that needs to call the protected endpoints."""
    if not authenticate_owner(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return schemas.Token(access_token=create_access_token(form_data.username), token_type="bearer")


@router.get("/me", response_model=schemas.CurrentUserOut)
def read_current_user(username: CurrentUser):
    return schemas.CurrentUserOut(username=username)
