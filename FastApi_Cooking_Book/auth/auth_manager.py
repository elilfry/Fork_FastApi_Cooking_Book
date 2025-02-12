from os import getenv

from fastapi_users.jwt import decode_jwt

from .auth_models import User, get_user_db
import jwt
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())



SECRET = getenv('SECRET_MANAGE')


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.email} has registered.")



async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)