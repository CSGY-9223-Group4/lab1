import base64
import os
import pytest
import random
import requests
import time
from string import ascii_letters
from testcontainers.compose import DockerCompose


def random_secret(length=10):
    """Generate a random string of a specified length."""
    return base64.encode("".join(random.choices(ascii_letters, k=length)))


def wait_for_server(url, timeout=30):
    """Waits for a web server to become available at the specified URL."""
    start_time = time.time()
    while True:
        try:
            requests.get(url)
            return True
        except requests.exceptions.ConnectionError:
            if time.time() - start_time > timeout:
                return False
            time.sleep(1)


def create_dot_env():
    """Create a .env file if it does not exist."""
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(f"JWT_SECRET={random_secret(32)}\n")
            f.write(f"DB_PASSWORD={random_secret(20)}\n")
            f.write(f"DB_ROOT_PASSWORD={random_secret(20)}\n")


@pytest.fixture(scope="session")
def docker_compose():
    create_dot_env()
    with DockerCompose(context=".", wait=False, env_file=".env") as compose:
        wait_for_server("http://localhost:8000", timeout=120)
        yield compose
