import os

from src.config import Settings


def test_settings_db_host():
    os.environ["DB_HOST"] = "localhost"
    settings = Settings()
    assert settings.DB_HOST == "localhost"

def test_settings_db_port():
    os.environ["DB_PORT"] = "3306"
    settings = Settings()
    assert settings.DB_PORT == 3306

def test_settings_db_user():
    os.environ["DB_USER"] = "test_user"
    settings = Settings()
    assert settings.DB_USER == "test_user"

def test_settings_db_password():
    os.environ["DB_PASSWORD"] = "test_password"
    settings = Settings()
    assert settings.DB_PASSWORD == "test_password"

def test_settings_db_name():
    os.environ["DB_NAME"] = "test_db"
    settings = Settings()
    assert settings.DB_NAME == "test_db"

def test_settings_jwt_secret():
    os.environ["JWT_SECRET"] = "super_secret_key"
    settings = Settings()
    assert settings.JWT_SECRET_KEY == "super_secret_key"