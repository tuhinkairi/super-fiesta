from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    hash_pass: str = Field(min_length=1)
    role: Literal["User", "Admin"] = "User"


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = None
    role: Literal["User", "Admin"] | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    name: str
    email: str | None = None
    role: Literal["User", "Admin"]
    created_at: datetime
    updated_at: datetime | None = None
