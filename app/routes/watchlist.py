from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import get_current_user

from database import (
    get_watchlist,
    add_to_watchlist,
    remove_from_watchlist,
)


router = APIRouter(
    prefix="/watchlist",
    tags=["Watchlist"],
)


class WatchlistRequest(BaseModel):

    keyword: str


# --------------------------------------------------
# GET WATCHLIST
# --------------------------------------------------

@router.get("")
def read_watchlist(
    user=Depends(get_current_user),
):

    return {
        "watchlist": get_watchlist(
            user["id"]
        )
    }


# --------------------------------------------------
# ADD
# --------------------------------------------------

@router.post("")
def add_watchlist(
    request: WatchlistRequest,

    user=Depends(get_current_user),
):

    keyword = request.keyword.strip()


    if not keyword:

        raise HTTPException(
            status_code=400,
            detail="Keyword cannot be empty.",
        )


    add_to_watchlist(
        user["id"],
        keyword,
    )


    return {
        "success": True,
        "keyword": keyword.upper(),
    }


# --------------------------------------------------
# REMOVE
# --------------------------------------------------

@router.delete("/{keyword}")
def delete_watchlist(
    keyword: str,

    user=Depends(get_current_user),
):

    remove_from_watchlist(
        user["id"],
        keyword,
    )


    return {
        "success": True,
    }
