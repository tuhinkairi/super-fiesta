from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from src.models.user_model import UserCreate, UserOut, UserUpdate
from src.services.user_services import (
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
)
from src.setup.dependencies import get_db


router = APIRouter(prefix="/users", tags=["users"])


def parse_user_id(user_id: str) -> ObjectId:
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    return ObjectId(user_id)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate, db=Depends(get_db)):
    return await create_user(db, user.model_dump())


@router.get("", response_model=list[UserOut])
async def list_users_endpoint(db=Depends(get_db)):
    return await list_users(db)


@router.get("/{user_id}", response_model=UserOut)
async def get_user_endpoint(user_id: str, db=Depends(get_db)):
    user = await get_user(db, parse_user_id(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserOut)
async def update_user_endpoint(user_id: str, changes: UserUpdate, db=Depends(get_db)):
    user = await update_user(
        db,
        parse_user_id(user_id),
        changes.model_dump(exclude_unset=True, exclude_none=True),
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(user_id: str, db=Depends(get_db)):
    deleted = await delete_user(db, parse_user_id(user_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
