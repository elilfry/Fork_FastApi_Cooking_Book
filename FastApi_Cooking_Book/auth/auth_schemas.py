from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr
from pydantic import BaseModel



class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    # is_active: bool = True
    # is_superuser: bool = False
    # is_verified: bool = False

    class Config:
        orm_mode = True


class UserCreate(schemas.CreateUpdateDictModel):
    email: EmailStr
    password: str

