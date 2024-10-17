import pytest
from unittest.mock import patch, MagicMock
from src.api.user_service import UserService
from src.db import users
from src.exceptions.auth_exception import AuthException


@pytest.fixture
def mock_user_db():
    return MagicMock(spec=users)


@pytest.fixture
def user_service(mock_user_db):
    return UserService(mock_user_db)


@patch("src.api.user_service.create_access_token")
def test_register_user(mock_create_access_token, user_service, mock_user_db):
    """
    GIVEN a username and password
    WHEN register_user is called
    THEN a new user is created and an access token is returned
    """
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.user_id = 1
    mock_user_db.create_user.return_value = mock_user
    mock_create_access_token.return_value = "access_token"

    username = "testuser"
    password = "password123"
    token = user_service.register_user(username, password)

    assert token == "access_token"
    mock_user_db.create_user.assert_called_once_with(username, password)
    mock_create_access_token.assert_called_once_with(
        identity={
            "username": mock_user.username,
            "user_id": mock_user.user_id,
        }
    )


@patch("src.api.user_service.create_access_token")
def test_login_success(mock_create_access_token, user_service, mock_user_db):
    """
    GIVEN a username and password
    WHEN login is called with valid credentials
    THEN an access token is returned
    """
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.user_id = 1
    mock_user_db.check_password.return_value = mock_user
    mock_create_access_token.return_value = "access_token"

    username = "testuser"
    password = "password123"
    token = user_service.login(username, password)

    assert token == "access_token"
    mock_user_db.check_password.assert_called_once_with(username, password)
    mock_create_access_token.assert_called_once_with(
        identity={
            "username": mock_user.username,
            "user_id": mock_user.user_id,
        }
    )


def test_login_invalid_credentials(user_service, mock_user_db):
    """
    GIVEN a username and password
    WHEN login is called with invalid credentials
    THEN an AuthException is raised
    """
    mock_user_db.check_password.side_effect = AuthException("Invalid credentials")

    username = "testuser"
    password = "wrongpassword"

    with pytest.raises(AuthException):
        user_service.login(username, password)

    mock_user_db.check_password.assert_called_once_with(username, password)


def test_get_user_id_from_token_success(user_service):
    """
    GIVEN a valid access token
    WHEN get_user_id_from_token is called
    THEN the user ID is returned
    """
    token = {
        "username": "testuser",
        "user_id": 1,
    }
    user_id = user_service.get_user_id_from_token(token)
    assert user_id == 1


def test_get_user_id_from_token_invalid_token(user_service):
    """
    GIVEN an invalid access token
    WHEN get_user_id_from_token is called
    THEN an AuthException is raised
    """
    invalid_tokens = [
        None,
        {},
        {"username": "testuser"},
        {"user_id": 1},
    ]

    for token in invalid_tokens:
        with pytest.raises(AuthException):
            user_service.get_user_id_from_token(token)
