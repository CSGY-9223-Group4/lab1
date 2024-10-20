import pytest
import requests

BASE_URL = "http://localhost:8000/v1"


@pytest.mark.usefixtures("docker_compose")
def test_register_user(wait_for_server):
    """
    GIVEN a Flask application running in a Docker container
    WHEN the '/v1/register_user' endpoint is posted to (POST)
    THEN check that the response is valid
    """
    response = requests.post(
        f"{BASE_URL}/register_user",
        json={"username": "testuser", "password": "password123"},
        headers={"Content-Type": "application/json"},
    )
    data = response.json()
    assert response.status_code == 200
    assert "access_token" in data


@pytest.mark.usefixtures("docker_compose")
def test_register_user_missing_fields(wait_for_server):
    """
    GIVEN a Flask application running in a Docker container
    WHEN the '/v1/register_user' endpoint is posted to (POST) with missing fields
    THEN check that the response is a bad request
    """
    response = requests.post(
        f"{BASE_URL}/register_user",
        json={"username": "testuser"},
        headers={"Content-Type": "application/json"},
    )
    data = response.json()
    assert response.status_code == 400
    assert "error" in data


@pytest.mark.usefixtures("docker_compose")
def test_login(wait_for_server):
    """
    GIVEN a Flask application running in a Docker container
    WHEN the '/v1/login' endpoint is posted to (POST)
    THEN check that the response is valid
    """
    # First, register the user
    requests.post(
        f"{BASE_URL}/register_user",
        json={"username": "testuser", "password": "password123"},
        headers={"Content-Type": "application/json"},
    )

    # Then, login with the same user
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": "testuser", "password": "password123"},
        headers={"Content-Type": "application/json"},
    )
    data = response.json()
    assert response.status_code == 200
    assert "access_token" in data


@pytest.mark.usefixtures("docker_compose")
def test_login_invalid_credentials(wait_for_server):
    """
    GIVEN a Flask application running in a Docker container
    WHEN the '/v1/login' endpoint is posted to (POST) with invalid credentials
    THEN check that the response is unauthorized
    """
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": "testuser", "password": "wrongpassword"},
        headers={"Content-Type": "application/json"},
    )
    data = response.json()
    assert response.status_code == 401
    assert "error" in data
