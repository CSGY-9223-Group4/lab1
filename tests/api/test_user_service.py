import pytest
from unittest.mock import patch, MagicMock
from src.api.user_service import register_user, login, get_user_id_from_token
from src.exceptions.auth_exception import AuthException


@patch("src.api.user_service.create_user")
@patch("src.api.user_service.create_access_token")
def test_register_user(mock_create_access_token, mock_create_user):
    """
    GIVEN a username and password
    WHEN register_user is called
    THEN a new user is created and an access token is returned
    """
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.user_id = 1
    mock_create_user.return_value = mock_user
    mock_create_access_token.return_value = "access_token"

    username = "testuser"
    password = "password123"
    token = register_user(username, password)

    assert token == "access_token"
    mock_create_user.assert_called_once_with(username, password)
    mock_create_access_token.assert_called_once_with(
        identity={
            "username": mock_user.username,
            "user_id": mock_user.user_id,
        }
    )


@patch("src.api.user_service.check_password")
@patch("src.api.user_service.create_access_token")
def test_login_success(mock_create_access_token, mock_check_password):
    """
    GIVEN a username and password
    WHEN login is called with valid credentials
    THEN an access token is returned
    """
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.user_id = 1
    mock_check_password.return_value = mock_user
    mock_create_access_token.return_value = "access_token"

    username = "testuser"
    password = "password123"
    token = login(username, password)

    assert token == "access_token"
    mock_check_password.assert_called_once_with(username, password)
    mock_create_access_token.assert_called_once_with(
        identity={
            "username": mock_user.username,
            "user_id": mock_user.user_id,
        }
    )


@patch("src.api.user_service.check_password")
def test_login_invalid_credentials(mock_check_password):
    """
    GIVEN a username and password
    WHEN login is called with invalid credentials
    THEN an AuthException is raised
    """
    mock_check_password.side_effect = AuthException("Invalid credentials")

    username = "testuser"
    password = "wrongpassword"

    with pytest.raises(AuthException):
        login(username, password)

    mock_check_password.assert_called_once_with(username, password)


def test_get_user_id_from_token_success():
    """
    GIVEN a valid access token
    WHEN get_user_id_from_token is called
    THEN the user ID is returned
    """
    token = {
        "username": "testuser",
        "user_id": 1,
    }
    user_id = get_user_id_from_token(token)
    assert user_id == 1


def test_get_user_id_from_token_invalid_token():
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
            get_user_id_from_token(token)
