import pytest
from unittest.mock import Mock, patch
from flask import json
from flask_jwt_extended import create_access_token
from src.app import create_app
from src.config import Settings
from src.api.user_service import UserService
from src.api.note_service import NoteService
from src.exceptions.auth_exception import AuthException


@pytest.fixture
def app():
    settings = Mock(spec=Settings)
    settings.JWT_SECRET_KEY = "test_secret_key"
    user_service = Mock(spec=UserService)
    note_service = Mock(spec=NoteService)
    app = create_app(user_service, note_service, settings)
    app.config["TESTING"] = True
    app.config["DEBUG"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@patch("src.config.settings")
@patch("src.api.note_service.note_service")
@patch("src.api.user_service.user_service")
def test_create_app(mock_user_service, mock_note_service, mock_settings):
    jwt_secret = "123abc"
    mock_settings.JWT_SECRET_KEY = jwt_secret

    app = create_app(mock_user_service, mock_note_service, mock_settings)

    assert app.user_service == mock_user_service
    assert app.note_service == mock_note_service
    assert app.config["JWT_SECRET_KEY"] == jwt_secret


def test_register_user_success(client, app):
    with app.app_context():
        with patch.object(
            client.application.user_service, "register_user", return_value="test_token"
        ):

            response = client.post(
                "/v1/register_user",
                json={"username": "testuser", "password": "testpass"},
            )
            assert response.status_code == 200
            assert "access_token" in json.loads(response.data)


def test_register_user_missing_data(client):
    response = client.post("/v1/register_user", json={})
    assert response.status_code == 400
    assert b"Missing username or password" in response.data


def test_login_success(client):
    with patch.object(
        client.application.user_service, "login", return_value="test_token"
    ):
        response = client.post(
            "/v1/login", json={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 200
        assert "access_token" in json.loads(response.data)


def test_login_invalid_credentials(client):
    with patch.object(
        client.application.user_service,
        "login",
        side_effect=AuthException("test message"),
    ):
        response = client.post(
            "/v1/login", json={"username": "testuser", "password": "wrongpass"}
        )
        assert response.status_code == 401
        assert b"Invalid username or password" in response.data


@pytest.mark.parametrize(
    "route",
    [
        "/v1/protected",
        "/v1/notes",
        "/v1/notes/1",
    ],
)
def test_protected_routes_without_token(client, route):
    response = client.get(route)
    assert response.status_code == 401


def test_get_notes_success(client, app):
    with app.app_context():
        access_token = create_access_token(identity=1)
        mock_note = Mock()
        mock_note.to_dict.return_value = {
            "id": 1,
            "title": "Test Note",
            "text": "This is a test note",
        }
        with patch.object(
            client.application.user_service, "get_user_id_from_token", return_value=1
        ), patch.object(
            client.application.note_service, "get_notes", return_value=[mock_note]
        ):
            response = client.get(
                "/v1/notes", headers={"Authorization": f"Bearer {access_token}"}
            )
            assert response.status_code == 200
            assert len(json.loads(response.data)) == 1


def test_get_note_by_id_success(client, app):
    with app.app_context():
        access_token = create_access_token(identity=1)
        mock_note = Mock()
        mock_note.to_dict.return_value = {
            "id": 1,
            "title": "Test Note",
            "text": "This is a test note",
        }
        with patch.object(
            client.application.user_service, "get_user_id_from_token", return_value=1
        ), patch.object(
            client.application.note_service, "get_note_by_id", return_value=mock_note
        ):
            response = client.get(
                "/v1/notes/1", headers={"Authorization": f"Bearer {access_token}"}
            )
            assert response.status_code == 200
            assert json.loads(response.data)["id"] == 1


def test_get_note_by_id_not_found(client, app):
    with app.app_context():
        access_token = create_access_token(identity=1)
        with patch.object(
            client.application.user_service, "get_user_id_from_token", return_value=1
        ), patch.object(
            client.application.note_service, "get_note_by_id", return_value=None
        ):
            response = client.get(
                "/v1/notes/999", headers={"Authorization": f"Bearer {access_token}"}
            )
            assert response.status_code == 404


def test_create_note_success(client, app):
    with app.app_context():
        access_token = create_access_token(identity=1)
        mock_note = Mock()
        mock_note.to_dict.return_value = {
            "id": 1,
            "title": "New Note",
            "text": "This is a new note",
            "public": False,
        }
        with patch.object(
            client.application.user_service, "get_user_id_from_token", return_value=1
        ), patch.object(
            client.application.note_service, "create_note", return_value=mock_note
        ):
            response = client.post(
                "/v1/notes",
                json={
                    "title": "New Note",
                    "text": "This is a new note",
                    "public": False,
                },
                headers={"Authorization": f"Bearer {access_token}"},
            )
            assert response.status_code == 201
            assert json.loads(response.data)["title"] == "New Note"


def test_update_note_success(client, app):
    with app.app_context():
        access_token = create_access_token(identity=1)
        mock_note = Mock()
        mock_note.to_dict.return_value = {
            "id": 1,
            "title": "Updated Note",
            "text": "This note has been updated",
            "public": True,
        }
        with patch.object(
            client.application.user_service, "get_user_id_from_token", return_value=1
        ), patch.object(
            client.application.note_service, "update_note", return_value=mock_note
        ):
            response = client.put(
                "/v1/notes/1",
                json={
                    "title": "Updated Note",
                    "text": "This note has been updated",
                    "public": True,
                },
                headers={"Authorization": f"Bearer {access_token}"},
            )
            assert response.status_code == 200
            assert json.loads(response.data)["title"] == "Updated Note"


def test_delete_note_success(client, app):
    with app.app_context():
        access_token = create_access_token(identity=1)
        with patch.object(
            client.application.user_service, "get_user_id_from_token", return_value=1
        ), patch.object(
            client.application.note_service, "delete_note", return_value=True
        ):
            response = client.delete(
                "/v1/notes/1", headers={"Authorization": f"Bearer {access_token}"}
            )
            assert response.status_code == 200
            assert b"Successfully deleted note 1" in response.data


def test_delete_note_not_found(client, app):
    with app.app_context():
        access_token = create_access_token(identity=1)
        with patch.object(
            client.application.user_service, "get_user_id_from_token", return_value=1
        ), patch.object(
            client.application.note_service, "delete_note", return_value=None
        ):
            response = client.delete(
                "/v1/notes/999", headers={"Authorization": f"Bearer {access_token}"}
            )
            assert response.status_code == 404
