from mysql.connector.errors import IntegrityError

import base64
import hashlib
import mysql.connector
import os

from ..exceptions.user_exists_exception import UserAlreadyExistsException
from ..config import settings

users_db = mysql.connector.connect(
    host=settings.DB_HOST,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    database=settings.DB_NAME
)

CREATE_USER_STATEMENT = "INSERT INTO users (username, password) VALUES (%s, %s)"
GET_USER_PASSWORD_HASH = "SELECT password FROM users WHERE username = %s"


def create_user(username: str, password: str):
    try:
        salt = os.urandom(16)
        hashed_password = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        encoded_password = base64.b64encode(hashed_password + salt).decode("utf-8")
        with users_db.cursor() as cursor:
            cursor.execute(CREATE_USER_STATEMENT, (username, encoded_password))
        users_db.commit()
    except IntegrityError as e:
        raise UserAlreadyExistsException("User already exists")


def check_password(username: str, password: str) -> bool:
    with users_db.cursor() as cursor:
        cursor.execute(GET_USER_PASSWORD_HASH, (username,))
        result = cursor.fetchone()
    if result:
        encoded_password = result[0]
        combined = base64.b64decode(encoded_password)
        stored_hashed_password = combined[:32]
        stored_salt = combined[32:]
        hashed_password = hashlib.pbkdf2_hmac("sha256", password.encode(), stored_salt, 100000)
        return stored_hashed_password == hashed_password
    return False
