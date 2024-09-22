from flask_jwt_extended import create_access_token

from ..db.users import check_password, create_user
from ..exceptions.auth_exception import AuthException


def register_user(username: str, password: str) -> str:
    create_user(username, password)
    return create_access_token(identity=username)


def login(username: str, password: str) -> str:
    if not check_password(username, password):
        raise AuthException("Invalid username or password")
    return create_access_token(identity=username)
