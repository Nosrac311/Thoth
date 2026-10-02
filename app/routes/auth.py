from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from database import (
    create_user,
    get_user_by_email,
)

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class RegisterRequest(BaseModel):

    email: EmailStr

    password: str


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@router.post("/register")
def register(
    request: RegisterRequest,
):

    email = request.email.lower().strip()


    if len(request.password) < 8:

        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters.",
        )


    existing = get_user_by_email(
        email
    )


    if existing:

        raise HTTPException(
            status_code=409,
            detail="An account with that email already exists.",
        )


    hashed = hash_password(
        request.password
    )


    try:

        user_id = create_user(
            email,
            hashed,
        )

    except Exception:

        raise HTTPException(
            status_code=409,
            detail="An account with that email already exists.",
        )


    token = create_access_token(
        user_id
    )


    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": email,
        },
    }


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@router.post("/login")
def login(
    request: LoginRequest,
):

    email = request.email.lower().strip()


    user = get_user_by_email(
        email
    )


    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )


    if not verify_password(
        request.password,
        user["password_hash"],
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )


    token = create_access_token(
        user["id"]
    )


    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
        },
    }
