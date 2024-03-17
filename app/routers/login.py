from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ..models import Token
from ..admin_database import get_admin, authenticate_admin
from ..user_database import get_database, authenticate_user
from ..admin_auth import create_admin_access_token
from ..user_auth import create_user_access_token
from sqlalchemy.orm import Session


router = APIRouter()

@router.post("/login", tags=["Authentication"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_database)
) -> Token:
    username = form_data.username
    password = form_data.password

    # Attempt authentication for both admin and user
    admin = authenticate_admin(username, password, db=db)
    user = authenticate_user(username, password, db=db)

    if admin:
        access_token = create_admin_access_token(data={"sub": admin.username})
    elif user:
        access_token = create_user_access_token(data={"sub": user.username})
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=access_token, token_type="bearer")
