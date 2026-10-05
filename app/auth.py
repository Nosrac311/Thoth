import os

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash

from database import get_user_by_id


# --------------------------------------------------
# CONFIG
# --------------------------------------------------

SECRET_KEY = os.getenv("JWT_SECRET")

if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET environment variable is not set."
    )


ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


# --------------------------------------------------
# PASSWORD HASHING
# --------------------------------------------------

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:

    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:

    return password_hash.verify(
        password,
        hashed_password,
    )


# --------------------------------------------------
# JWT
# --------------------------------------------------

def create_access_token(
    user_id: int,
) -> str:

    expires = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "exp": expires,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# --------------------------------------------------
# CURRENT USER
# --------------------------------------------------

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials =
        Depends(security),
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token.",
            )

        user_id = int(user_id)

    except (
        JWTError,
        ValueError,
        TypeError,
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token.",
        )


    user = get_user_by_id(
        user_id
    )


    if user is None:

        raise HTTPException(
            status_code=401,
            detail="User no longer exists.",
        )
    print(
    "JWT USER ID:",
    user_id
    )

    user = get_user_by_id(user_id)

    print(
        "USER FOUND:",
        user is not None
    )



    return user
