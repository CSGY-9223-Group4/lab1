import base64
import os
import time
import pytest
import random
from string import ascii_letters

import requests
from testcontainers.compose import DockerCompose

SERVER_START_TIMEOUT_SEC = 30


def random_secret(length=10):
    """Generate a random string of a specified length."""
    return base64.b64encode(
        "".join(random.choices(ascii_letters, k=length)).encode()
    ).decode()


@pytest.fixture(scope="session")
def create_dot_env():
    """Create a .env file if it does not exist."""
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(f"JWT_SECRET={random_secret(32)}\n")
            f.write(f"DB_PASSWORD={random_secret(20)}\n")
            f.write(f"DB_ROOT_PASSWORD={random_secret(20)}\n")


@pytest.fixture(scope="session")
def docker_compose(create_dot_env):
    with DockerCompose(context=".", wait=False, env_file=".env") as compose:
        yield compose


@pytest.fixture(scope="session")
def server_url():
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def wait_for_server(docker_compose, server_url):
    """Waits for a web server to become available at the specified URL."""
    start_time = time.time()
    while True:
        try:
            requests.get(server_url)
            return True
        except requests.exceptions.ConnectionError:
            if time.time() - start_time > SERVER_START_TIMEOUT_SEC:
                return False
            time.sleep(1)
