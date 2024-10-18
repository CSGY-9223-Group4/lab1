from flask.testing import FlaskClient
import pytest
from unittest.mock import Mock, patch
from flask import json
from flask_jwt_extended import create_access_token
from src.app import create_app
from src.exceptions.auth_exception import AuthException
from src.exceptions.user_exists_exception import UserAlreadyExistsException


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


def test_register_user_success(client: FlaskClient, app):
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


def test_register_user_missing_data(client: FlaskClient):
    response = client.post("/v1/register_user", json={})
    assert response.status_code == 400
    assert b"Missing username or password" in response.data


def test_register_user_not_json(client: FlaskClient):
    response = client.post("/v1/register_user", data="not json")
    assert response.status_code == 415
    assert b"Unsupported media type" in response.data


def test_register_user_already_exists(client: FlaskClient):
    with patch.object(
        client.application.user_service,
        "register_user",
        side_effect=UserAlreadyExistsException("User already exists"),
    ):
        response = client.post(
            "/v1/register_user", json={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 409
        assert b"User already exists" in response.json["error"].encode()


def test_register_user_unknown_error(client: FlaskClient):
    with patch.object(
        client.application.user_service, "register_user", side_effect=Exception
    ):
        response = client.post(
            "/v1/register_user", json={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 500
        assert b"Internal Server Error" in response.data


def test_login_success(client: FlaskClient):
    with patch.object(
        client.application.user_service, "login", return_value="test_token"
    ):
        response = client.post(
            "/v1/login", json={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 200
        assert "access_token" in json.loads(response.data)


def test_login_missing_username(client: FlaskClient):
    response = client.post("/v1/login", json={"password": "testpass"})
    assert response.status_code == 400
    assert b"Missing username or password" in response.data


def test_login_missing_password(client: FlaskClient):
    response = client.post("/v1/login", json={"username": "testuser"})
    assert response.status_code == 400
    assert b"Missing username or password" in response.data


def test_login_not_json(client: FlaskClient):
    response = client.post("/v1/login", data="username=testuser&password=testpass")
    assert response.status_code == 415
    assert b"Unsupported media type" in response.data


def test_login_unknown_error(client: FlaskClient):
    with patch.object(
        client.application.user_service, "login", side_effect=Exception
    ):
        response = client.post(
            "/v1/login", json={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 500
        assert b"Internal Server Error" in response.data


def test_login_invalid_credentials(client: FlaskClient):
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
    "route,method",
    [
        ("/v1/protected",  FlaskClient.get),
        ("/v1/notes",      FlaskClient.get),
        ("/v1/notes/1",    FlaskClient.get),
        ("/v1/notes",      FlaskClient.post),
        ("/v1/notes/1",    FlaskClient.put),
        ("/v1/notes/1",    FlaskClient.delete),
    ],
)
def test_protected_routes_without_token(client: FlaskClient, route: str, method):
    response = method(client, route)
    assert response.status_code == 401


def test_protected(client: FlaskClient):
    access_token = create_access_token(identity=1)
    response = client.get("/v1/protected", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert json.loads(response.data)["logged_in_as"] == 1


def test_protected_unknown_error(client: FlaskClient):
    access_token = create_access_token(identity=1)
    with patch("src.app.get_jwt_identity", side_effect=Exception):
        response = client.get(
            "/v1/protected", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 500
        assert b"Internal Server Error" in response.data


def test_get_notes_success(client: FlaskClient, app):
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


def test_get_notes_invalid_page_size(client: FlaskClient):
    access_token = create_access_token(identity=1)
    response = client.get(
        "/v1/notes?page_size=0", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 400
    assert b"Invalid page or page_size" in response.data


def test_get_notes_invalid_max_page_size(client: FlaskClient):
    access_token = create_access_token(identity=1)
    response = client.get(
        "/v1/notes?page_size=1000", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 400
    assert b"Invalid page or page_size" in response.data


def test_get_notes_invalid_page(client: FlaskClient):
    access_token = create_access_token(identity=1)
    response = client.get(
        "/v1/notes?page=0", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 400
    assert b"Invalid page or page_size" in response.data


def test_get_notes_value_error(client: FlaskClient):
    access_token = create_access_token(identity=1)
    response = client.get(
        "/v1/notes?page=abc", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 400
    assert b"Invalid page or page_size" in response.data


def test_get_notes_unknown_error(client: FlaskClient):
    access_token = create_access_token(identity=1)
    with patch.object(
        client.application.user_service, "get_user_id_from_token", side_effect=Exception
    ):
        response = client.get(
            "/v1/notes", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 500
        assert b"Internal Server Error" in response.data


def test_get_note_by_id_success(client: FlaskClient, app):
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


def test_get_note_by_id_not_found(client: FlaskClient, app):
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


def test_get_note_by_id_invalid_id(client: FlaskClient):
    access_token = create_access_token(identity=1)
    response = client.get(
        "/v1/notes/abc", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 404


def test_get_note_by_id_unknown_error(client: FlaskClient):
    access_token = create_access_token(identity=1)
    with patch.object(
        client.application.user_service, "get_user_id_from_token", side_effect=Exception
    ):
        response = client.get(
            "/v1/notes/1", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 500
        assert b"Internal Server Error" in response.data


def test_create_note_success(client: FlaskClient, app):
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


def test_create_note_missing_text(client: FlaskClient):
    access_token = create_access_token(identity=1)
    response = client.post(
        "/v1/notes", json={"title": "New Note"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 400
    assert b"Missing note title or text" in response.data


def test_create_note_missing_title(client: FlaskClient):
    access_token = create_access_token(identity=1)
    response = client.post(
        "/v1/notes", json={"text": "This is a new note"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 400
    assert b"Missing note title or text" in response.data


def test_create_note_not_json(client: FlaskClient):
    access_token = create_access_token(identity=1)
    response = client.post("/v1/notes", data="not json",
                           headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 415
    assert b"Unsupported media type" in response.data


def test_create_note_unknown_error(client: FlaskClient):
    access_token = create_access_token(identity=1)
    with patch.object(
        client.application.user_service, "get_user_id_from_token", side_effect=Exception
    ):
        response = client.post(
            "/v1/notes",
            json={"title": "New Note", "text": "This is a new note"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 500
        assert b"Internal Server Error" in response.data


def test_update_note_success(client: FlaskClient, app):
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


def test_update_note_missing_text(client: FlaskClient):
    access_token = create_access_token(identity=1)
    response = client.put(
        "/v1/notes/1", json={"title": "Updated Note"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 400
    assert b"Missing note title or text" in response.data


def test_update_note_missing_title(client: FlaskClient):
    access_token = create_access_token(identity=1)
    response = client.put(
        "/v1/notes/1", json={"text": "This note has been updated"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 400
    assert b"Missing note title or text" in response.data


def test_update_note_not_json(client: FlaskClient):
    access_token = create_access_token(identity=1)
    response = client.put("/v1/notes/1", data="not json",
                          headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 415
    assert b"Unsupported media type" in response.data


def test_update_note_unknown_error(client: FlaskClient):
    access_token = create_access_token(identity=1)
    with patch.object(
        client.application.user_service, "get_user_id_from_token", side_effect=Exception
    ):
        response = client.put(
            "/v1/notes/1",
            json={"title": "Updated Note", "text": "This note has been updated"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 500
        assert b"Internal Server Error" in response.data


def test_delete_note_success(client: FlaskClient, app):
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


def test_delete_note_not_found(client: FlaskClient, app):
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


def test_delete_note_unknown_error(client: FlaskClient):
    access_token = create_access_token(identity=1)
    with patch.object(
        client.application.user_service, "get_user_id_from_token", side_effect=Exception
    ):
        response = client.delete(
            "/v1/notes/1", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 500
        assert b"Internal Server Error" in response.data
