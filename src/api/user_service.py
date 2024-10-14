from flask_jwt_extended import create_access_token

from ..db import users as UsersDB
from ..exceptions.auth_exception import AuthException

class UserService:
    def __init__(self, users_db: UsersDB):
        self.users_db = users_db

    def register_user(self, username: str, password: str) -> str:
        """
        Registers a new user with the given username and password.
        @param username: The username of the new user.
        @param password: The password of the new user.
        @return: An access token for the new user.
        """
        user = self.users_db.create_user(username, password)
        return create_access_token(
            identity={
                "username": user.username,
                "user_id": user.user_id,
            }
        )

    def login(self, username: str, password: str) -> str:
        """
        Logs in the user with the given username and password.
        @param username: The username of the user.
        @param password: The password of the user.
        @raises AuthException: If the username or password is invalid.
        @return: An access token for the user.
        """
        user = self.users_db.check_password(username, password)
        return create_access_token(
            identity={
                "username": user.username,
                "user_id": user.user_id,
            }
        )

    def get_user_id_from_token(self, token) -> int:
        """
        Gets the user ID from the given access token.
        @param token: The access token.
        @return: The user ID.
        """
        if not token or "user_id" not in token or "username" not in token:
            raise AuthException("Invalid JWT identity")
        return token["user_id"]

user_service = UserService(UsersDB)