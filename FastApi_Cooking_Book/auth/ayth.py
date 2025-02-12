from os import getenv
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


#Transport - cookie
cookie_transport = CookieTransport(cookie_name='recipe_user', cookie_max_age=3600)


#Strategy - JWT
SECRET = getenv('SECRET_JWS')

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)