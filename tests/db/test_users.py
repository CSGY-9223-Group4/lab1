import base64
import hashlib
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError
from src.models.user import User
from src.exceptions.auth_exception import AuthException
from src.exceptions.user_exists_exception import UserAlreadyExistsException
from src.db.users import create_user, check_password


@patch("src.db.users.get_db")
def test_create_user_success(mock_get_db):
    """
    GIVEN a username and password
    WHEN create_user is called
    THEN a new user is created and returned
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    username = "testuser"
    password = "password123"
    new_user = create_user(username, password)

    assert new_user.username == username
    assert new_user.password is not None
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(new_user)


@patch("src.db.users.get_db")
def test_create_user_already_exists(mock_get_db):
    """
    GIVEN a username that already exists
    WHEN create_user is called
    THEN a UserAlreadyExistsException is raised
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db
    mock_db.add.side_effect = IntegrityError(None, None, None)

    with pytest.raises(UserAlreadyExistsException):
        create_user("existinguser", "password123")


@patch("src.db.users.get_db")
def test_check_password_success(mock_get_db):
    """
    GIVEN a username and correct password
    WHEN check_password is called
    THEN the user is returned
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    username = "testuser"
    password = "password123"
    salt = b"some_salt"
    hashed_password = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    encoded_password = base64.b64encode(hashed_password + salt).decode("utf-8")
    user = User(username=username, password=encoded_password)
    mock_db.query.return_value.filter.return_value.first.return_value = user

    returned_user = check_password(username, password)

    assert returned_user == user


@patch("src.db.users.get_db")
def test_check_password_invalid_username(mock_get_db):
    """
    GIVEN an invalid username
    WHEN check_password is called
    THEN an AuthException is raised
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(AuthException):
        check_password("invaliduser", "password123")


@patch("src.db.users.get_db")
def test_check_password_invalid_password(mock_get_db):
    """
    GIVEN a username and incorrect password
    WHEN check_password is called
    THEN an AuthException is raised
    """
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    username = "testuser"
    correct_password = "password123"
    incorrect_password = "wrongpassword"
    salt = b"some_salt"
    hashed_password = hashlib.pbkdf2_hmac(
        "sha256", correct_password.encode(), salt, 100000
    )
    encoded_password = base64.b64encode(hashed_password + salt).decode("utf-8")
    user = User(username=username, password=encoded_password)
    mock_db.query.return_value.filter.return_value.first.return_value = user

    with pytest.raises(AuthException):
        check_password(username, incorrect_password)
