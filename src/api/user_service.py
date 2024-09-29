from flask_jwt_extended import create_access_token

from ..db.users import check_password, create_user
from ..exceptions.auth_exception import AuthException


def register_user(username: str, password: str) -> str:
    """
    Registers a new user with the given username and password.
    @param username: The username of the new user.
    @param password: The password of the new user.
    @return: An access token for the new user.
    """
    user = create_user(username, password)
    return create_access_token(identity={
        "username": user.username,
        "user_id": user.user_id,
    })


def login(username: str, password: str) -> str:
    """
    Logs in the user with the given username and password.
    @param username: The username of the user.
    @param password: The password of the user.
    @raises AuthException: If the username or password is invalid.
    @return: An access token for the user.
    """
    user = check_password(username, password)
    return create_access_token(identity={
        "username": user.username,
        "user_id": user.user_id,
    })


def get_user_id_from_token(token) -> int:
    """
    Gets the user ID from the given access token.
    @param token: The access token.
    @return: The user ID.
    """
    if not token or "user_id" not in token or "username" not in token:
        raise AuthException("Invalid JWT identity")
    return token["user_id"]
