from sqlalchemy.exc import IntegrityError

import base64
import hashlib
import os

from ..db.database import get_db
from ..exceptions.auth_exception import AuthException
from ..exceptions.user_exists_exception import UserAlreadyExistsException
from ..models.user import User


def create_user(username: str, password: str) -> User:
    """
    Creates a new user with the given username and password.
    @param username: The username of the new user.
    @param password: The password of the new user.
    @return: The newly created user.
    @raises UserAlreadyExistsException: If a user with the given username already exists.
    """
    try:
        salt = os.urandom(16)
        hashed_password = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        encoded_password = base64.b64encode(hashed_password + salt).decode("utf-8")
        new_user = User(username=username, password=encoded_password)
        with get_db() as db:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
    except IntegrityError:
        raise UserAlreadyExistsException("User already exists")


def check_password(username: str, password: str) -> User:
    """
    Checks if the given password is correct for the user with the given username.
    @param username: The username of the user.
    @param password: The password to check.
    @return: The user if the password is correct.
    @raises AuthException: If the username or password is invalid
    """
    with get_db() as db:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise AuthException("Invalid username or password")

        combined = base64.b64decode(user.password)
        stored_hashed_password = combined[:32]
        stored_salt = combined[32:]
        hashed_password = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), stored_salt, 100000
        )
        if stored_hashed_password != hashed_password:
            raise AuthException("Invalid username or password")
        return user
